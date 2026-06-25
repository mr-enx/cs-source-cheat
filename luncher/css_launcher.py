import socket
import sys
import tkinter as tk
from tkinter import ttk
import subprocess
import os

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_ipv4():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "نامشخص"

def launch_game():
    app_dir = get_app_dir()
    game_dir = os.path.join(app_dir, "Counter Strike Source v.34")
    game_exe = os.path.join(game_dir, "hl2.exe")
    if os.path.exists(game_exe):
        subprocess.Popen([game_exe, "-game", "cstrike"], cwd=game_dir)
    else:
        error_label.config(text="فایل بازی یافت نشد!")

root = tk.Tk()
root.title("لانچر کانتر سورس")
root.geometry("400x250")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Arial", 11))
style.configure("Title.TLabel", background="#1e1e1e", foreground="#ffffff", font=("Arial", 16, "bold"))
style.configure("IP.TLabel", background="#1e1e1e", foreground="#00ff00", font=("Consolas", 12, "bold"))
style.configure("TButton", background="#3a3a3a", foreground="#ffffff", font=("Arial", 11, "bold"), padding=10)
style.map("TButton",
          background=[("active", "#5a5a5a"), ("!disabled", "#3a3a3a")],
          foreground=[("active", "#ffffff"), ("!disabled", "#ffffff")])

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(frame, text="لانچر کانتر سورس", style="Title.TLabel")
title_label.pack(pady=(0, 20))

launch_button = ttk.Button(frame, text="اجرای بازی", command=launch_game)
launch_button.pack(pady=10, fill=tk.X)

ip_title_label = ttk.Label(frame, text="آیپی شما (IPv4):")
ip_title_label.pack(pady=(15, 2))

ip_value_label = ttk.Label(frame, text=get_ipv4(), style="IP.TLabel")
ip_value_label.pack()

error_label = ttk.Label(frame, text="", foreground="red", background="#1e1e1e")
error_label.pack(pady=(10, 0))

root.mainloop()
