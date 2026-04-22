# -*- coding: utf-8 -*-
"""Configuration and constants for CS:S trainer"""

# Memory access constants
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_EXECUTE_READWRITE = 0x40

# Client base address
CLIENT_BASE = 0x24000000

# Feature addresses
WALLHACK_ADDRESS = 0x243B0C9C
ENABLE_WALLHACK = 2
DISABLE_WALLHACK = 1

ADDR_PARTICLES = CLIENT_BASE + 0x3E9C34   # No Smoke
ADDR_HOOK_5B = CLIENT_BASE + 0x8E4F3      # No Smoke
ADDR_PATCH_2B = CLIENT_BASE + 0x1D1D5D    # No Flash

ADDR_NOSKY_1 = CLIENT_BASE + 0x3EEDFC     # No Hands & No Sky
ADDR_NOSKY_2 = CLIENT_BASE + 0x3EE78C     # No Hands & No Sky

# Engine addresses
OFFSET_FULLBRIGHT = 0x4F0C44
ENGINE_DELTA = 0

# UI Configuration
WINDOW_TITLE = "CS:S v34 Multi-Hack"
WINDOW_SIZE = "360x360"
GAME_WINDOW_NAME = "Counter-Strike Source"
WEBSITE_URL = "https://genius-programmer.com"

# Virtual key codes
VK_XBUTTON1 = 0x06  # Mouse Button 4
