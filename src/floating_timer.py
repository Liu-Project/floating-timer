#!/usr/bin/env python3
"""Floating Timer — a translucent, always-on-top countdown / stopwatch widget.

A tiny productivity tool for keeping track of time while presenting,
speaking, or working in meetings. Pure Python + Tkinter, no third-party
runtime dependencies.

Features
--------
- Always-on-top floating card, draggable anywhere on screen.
- Count-up (stopwatch) and count-down (timer) modes.
- Red minute flash reminder and a flashing finish alert.
- Keyboard shortcuts: Space to start/pause, R to reset.
- Translucent frosted-glass look (falls back to simple translucency).
"""

import subprocess
import tkinter as tk

GLASS = "#2a2e35"
EDGE = "#3d434c"
ACCENT = "#3584e4"
GREEN = "#2ec27e"
ORANGE = "#f5a742"
RED = "#e01b24"
TEXT = "#ffffff"
DIM = "#9aa3ad"
BTN_TEXT = "#c3cad3"
BTN_HOVER = "#3a414b"
PRIMARY_HOVER = "#33506b"
ALPHA = 0.9
FONT_TIME = ("Consolas", 44, "bold")
FONT_LABEL = ("Source Han Sans CN", 10)
FONT_SMALL = ("Source Han Sans CN", 9)


def format_time(sec):
    """Format a number of seconds as ``MM:SS`` (or ``HH:MM:SS`` past an hour)."""
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60) if m >= 60 else (0, m)
    if h:
        return "%02d:%02d:%02d" % (h, m, s)
    return "%02d:%02d" % (m, s)


def format_mode_label(mode, countdown_total):
    """Build the small caption shown under the clock."""
    if mode == "countdown":
        return "倒计时 %02d:%02d" % divmod(countdown_total, 60)
    return "正计时"


