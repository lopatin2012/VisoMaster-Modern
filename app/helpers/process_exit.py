"""Immediate process termination helpers.

On Windows, tearing down the CUDA/TensorRT + Qt DLLs during normal interpreter
finalization can segfault. ``TerminateProcess`` ends the process without running
DLL detach handlers, which avoids that crash.
"""

import os


def hard_exit(code: int = 0) -> None:
    """Exit immediately with ``code``, skipping Python/C++ teardown."""
    if os.name == "nt":
        try:
            import ctypes

            ctypes.windll.kernel32.TerminateProcess(
                ctypes.windll.kernel32.GetCurrentProcess(), int(code) & 0xFFFFFFFF
            )
            return
        except Exception:  # pylint: disable=broad-exception-caught
            pass
    os._exit(code)
