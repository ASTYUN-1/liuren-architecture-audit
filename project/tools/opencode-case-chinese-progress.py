"""Refresh a Chinese status page for an already running controller without restarting it."""
import argparse
import ctypes
import importlib.util
import os
from pathlib import Path
import time

spec = importlib.util.spec_from_file_location('controller', Path(__file__).with_name('opencode-case-continue.py'))
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


def alive(pid):
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    try:
        code = ctypes.c_ulong()
        return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
    finally:
        kernel.CloseHandle(handle)


def refresh(run):
    state = controller.batch.read_json(run / 'controller.json')
    if state['state'] == 'running' and not alive(state['pid']):
        state = dict(state, state='stopped_runtime_error')
    controller.write_progress(run, state, filename='中文进度.md')
    return state['state'] == 'running'


def watch(run):
    lock = run / '中文进度.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    try:
        while refresh(run):
            time.sleep(5)
    finally:
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    (watch if args.watch else refresh)(args.run.resolve())
