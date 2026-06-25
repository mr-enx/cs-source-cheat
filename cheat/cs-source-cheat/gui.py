# -*- coding: utf-8 -*-
"""GUI implementation for CS:S trainer"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import webbrowser
import struct

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from config import *
from memory_patcher import MemoryPatcher


class TrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(bg="#000000")

        self.font_title = ("Segoe UI", 13, "bold")
        self.font_main = ("Segoe UI", 10, "bold")
        self.font_status = ("Segoe UI", 10)
        self.font_link = ("Segoe UI", 9, "underline")

        self.mem = MemoryPatcher()
        self.codecave_address = 0
        self.is_connected = False
        self.engine_base = 0

        self.setup_ui()
        self.start_hotkey_listener()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Build the user interface"""
        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Title
        self.lbl_title = tk.Label(
            self.main_frame,
            text="Counter-Strike: Source Trainer",
            font=self.font_title,
            bg="#000000",
            fg="#FFFFFF"
        )
        self.lbl_title.pack(pady=(0, 10))

        self._create_connection_ui()
        self._create_options_ui()
        self._create_footer()

    def _create_connection_ui(self):
        """Create connection status and button"""
        self.connection_frame = tk.Frame(self.main_frame, bg="#000000")
        self.connection_frame.pack(pady=10)

        status_row = tk.Frame(self.connection_frame, bg="#000000")
        status_row.pack(pady=(0, 8), fill=tk.X)

        self.lbl_status_text = tk.Label(
            status_row,
            text="STATUS:",
            font=self.font_main,
            bg="#000000",
            fg="#CCCCCC"
        )
        self.lbl_status_text.pack(side=tk.LEFT)

        self.lbl_status = tk.Label(
            status_row,
            text="Not Connected",
            font=self.font_status,
            bg="#000000",
            fg="#FF4C4C"
        )
        self.lbl_status.pack(side=tk.LEFT, padx=(5, 0))

        self.btn_connect = tb.Button(
            self.connection_frame,
            text="Connect to Game",
            bootstyle=SECONDARY,
            width=18,
            command=self.connect_to_game
        )
        self.btn_connect.pack(pady=(5, 0))

    def _create_options_ui(self):
        """Create feature checkboxes"""
        self.options_frame = tk.Frame(self.main_frame, bg="#000000")
        self.options_frame.pack_forget()

        self.lbl_options_title = tk.Label(
            self.options_frame,
            text="Available Features",
            font=self.font_main,
            bg="#000000",
            fg="#FFFFFF"
        )
        self.lbl_options_title.pack(pady=(5, 8))

        self.features_frame = tk.Frame(self.options_frame, bg="#000000")
        self.features_frame.pack(anchor=tk.W, padx=15)

        # Variables
        self.var_wh = tk.BooleanVar()
        self.var_smoke = tk.BooleanVar()
        self.var_flash = tk.BooleanVar()
        self.var_fb = tk.BooleanVar()
        self.var_nosky = tk.BooleanVar()
        self.var_norecoil = tk.BooleanVar()
        self.var_bhop = tk.BooleanVar()
        self.var_nospread = tk.BooleanVar()
        self.var_rcs = tk.BooleanVar()

        # Checkbuttons
        self.chk_wh = self._create_checkbutton("Wallhack", self.var_wh, self.toggle_wallhack)
        self.chk_smoke = self._create_checkbutton("No Smoke", self.var_smoke, self.toggle_smoke)
        self.chk_flash = self._create_checkbutton("No Flash", self.var_flash, self.toggle_flash)
        self.chk_fb = self._create_checkbutton("Remove Shadows", self.var_fb, self.toggle_fullbright)
        self.chk_nosky = self._create_checkbutton("No Hands & No Sky", self.var_nosky, self.toggle_nosky)
        self.chk_norecoil = self._create_checkbutton("No Camera Shake (Visual No Recoil)", self.var_norecoil, self.toggle_norecoil)
        self.chk_rcs = self._create_checkbutton("Perfect No Recoil (Bullets in one spot)", self.var_rcs, self.toggle_rcs)
        self.chk_bhop = self._create_checkbutton("Bunnyhop", self.var_bhop, self.toggle_bunnyhop)
        self.chk_nospread = self._create_checkbutton("No Spread (Visual Only)", self.var_nospread, self.toggle_nospread)

        # Bunnyhop thread
        self.bhop_thread = None
        self.bhop_running = False
        
        # RCS thread
        self.rcs_thread = None
        self.rcs_running = False

    def _create_checkbutton(self, text, variable, command):
        """Helper to create a checkbutton"""
        chk = tb.Checkbutton(
            self.features_frame,
            text=text,
            variable=variable,
            bootstyle="round-toggle",
            command=command
        )
        chk.state(["disabled"])
        chk.pack(anchor=tk.W, pady=2)
        return chk

    def _create_footer(self):
        """Create footer link"""
        self.link_label = tk.Label(
            self.main_frame,
            text="genius-programmer.com",
            font=self.font_link,
            bg="#000000",
            fg="#00A8FF",
            cursor="hand2"
        )
        self.link_label.pack(side=tk.BOTTOM, pady=(15, 0))
        self.link_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab(WEBSITE_URL))

    def connect_to_game(self):
        """Connect to game process"""
        pid = self.mem.get_process_id(GAME_WINDOW_NAME)
        if not pid:
            messagebox.showerror("Error", "Game window not found! Please run the game first.")
            return

        self.mem.process_handle = self.mem.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not self.mem.process_handle or self.mem.process_handle == -1:
            messagebox.showerror("Access Error", "Cannot connect to game process. Please run this trainer as Administrator.")
            return

        self.engine_base = self.mem.get_module_base("engine.dll")
        if not self.engine_base:
            messagebox.showerror("Error", "engine.dll module not found!")
            return

        self.codecave_address = self.mem.setup_codecave()
        if not self.codecave_address:
            messagebox.showerror("Error", "Memory allocation failed.")
            return

        self.is_connected = True
        self.lbl_status.config(text="Connected", fg="#43B581")

        self.connection_frame.pack_forget()
        self.lbl_status_text.pack_forget()

        for chk in [self.chk_wh, self.chk_smoke, self.chk_flash, self.chk_fb, self.chk_nosky, self.chk_norecoil, self.chk_rcs, self.chk_bhop, self.chk_nospread]:
            chk.state(["!disabled"])

        self.options_frame.pack(pady=10, fill=tk.X)

    def toggle_wallhack(self):
        if not self.is_connected:
            return
        value = ENABLE_WALLHACK if self.var_wh.get() else DISABLE_WALLHACK
        self.mem.write_short(WALLHACK_ADDRESS, value)

    def toggle_smoke(self):
        if not self.is_connected:
            return
        if self.var_smoke.get():
            self.mem.write_int(ADDR_PARTICLES, 0)
            hook_jmp_offset = self.codecave_address - (ADDR_HOOK_5B + 5)
            hook_bytes = [0xE9] + list(struct.pack('<i', hook_jmp_offset))
            self.mem.write_bytes(ADDR_HOOK_5B, hook_bytes)
        else:
            self.mem.write_int(ADDR_PARTICLES, 1)
            self.mem.write_bytes(ADDR_HOOK_5B, [0x8B, 0x01, 0xFF, 0x50, 0x04])

    def toggle_flash(self):
        if not self.is_connected:
            return
        bytes_val = [0x90, 0xE9] if self.var_flash.get() else [0x0F, 0x8B]
        self.mem.write_bytes(ADDR_PATCH_2B, bytes_val)

    def toggle_fullbright(self):
        if not self.is_connected:
            return
        addr = self.engine_base + OFFSET_FULLBRIGHT - ENGINE_DELTA
        value = 1 if self.var_fb.get() else 0
        self.mem.write_int(addr, value)

    def toggle_nosky(self):
        if not self.is_connected:
            return
        if self.var_nosky.get():
            self.mem.write_int(ADDR_NOSKY_1, 0)
            self.mem.write_int(ADDR_NOSKY_2, 1)
        else:
            self.mem.write_int(ADDR_NOSKY_1, 1)
            self.mem.write_int(ADDR_NOSKY_2, 0)

    def toggle_norecoil(self):
        if not self.is_connected:
            return
        if self.var_norecoil.get():
            self.mem.write_int(ADDR_VISUAL_NORECOIL_1, 0)
            self.mem.write_int(ADDR_VISUAL_NORECOIL_2, 0)
        else:
            self.mem.write_int(ADDR_VISUAL_NORECOIL_1, 0x0BB0)
            self.mem.write_int(ADDR_VISUAL_NORECOIL_2, 0x0BB4)

    def toggle_rcs(self):
        if not self.is_connected:
            return
        if self.var_rcs.get():
            self.rcs_running = True
            if not self.rcs_thread or not self.rcs_thread.is_alive():
                self.rcs_thread = threading.Thread(target=self._rcs_loop, daemon=True)
                self.rcs_thread.start()
        else:
            self.rcs_running = False

    def _rcs_loop(self):
        while self.rcs_running and self.is_connected:
            try:
                local_player = self.mem.read_int(CLIENT_BASE + OFFSET_LOCALPLAYER)
                if local_player:
                    # Freeze PunchAngle to 0.0 constantly so bullets have no recoil kick
                    self.mem.write_float(local_player + OFFSET_PUNCHANGLE, 0.0)
                    self.mem.write_float(local_player + OFFSET_PUNCHANGLE + 4, 0.0)
                    self.mem.write_float(local_player + OFFSET_PUNCHANGLE + 8, 0.0)
            except Exception:
                pass
            time.sleep(0.001)

    def toggle_bunnyhop(self):
        if not self.is_connected:
            return
        if self.var_bhop.get():
            self.bhop_running = True
            if not self.bhop_thread or not self.bhop_thread.is_alive():
                self.bhop_thread = threading.Thread(target=self._bunnyhop_loop, daemon=True)
                self.bhop_thread.start()
        else:
            self.bhop_running = False

    def _bunnyhop_loop(self):
        while self.bhop_running and self.is_connected:
            try:
                space_pressed = self.mem.user32.GetAsyncKeyState(VK_SPACE) & 0x8000
                if space_pressed:
                    local_player = self.mem.read_int(CLIENT_BASE + OFFSET_LOCALPLAYER_BHOP)
                    if local_player:
                        flags = self.mem.read_int(local_player + OFFSET_FLAGS)
                        on_ground = flags & 1
                        
                        if on_ground:
                            self.mem.write_int(CLIENT_BASE + OFFSET_FORCEJUMP, 5) # +jump
                        else:
                            self.mem.write_int(CLIENT_BASE + OFFSET_FORCEJUMP, 4) # -jump
            except Exception:
                pass
            time.sleep(0.001)

    def toggle_nospread(self):
        if not self.is_connected:
            return
        if self.var_nospread.get():
            # Apply No Spread/No Recoil stabilization (cl_predictweapons patch)
            self.mem.write_bytes(ADDR_PREDICTWEAPONS_PATCH, [0x90, 0x90, 0x90, 0x90, 0x90])
        else:
            # Restore original bytes (CALL instruction)
            self.mem.write_bytes(ADDR_PREDICTWEAPONS_PATCH, [0xE8, 0x03, 0x28, 0xFF, 0xFF])

    def start_hotkey_listener(self):
        """Start hotkey monitoring thread"""
        self.hotkey_thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self.hotkey_thread.start()

    def _hotkey_loop(self):
        """Monitor Mouse4 for toggling features"""
        while True:
            if self.mem.user32.GetAsyncKeyState(VK_XBUTTON1) & 0x1:
                if self.is_connected:
                    new_state = not self.var_wh.get()
                    
                    self.var_wh.set(new_state)
                    self.toggle_wallhack()
                    
                    self.var_smoke.set(new_state)
                    self.toggle_smoke()
                    
                    self.var_flash.set(new_state)
                    self.toggle_flash()

            time.sleep(0.1)

    def on_closing(self):
        """Cleanup before closing"""
        if self.is_connected:
            self.bhop_running = False
            for var, toggle in [
                (self.var_smoke, self.toggle_smoke),
                (self.var_flash, self.toggle_flash),
                (self.var_fb, self.toggle_fullbright),
                (self.var_wh, self.toggle_wallhack),
                (self.var_nosky, self.toggle_nosky),
                (self.var_norecoil, self.toggle_norecoil),
                (self.var_bhop, self.toggle_bunnyhop),
                (self.var_nospread, self.toggle_nospread)
            ]:
                if var.get():
                    var.set(False)
                    toggle()
        self.root.destroy()
