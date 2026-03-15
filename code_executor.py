"""
Sandbox Python code executor for V16 code_gen scenarios.

Runs generated code in an isolated subprocess with:
- Matplotlib Agg backend injected automatically
- 20s hard timeout
- Basic pattern-based safety filter
- Output file capture (PNG, CSV, etc.)
"""
import os
import re
import subprocess
import sys
import tempfile

# Inject before any user code to prevent GUI window creation
_MATPLOTLIB_HEADER = "import matplotlib\nmatplotlib.use('Agg')\n"

# Patterns that indicate clearly dangerous intent — block execution
_BLOCKED_PATTERNS = [
    r"\bimport\s+subprocess\b",
    r"\bimport\s+socket\b",
    r"\bimport\s+requests\b",
    r"\bimport\s+urllib\b",
    r"\b__import__\s*\(",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bos\.system\b",
    r"\bos\.popen\b",
    r"\bos\.remove\b",
    r"\bshutil\.rmtree\b",
]


def _safety_check(code: str) -> tuple[bool, str]:
    for pat in _BLOCKED_PATTERNS:
        if re.search(pat, code):
            return False, f"Blocked pattern detected: {pat}"
    return True, ""


def exec_code(code: str, timeout: int = 20) -> dict:
    """
    Execute Python code in a temporary subprocess.

    Returns dict:
        stdout      str   — captured standard output
        stderr      str   — captured standard error
        returncode  int   — process exit code (0 = success)
        files       list  — filenames written in the working dir
        file_contents dict — {filename: bytes} for files ≤ 5 MB
        success     bool  — returncode == 0
        timed_out   bool
    """
    safe, reason = _safety_check(code)
    if not safe:
        return {
            "stdout": "", "stderr": f"BLOCKED: {reason}",
            "returncode": -2, "files": [], "file_contents": {},
            "success": False, "timed_out": False,
        }

    # Prepend Agg backend when matplotlib is used
    if re.search(r"\b(matplotlib|plt|seaborn|sns)\b", code):
        full_code = _MATPLOTLIB_HEADER + code
    else:
        full_code = code

    with tempfile.TemporaryDirectory() as tmpdir:
        script = os.path.join(tmpdir, "solution.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(full_code)

        try:
            proc = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
                env={**os.environ, "MPLBACKEND": "Agg"},
            )
            files = [fn for fn in os.listdir(tmpdir) if fn != "solution.py"]
            file_contents: dict[str, bytes] = {}
            for fn in files:
                path = os.path.join(tmpdir, fn)
                if os.path.getsize(path) <= 5_000_000:
                    try:
                        with open(path, "rb") as fh:
                            file_contents[fn] = fh.read()
                    except OSError:
                        pass
            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "files": files,
                "file_contents": file_contents,
                "success": proc.returncode == 0,
                "timed_out": False,
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "", "stderr": "TimeoutExpired",
                "returncode": -1, "files": [], "file_contents": {},
                "success": False, "timed_out": True,
            }
        except Exception as exc:
            return {
                "stdout": "", "stderr": str(exc),
                "returncode": -3, "files": [], "file_contents": {},
                "success": False, "timed_out": False,
            }


# ── Partial scoring helper ─────────────────────────────────────

def code_partial_score(
    exec_result: dict,
    core_check: "callable | None" = None,
    spec_checks: "list[callable] | None" = None,
) -> tuple[float, dict]:
    """
    20 pts — no SyntaxError / IndentationError
    30 pts — executes without RuntimeError (returncode == 0)
    30 pts — core_check passes (primary output validation)
    20 pts — all spec_checks pass (full spec compliance)

    Returns (score 0-100, breakdown dict)
    """
    spec_checks = spec_checks or []
    breakdown: dict = {}
    score = 0.0
    stderr = exec_result.get("stderr", "")

    # 20 pts: syntax
    if "SyntaxError" not in stderr and "IndentationError" not in stderr:
        score += 20
        breakdown["syntax"] = True
    else:
        breakdown["syntax"] = False
        breakdown["syntax_error"] = stderr[:300]
        return score, breakdown

    # 30 pts: runtime
    if exec_result.get("success"):
        score += 30
        breakdown["runs"] = True
    else:
        breakdown["runs"] = False
        breakdown["runtime_error"] = stderr[:300]
        return score, breakdown

    # 30 pts: core check
    if core_check and core_check(exec_result):
        score += 30
        breakdown["core"] = True
    elif not core_check:
        score += 30
        breakdown["core"] = True
    else:
        breakdown["core"] = False

    # 20 pts: spec checks
    if spec_checks:
        all_ok = all(fn(exec_result) for fn in spec_checks)
        if all_ok:
            score += 20
            breakdown["full_spec"] = True
        else:
            breakdown["full_spec"] = False
    else:
        score += 20
        breakdown["full_spec"] = True

    return min(100.0, score), breakdown
