# 0.12.0 mark assignment and numbering evaluation

Status: **ready_for_owner_test**. Native mark/numbering acceptance is pending;
M3/UAT-05/UAT-06 remain open. The new implementation replaces existing string
mark attributes through the shared reviewed executor and introduces versioned
native-model-qa-demo-mark-numbering 1.0.0. Valid marks remain; missing marks and
surplus duplicates receive free S numbers in canonical center Y/X/Z/UUID order.
Full-scope collisions/source checks include excluded peers.

Source: **fd78700378eceb6f217e4ca30a83b88004b73a57**, source_modified=false.
The delivered ZIP is **260989 bytes**, SHA-256:

```text
afab9c1dfa427d312576918ca5407520d10b0928e0a3ba92c8044bd396c02891
```

[Windows evaluation ZIP](allplan-mcp-0.12.0-windows-evaluation.zip),
[checksum](allplan-mcp-0.12.0-windows-evaluation.zip.sha256),
[wheel](allplan_mcp_server-0.12.0-py3-none-any.whl),
[sdist](allplan_mcp_server-0.12.0.tar.gz),
[exact delivery record](delivery-0.12.0.json).
Archives are built once from this source and preserved through publication.
The portable package test separately exercises deterministic ZIPs.

Local verification: one full **187-test PASS** on Linux CPython 3.12.14 after
focused repair/mark and HTTP checks; frozen sync, wheel/sdist build and exact
extracted package integrity PASS. All **23** installed bridge hashes match;
Setup/Restore preserves the journal and restores the prior bridge in the fixture.
Source CI **6/6 PASS**: [run 38075847420](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38075847420),
Windows/Ubuntu Python 3.11–3.13; final observations are retained in
source-ci-0.12.0.json and delivery-0.12.0.json. Portable checks do not run Allplan.

Owner instructions are standalone [Markdown](TEST-ALLPLAN-0.12.0.md) and
[text](TEST-ALLPLAN-0.12.0.txt), also inside the package's docs directory.
Install through Setup.cmd, start the host/MCP and run **M3 Numbering.cmd**.
Review C03→S03/C04→S04, then enter **NUMERUJ KOPIE** to authorize that exact plan.
The launcher reads actual marks first; it does not assume the prior layer/status
Undo state. Current layer/status defects remain untouched.

After UI/Undo observation use **M3 Numbering Recover.cmd**. Lost/partial outcomes
require Recover only; never restart the write launcher to repeat an uncertain
write. Preserve the Local journal and original project copy. The package contains
no Allplan/Python/Codex runtime; existing external-Python dependency setup remains.
Previous 0.11.0 delivered archives/evidence are unchanged. No main merge or release.
