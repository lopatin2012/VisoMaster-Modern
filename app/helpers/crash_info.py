"""Capture the faulting module of native access violations on Windows.

Python's ``faulthandler`` reports that a crash happened but cannot unwind C++
frames, so the faulting module is unknown. This installs a vectored exception
handler (VEH) that, on an access violation, resolves the faulting instruction
address to the owning DLL and appends ``address / access type / module`` to
``faulthandler.log`` (and stderr) before letting the default handler continue.

No-op on non-Windows platforms.
"""

import ctypes
import os
from ctypes import wintypes

EXCEPTION_ACCESS_VIOLATION = 0xC0000005
_LOG_FILE = "faulthandler.log"
_ARRAY_INDEX_ACCESS_TYPE = 0  # 0=read, 1=write, 8=execute
_ARRAY_INDEX_ACCESS_ADDR = 1

_GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS = 0x00000004
_GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT = 0x00000001


class _EXCEPTION_RECORD(ctypes.Structure):
    _fields_ = [
        ("ExceptionCode", wintypes.DWORD),
        ("ExceptionFlags", wintypes.DWORD),
        ("ExceptionRecord", ctypes.c_void_p),
        ("ExceptionAddress", ctypes.c_void_p),
        ("NumberParameters", wintypes.DWORD),
        ("ExceptionInformation", ctypes.c_size_t * 15),
    ]


class _EXCEPTION_POINTERS(ctypes.Structure):
    _fields_ = [
        ("ExceptionRecord", ctypes.POINTER(_EXCEPTION_RECORD)),
        ("ContextRecord", ctypes.c_void_p),
    ]


_VEH = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.POINTER(_EXCEPTION_POINTERS))
_handler_ref = None  # keep the callback alive


def _module_for_address(address: int) -> str:
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.GetModuleHandleExW.restype = wintypes.BOOL
        kernel32.GetModuleHandleExW.argtypes = [
            wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(wintypes.HMODULE)
        ]
        module = wintypes.HMODULE()
        flags = (
            _GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS
            | _GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT
        )
        if kernel32.GetModuleHandleExW(flags, ctypes.c_void_p(address), ctypes.byref(module)):
            buffer = ctypes.create_unicode_buffer(1024)
            if kernel32.GetModuleFileNameW(module, buffer, 1024):
                return buffer.value
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    return "<unknown>"


def _write(message: str) -> None:
    data = (message + "\n").encode("utf-8", "replace")
    try:
        os.write(2, data)  # stderr
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    try:
        with open(_LOG_FILE, "ab", buffering=0) as handle:
            handle.write(data)
    except Exception:  # pylint: disable=broad-exception-caught
        pass


def _vectored_handler(pointers):
    try:
        record = pointers.contents.ExceptionRecord.contents
        if record.ExceptionCode == EXCEPTION_ACCESS_VIOLATION:
            address = record.ExceptionAddress or 0
            access_type = record.ExceptionInformation[_ARRAY_INDEX_ACCESS_TYPE]
            accessed = record.ExceptionInformation[_ARRAY_INDEX_ACCESS_ADDR]
            kind = {0: "read", 1: "write", 8: "execute"}.get(access_type, str(access_type))
            _write(
                "[crash_info] ACCESS_VIOLATION "
                f"at 0x{address:016x} module={_module_for_address(address)} "
                f"access={kind} address=0x{accessed:016x}"
            )
    except Exception:  # pylint: disable=broad-exception-caught
        pass
    return 0  # EXCEPTION_CONTINUE_SEARCH: let faulthandler/default handling run


def install_crash_handler() -> None:
    """Install the vectored handler once (Windows only)."""
    global _handler_ref
    if os.name != "nt" or _handler_ref is not None:
        return
    try:
        _handler_ref = _VEH(_vectored_handler)
        ctypes.windll.kernel32.AddVectoredExceptionHandler(1, _handler_ref)
    except Exception:  # pylint: disable=broad-exception-caught
        _handler_ref = None