class FloatingTimer:
    def __init__(self, root):
        self.root = root
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        self.mode = "countup"
        self.running = False
        self.elapsed = 0
        self.countdown_total = 900
        self.countdown_left = 900
        self.tick_id = None
        self.flash_ids = []
        self.minute_flash_id = None

        self.card = tk.Frame(root, bg=GLASS, bd=0,
                             highlightthickness=1, highlightbackground=EDGE)
        self.card.pack(fill="both", expand=True)

        self.time_label = tk.Label(self.card, text="00:00", font=FONT_TIME,
                                   bg=GLASS, fg=TEXT)
        self.time_label.pack(pady=(14, 0))
        self.mode_label = tk.Label(self.card, text="正计时", font=FONT_SMALL,
                                   bg=GLASS, fg=DIM)
        self.mode_label.pack(pady=(0, 2))

        bar = tk.Frame(self.card, bg=GLASS)
        bar.pack(pady=(0, 12))
        self.btn_toggle = self.make_btn(bar, "开 始", self.toggle, primary=True)
        self.btn_toggle.pack(side="left", padx=4)
        self.make_btn(bar, "重 置", self.reset).pack(side="left", padx=4)

        for target in (self.card, self.time_label, self.mode_label, bar):
            target.bind("<Button-1>", self.start_drag)
            target.bind("<B1-Motion>", self.on_drag)
            target.bind("<Button-3>", self.show_menu)
        self.time_label.bind("<Double-Button-1>", lambda e: self.toggle())

        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="切换：倒计时/正计时", command=self.switch_mode)
        self.menu.add_command(label="时长 +1 分", command=lambda: self.shift(60))
        self.menu.add_command(label="时长 -1 分", command=lambda: self.shift(-60))
        self.menu.add_separator()
        self.top_var = tk.BooleanVar(value=True)
        self.menu.add_checkbutton(label="置顶", onvalue=True, offvalue=False,
                                  variable=self.top_var,
                                  command=self.set_topmost)
        self.menu.add_command(label="退出", command=root.destroy)
        root.bind("<space>", lambda e: self.toggle())
        root.bind("<r>", lambda e: self.reset())

        try:
            root.attributes("-alpha", ALPHA)
        except tk.TclError:
            pass
        root.after(300, self.apply_alpha)

        self.update_view()

    def apply_alpha(self):
        try:
            value = int(ALPHA * 0xFFFFFFFF)
            xid = self.top_xid()
            if xid:
                subprocess.Popen(["xprop", "-id", str(xid),
                                  "-f", "_NET_WM_WINDOW_OPACITY", "32c",
                                  "-set", "_NET_WM_WINDOW_OPACITY", str(value)])
        except Exception:
            pass

    def top_xid(self):
        import re

        def xwin(args):
            return subprocess.check_output(["xwininfo"] + args).decode(errors="replace")

        root_id = 0
        m = re.search(r"Window id: (0x[0-9a-fA-F]+)", xwin(["-root"]))
        if m:
            root_id = int(m.group(1), 16)
        cur = self.root.winfo_id()
        for _ in range(20):
            m = re.search(r"Parent window id: (0x[0-9a-fA-F]+)",
                          xwin(["-id", str(cur), "-tree"]))
            if not m:
                break
            parent = int(m.group(1), 16)
            if parent == 0 or parent == root_id:
                break
            cur = parent
        return cur

    def make_btn(self, parent, text, cmd, primary=False):
        hover = PRIMARY_HOVER if primary else BTN_HOVER
        fg = "#eef2f6" if primary else BTN_TEXT
        b = tk.Button(parent, text=text, command=cmd, relief="flat", bd=0,
                      bg=GLASS, fg=fg, activebackground=hover, activeforeground=fg,
                      font=FONT_LABEL, padx=14, pady=4, cursor="hand2",
                      highlightthickness=0)

        def on_enter(e):
            b.config(bg=hover)

        def on_leave(e):
            b.config(bg=GLASS)
        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        return b

    def set_topmost(self):
        self.root.attributes("-topmost", self.top_var.get())

    def start_drag(self, e):
        self._dx = e.x_root - self.root.winfo_x()
        self._dy = e.y_root - self.root.winfo_y()

    def on_drag(self, e):
        self.root.geometry("+%d+%d" % (e.x_root - self._dx, e.y_root - self._dy))

    def show_menu(self, e):
        self.menu.tk_popup(e.x_root, e.y_root)

    def toggle(self):
        self.running = not self.running
        self.btn_toggle.config(text="暂 停" if self.running else "开 始")
        if self.running and self.tick_id is None:
            self.tick()
        self.update_view()

    def reset(self):
        self.running = False
        self.btn_toggle.config(text="开 始")
        if self.tick_id:
            self.root.after_cancel(self.tick_id)
            self.tick_id = None
        self.clear_flash()
        self.clear_minute_flash()
        if self.mode == "countup":
            self.elapsed = 0
        else:
            self.countdown_left = self.countdown_total
        self.update_view()

    def shift(self, sec):
        self.countdown_total = max(0, self.countdown_total + sec)
        if not self.running:
            self.countdown_left = self.countdown_total
        self.update_view()

    def switch_mode(self):
        self.running = False
        self.btn_toggle.config(text="开 始")
        if self.tick_id:
            self.root.after_cancel(self.tick_id)
            self.tick_id = None
        self.clear_flash()
        self.clear_minute_flash()
        self.mode = "countdown" if self.mode == "countup" else "countup"
        self.update_view()

    def clear_flash(self):
        for i in self.flash_ids:
            self.root.after_cancel(i)
        self.flash_ids = []

    def clear_minute_flash(self):
        if self.minute_flash_id:
            self.root.after_cancel(self.minute_flash_id)
            self.minute_flash_id = None

    def minute_flash(self):
        self.clear_minute_flash()
        self.time_label.config(fg=RED)
        self.minute_flash_id = self.root.after(1000, self.restore_color)

    def restore_color(self):
        self.minute_flash_id = None
        self.update_view()

    def tick(self):
        if not self.running:
            return
        is_minute = False
        if self.mode == "countup":
            self.elapsed += 1
            if self.elapsed > 0 and self.elapsed % 60 == 0:
                is_minute = True
        else:
            self.countdown_left -= 1
            if self.countdown_left <= 0:
                self.countdown_left = 0
                self.running = False
                self.btn_toggle.config(text="开 始")
                self.update_view()
                self.flash()
                return
            if self.countdown_left % 60 == 0:
                is_minute = True
        self.update_view()
        if is_minute:
            self.minute_flash()
        self.tick_id = self.root.after(1000, self.tick)

    def flash(self):
        self.clear_flash()
        for i in range(6):
            color = RED if i % 2 == 0 else TEXT
            self.flash_ids.append(
                self.root.after(300 * i, lambda c=color: self.time_label.config(fg=c)))

    def fmt(self, sec):
        return format_time(sec)

    def remaining(self):
        if self.mode == "countup":
            return self.elapsed
        return self.countdown_left

    def update_view(self):
        sec = self.remaining()
        color = TEXT
        if not self.running:
            color = TEXT if sec else DIM
        elif self.mode == "countup":
            color = GREEN
        elif sec <= 60:
            color = ORANGE
        self.time_label.config(text=self.fmt(sec), fg=color)
        self.mode_label.config(text=format_mode_label(self.mode, self.countdown_total))


def main():
    root = tk.Tk()
    FloatingTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
