#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CS:S v34 Multi-Hack Trainer - Entry Point"""

import ttkbootstrap as tb
from gui import TrainerGUI


def main():
    app_style = tb.Style("darkly")
    root = app_style.master
    root.configure(bg="#000000")
    app = TrainerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
