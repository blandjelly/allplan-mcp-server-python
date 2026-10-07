"""Read-only runtime diagnostics, with explicit unavailable build information."""
from __future__ import annotations

import ctypes
import json
import hashlib
import platform
import sys
from pathlib import Path


def executable_versions() -> dict:
    result = {"status": "not_checked", "file_version": None, "product_version": None}
    if sys.platform != "win32":
        return result
    try:
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        versions = ctypes.WinDLL("version", use_last_error=True)
        kernel.GetModuleFileNameW.argtypes = [wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
        kernel.GetModuleFileNameW.restype = wintypes.DWORD
        versions.GetFileVersionInfoSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
        versions.GetFileVersionInfoSizeW.restype = wintypes.DWORD
        versions.GetFileVersionInfoW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
        versions.GetFileVersionInfoW.restype = wintypes.BOOL
        versions.VerQueryValueW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.UINT)]
        versions.VerQueryValueW.restype = wintypes.BOOL
        buffer = ctypes.create_unicode_buffer(32768)
        if not kernel.GetModuleFileNameW(None, buffer, len(buffer)):
            return result
        size = versions.GetFileVersionInfoSizeW(buffer.value, None)
        if not size:
            return result
        data = ctypes.create_string_buffer(size)
        if not versions.GetFileVersionInfoW(buffer.value, 0, size, data):
            return result
        pointer, length = ctypes.c_void_p(), ctypes.c_uint()
        if not versions.VerQueryValueW(data, "\\", ctypes.byref(pointer), ctypes.byref(length)):
            return result
        if length.value < 52:
            return result
        words = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_uint32))
        if words[0] != 0xFEEF04BD:
            return result
        def version(ms, ls):
            return f"{ms >> 16}.{ms & 65535}.{ls >> 16}.{ls & 65535}"
        return {"status": "observed", "file_version": version(words[2], words[3]),
                "product_version": version(words[4], words[5]), "source": "running_process_executable"}
    except (OSError, AttributeError, ValueError):
        return result


def runtime_info(version_api) -> dict:
    release = {}
    for name in ("Version", "MainReleaseName", "SubReleaseName", "WindowsReleaseName"):
        try:
            value = getattr(version_api, name)()
            release[name] = str(value) if value is not None else None
        except Exception:
            release[name] = None
    try:
        package = json.loads(Path(__file__).with_name("package_info.json").read_text(encoding="utf-8"))
        if not isinstance(package, dict):
            raise ValueError("Package metadata must be an object")
    except (OSError, ValueError):
        package = {"version": None, "integrity": "not_checked"}
    installed = {"status": "not_checked"}
    if isinstance(package.get("bridge_files"), dict) and package["bridge_files"]:
        local = Path(__file__).resolve().parents[2]
        mismatches = []
        for name, expected in package["bridge_files"].items():
            path = local / name
            try:
                if not path.resolve().is_relative_to(local) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                    mismatches.append(name)
            except OSError:
                mismatches.append(name)
        installed = {"status": "verified" if not mismatches else "mismatch", "mismatches": mismatches}
    return {"version": release["Version"], "allplan_release": release,
            "executable_versions": executable_versions(),
            "hotfix": {"status": "not_checked", "value": None},
            "embedded_python": {"version": platform.python_version(), "implementation": platform.python_implementation()},
            "bridge_package": package,
            "installed_bridge_integrity": installed,
            "compatibility": {"target_major": "2026", "major_matches": release["MainReleaseName"] == "2026", "runtime_verified": False}}
