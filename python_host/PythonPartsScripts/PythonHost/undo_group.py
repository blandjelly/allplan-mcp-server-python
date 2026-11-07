"""One UI Undo step for every setter of one typed model-edit Apply (0.51.0).

Owner requirement (0.50.1 trial, 2026-11-07): one Apply that changes several
values must be undone by one UI Undo. The paired write on the Wall with a door
ran two setters (native ModifyElements, then attribute ChangeAttributes) and
needed two UI Undo steps; the first restored only the attribute.

SDK 2026 (NemAll_Python_IFW_Input.UndoRedoService): the constructor
``UndoRedoService(doc, isPassivateAll, isLockPreviewDraw,
collectEleForMultipleTransactions)`` collects the elements of several
transactions and ``CreateUndoStep()`` closes them as one undo step. The
official examples SlopedSlabOpening, GeneralOpeningsFor3DSolids and
SlabOpeningsFor3DSolids (PythonPartsExamples at 8e2c252) open it with
``(doc, True, True, True)`` before several transactions and call
``CreateUndoStep()`` once afterwards. Whether ModifyElements and
ChangeAttributes join that step is a native-trial question; this module only
opens and closes the service and reports what happened. It never undoes,
retries or skips a setter, and a failure here never changes a setter outcome.
"""
from __future__ import annotations

API = "NemAll_Python_IFW_Input.UndoRedoService"
FLAGS = {"isPassivateAll": True, "isLockPreviewDraw": True, "collectEleForMultipleTransactions": True}


def _in_undo_service(service_type):
    try:
        value = service_type.IsInUndoService()
        return value if type(value) is bool else None
    except Exception:
        return None


class UndoGroup:
    """Open the service lazily before the first setter; close it exactly once."""

    def __init__(self, doc, planned_changes):
        self.doc = doc
        self.service = None
        self.service_type = None
        self.requested = planned_changes >= 2
        self.report = ({"status": "not_started", "api": API, "flags": dict(FLAGS), "setters_in_step": 0}
                       if self.requested else
                       {"status": "not_requested", "reason": "single_change_plan"})

    def before_setter(self):
        """Call right before each setter; opens the step for the first one."""
        if not self.requested or self.report["status"] in {"unavailable", "created", "close_failed"}:
            return
        if self.service is None:
            try:
                import NemAll_Python_IFW_Input as ifw
                self.service_type = ifw.UndoRedoService
                self.report["in_undo_service_before_open"] = _in_undo_service(self.service_type)
                self.service = self.service_type(self.doc, FLAGS["isPassivateAll"], FLAGS["isLockPreviewDraw"],
                                                 FLAGS["collectEleForMultipleTransactions"])
                self.report["status"] = "open"
                self.report["in_undo_service_after_open"] = _in_undo_service(self.service_type)
            except Exception as exc:
                # Setters still run (each may then be its own UI Undo step);
                # the report says so instead of claiming one step.
                self.service = None
                self.report.update(status="unavailable", error_type=type(exc).__name__,
                                   effect="each setter may be a separate UI Undo step")
                return
        self.report["setters_in_step"] += 1

    def close(self):
        """CreateUndoStep once after the last setter (also after a stop)."""
        if self.service is None:
            return self.report
        service, self.service = self.service, None
        try:
            service.CreateUndoStep()
            self.report["status"] = "created"
        except Exception as exc:
            self.report.update(status="close_failed", error_type=type(exc).__name__)
        finally:
            # Release the native service before asking whether one is active.
            del service
        self.report["in_undo_service_after_close"] = _in_undo_service(self.service_type)
        self.report["native_acceptance"] = "not_run: count the UI Undo steps in the owner trial"
        return self.report
