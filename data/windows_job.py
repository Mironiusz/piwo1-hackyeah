"""Contain a Windows import tool tree without allowing breakaway writers."""

import ctypes
import subprocess
import sys
from ctypes import wintypes
from dataclasses import dataclass
from typing import Any

from data.import_workspace import ImportWorkspaceUnconfirmed

JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_QUERY = 4
CREATE_SUSPENDED = 4
CREATE_NO_WINDOW = 0x08000000
WAIT_OBJECT_0 = 0
ERROR_FILE_NOT_FOUND = 2


class BasicLimitInformation(ctypes.Structure):
    """Match the native process-limit layout used by a Windows Job Object."""

    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class IoCounters(ctypes.Structure):
    """Match the six native job IO accounting counters."""

    _fields_ = [(name, ctypes.c_ulonglong) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class ExtendedLimitInformation(ctypes.Structure):
    """Match the native job limit structure without enabling breakaway flags."""

    _fields_ = [
        ("BasicLimitInformation", BasicLimitInformation),
        ("IoInfo", IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class BasicAccountingInformation(ctypes.Structure):
    """Expose the native active-process count for completion evidence."""

    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


class StartupInformation(ctypes.Structure):
    """Match STARTUPINFOW for a child launched with no inherited handles."""

    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class ProcessInformation(ctypes.Structure):
    """Keep the suspended child's process and primary-thread handles."""

    _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD)]


def fetch_kernel_api() -> Any:
    """Bind Windows functions with pointer-safe signatures on Windows only."""
    if sys.platform != "win32":
        raise ImportWorkspaceUnconfirmed("Windows process jobs require Windows")
    kernel: Any = ctypes.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
        "OpenJobObjectW": ([wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE),
        "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
        "QueryInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p], wintypes.BOOL),
        "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
        "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        "ResumeThread": ([wintypes.HANDLE], wintypes.DWORD),
        "TerminateProcess": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
        "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
        "GetExitCodeProcess": ([wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
        "CreateProcessW": (
            [
                wintypes.LPCWSTR,
                wintypes.LPWSTR,
                ctypes.c_void_p,
                ctypes.c_void_p,
                wintypes.BOOL,
                wintypes.DWORD,
                ctypes.c_void_p,
                wintypes.LPCWSTR,
                ctypes.POINTER(StartupInformation),
                ctypes.POINTER(ProcessInformation),
            ],
            wintypes.BOOL,
        ),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(kernel, name)
        function.argtypes = arguments
        function.restype = result
    return kernel


def fetch_active_processes(kernel: Any, handle: int) -> int:
    """Read only the active-process count of the run-owned job."""
    accounting = BasicAccountingInformation()
    if not kernel.QueryInformationJobObject(handle, JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
        raise ImportWorkspaceUnconfirmed("Windows job completion is unconfirmed")
    return int(accounting.ActiveProcesses)


def fetch_job_completion(name: str) -> bool:
    """Confirm that a named recovery job has no remaining writer processes."""
    kernel = fetch_kernel_api()
    handle = kernel.OpenJobObjectW(JOB_OBJECT_QUERY, False, name)
    if not handle:
        native: Any = ctypes
        if native.get_last_error() == ERROR_FILE_NOT_FOUND:
            return True
        raise ImportWorkspaceUnconfirmed("Windows recovery job is inaccessible")
    try:
        return fetch_active_processes(kernel, handle) == 0
    finally:
        kernel.CloseHandle(handle)


@dataclass
class WindowsJob:
    """Own a non-breakaway named process tree for one import run."""

    name: str
    kernel: Any
    handle: int

    @classmethod
    def apply_creation(cls, name: str) -> "WindowsJob":
        """Create a kill-on-close job before permitting child execution."""
        kernel = fetch_kernel_api()
        handle = kernel.CreateJobObjectW(None, name)
        native: Any = ctypes
        if not handle:
            raise ImportWorkspaceUnconfirmed("Windows import job creation failed")
        if native.get_last_error() == 183:
            kernel.CloseHandle(handle)
            raise ImportWorkspaceUnconfirmed("Windows import job already exists")
        limits = ExtendedLimitInformation()
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(handle, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)):
            kernel.CloseHandle(handle)
            raise ImportWorkspaceUnconfirmed("Windows import job limits failed")
        return cls(name, kernel, handle)

    def apply_process_start(self, arguments: list[str], directory: str) -> int:
        """Assign a suspended child to containment before resuming execution."""
        startup = StartupInformation()
        startup.cb = ctypes.sizeof(startup)
        information = ProcessInformation()
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline(arguments))
        if not self.kernel.CreateProcessW(arguments[0], command, None, None, False, CREATE_SUSPENDED | CREATE_NO_WINDOW, None, directory, ctypes.byref(startup), ctypes.byref(information)):
            raise ImportWorkspaceUnconfirmed("Windows import process creation failed")
        try:
            if not self.kernel.AssignProcessToJobObject(self.handle, information.hProcess):
                raise ImportWorkspaceUnconfirmed("Windows import process assignment failed")
            if self.kernel.ResumeThread(information.hThread) == 0xFFFFFFFF:
                raise ImportWorkspaceUnconfirmed("Windows import process resume failed")
        except BaseException:
            self.kernel.TerminateProcess(information.hProcess, 1)
            self.kernel.WaitForSingleObject(information.hProcess, 5000)
            self.kernel.CloseHandle(information.hProcess)
            raise
        finally:
            self.kernel.CloseHandle(information.hThread)
        return information.hProcess

    def fetch_process_exit(self, process_handle: int) -> int | None:
        """Poll only the registered child without blocking its deadline monitor."""
        wait_result = self.kernel.WaitForSingleObject(process_handle, 0)
        if wait_result == 258:
            return None
        if wait_result != WAIT_OBJECT_0:
            raise ImportWorkspaceUnconfirmed("Windows process wait is unconfirmed")
        result = wintypes.DWORD()
        if not self.kernel.GetExitCodeProcess(process_handle, ctypes.byref(result)):
            raise ImportWorkspaceUnconfirmed("Windows process exit is unconfirmed")
        return int(result.value)

    def apply_termination(self) -> None:
        """Terminate only this run's entire contained process tree."""
        if not self.kernel.TerminateJobObject(self.handle, 1):
            raise ImportWorkspaceUnconfirmed("Windows job termination is unconfirmed")

    def apply_close(self) -> None:
        """Close this owner's job handle after completion has been checked."""
        self.kernel.CloseHandle(self.handle)
