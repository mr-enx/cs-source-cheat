# -*- coding: utf-8 -*-
"""Memory patching functionality for CS:S trainer"""

import ctypes
from ctypes import wintypes
import struct
import psutil
from config import *


class MemoryPatcher:
    def __init__(self):
        self.kernel32 = ctypes.WinDLL('kernel32')
        self.user32 = ctypes.WinDLL('user32')
        self.process_handle = None
        self.pid = 0

        self._setup_function_signatures()

    def _setup_function_signatures(self):
        """Configure ctypes function signatures"""
        self.kernel32.VirtualProtectEx.argtypes = [
            wintypes.HANDLE,
            ctypes.c_void_p,
            ctypes.c_size_t,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD)
        ]
        self.kernel32.VirtualAllocEx.argtypes = [
            wintypes.HANDLE,
            ctypes.c_void_p,
            ctypes.c_size_t,
            wintypes.DWORD,
            wintypes.DWORD
        ]
        self.kernel32.VirtualAllocEx.restype = ctypes.c_void_p

    def get_process_id(self, window_name):
        """Find process ID by window name"""
        hWnd = self.user32.FindWindowW(None, window_name)
        if not hWnd:
            return 0
        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hWnd, ctypes.byref(pid))
        self.pid = pid.value
        return self.pid

    def get_module_base(self, module_name):
        """Get base address of a module"""
        try:
            for p in psutil.process_iter(['pid', 'name']):
                if p.info['pid'] == self.pid:
                    for m in p.memory_maps(grouped=False):
                        if m.path and m.path.lower().endswith(module_name.lower()):
                            return int(m.addr.split('-')[0], 16)
        except Exception:
            pass
        return 0

    def write_bytes(self, address, byte_list):
        """Write bytes to process memory"""
        if not self.process_handle:
            return False

        buffer = (ctypes.c_byte * len(byte_list))(*byte_list)
        bytes_written = wintypes.DWORD()
        old_protect = wintypes.DWORD()

        self.kernel32.VirtualProtectEx(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.sizeof(buffer),
            PAGE_EXECUTE_READWRITE,
            ctypes.byref(old_protect)
        )

        result = self.kernel32.WriteProcessMemory(
            self.process_handle,
            address,
            buffer,
            ctypes.sizeof(buffer),
            ctypes.byref(bytes_written)
        )

        self.kernel32.VirtualProtectEx(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.sizeof(buffer),
            old_protect.value,
            ctypes.byref(old_protect)
        )

        return bool(result)

    def write_int(self, address, value):
        """Write 4-byte integer to memory"""
        byte_list = list(struct.pack('<i', value))
        return self.write_bytes(address, byte_list)

    def write_short(self, address, value):
        """Write 2-byte short to memory"""
        byte_list = list(struct.pack('<h', value))
        return self.write_bytes(address, byte_list)

    def read_bytes(self, address, size):
        """Read bytes from process memory"""
        if not self.process_handle:
            return None
        buffer = ctypes.create_string_buffer(size)
        bytes_read = wintypes.DWORD()
        self.kernel32.ReadProcessMemory(
            self.process_handle,
            address,
            buffer,
            size,
            ctypes.byref(bytes_read)
        )
        return buffer.raw

    def read_int(self, address):
        """Read 4-byte integer from memory"""
        bytes_val = self.read_bytes(address, 4)
        if bytes_val:
            return struct.unpack('<i', bytes_val)[0]
        return 0

    def read_float(self, address):
        """Read 4-byte float from memory"""
        bytes_val = self.read_bytes(address, 4)
        if bytes_val:
            return struct.unpack('<f', bytes_val)[0]
        return 0.0

    def write_float(self, address, value):
        """Write 4-byte float to memory"""
        byte_list = list(struct.pack('<f', value))
        return self.write_bytes(address, byte_list)

    def setup_codecave(self):
        """Allocate and setup codecave for smoke hook"""
        codecave_addr = self.kernel32.VirtualAllocEx(
            self.process_handle,
            None,
            1024,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE
        )
        if not codecave_addr:
            return 0

        jmp_offset = (ADDR_HOOK_5B + 5) - (codecave_addr + 17)

        shellcode = bytearray([
            0x8B, 0x01,                         # mov eax, [ecx]
            0x3D, 0x98, 0x6C, 0x33, 0x24,       # cmp eax, 0x24336C98
            0x75, 0x03,                         # jne +3
            0xFF, 0x50, 0x04,                   # call [eax+4]
            0xE9                                # jmp back
        ])

        shellcode.extend(struct.pack('<i', jmp_offset))
        self.write_bytes(codecave_addr, list(shellcode))
        return codecave_addr
