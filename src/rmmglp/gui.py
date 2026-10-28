"""Small desktop frontend. USB work runs in a single background worker."""
from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from . import service
from .protocol import EP3, RGB_CAPTURED, RGB_NAMED, all_actions, replace_button
from .state import load_state


class Application:
    def __init__(self, root):
        self.root = root
        self.busy = False
        self.messages = queue.Queue()
        root.title("Rise Mode RM-MG-LP - Configuration Utility")
        root.geometry("920x700")
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="RM-MG-LP", font=("TkDefaultFont", 20, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Values below come from the utility's saved configuration, not live hardware.").pack(anchor="w", pady=6)
        ttk.Label(frame, text="DPI/RGB Apply resends the managed profile and captured button defaults.").pack(anchor="w")
        self.status = tk.StringVar(value="Ready - preview performs no USB access.")
        self.saved = tk.StringVar()
        ttk.Label(frame, textvariable=self.saved, wraplength=850).pack(anchor="w", pady=6)
        self.dpi = tk.StringVar(value="1200")
        self.polling = tk.StringVar(value="1000")
        self.rgb = tk.StringVar(value="green")
        self.slot = tk.StringVar(value="5")
        self.action = tk.StringVar(value="right")
        self.buttons = []
        for title, variable, values, operation in (
            ("DPI", self.dpi, None, service.set_dpi),
            ("Polling (Hz)", self.polling, ("500", "1000"), service.set_polling),
            ("RGB capture", self.rgb, tuple(RGB_NAMED) + tuple(f"capture-{n}" for n in RGB_CAPTURED), self.rgb_operation),
        ):
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=title, width=16).pack(side="left")
            if values is None:
                ttk.Spinbox(row, from_=200, to=16000, increment=100, textvariable=variable, width=20).pack(side="left")
            else:
                ttk.Combobox(row, textvariable=variable, values=values, state="readonly", width=20).pack(side="left")
            for label, dry_run in (("Preview", True), ("Apply", False)):
                button = ttk.Button(row, text=label, command=lambda v=variable, op=operation, dry=dry_run: self.run(op, v.get(), dry))
                button.pack(side="left", padx=6)
                self.buttons.append(button)
        row = ttk.LabelFrame(frame, text="Button packet preview only - based on captured EP3 #3", padding=8)
        row.pack(fill="x", pady=10)
        ttk.Combobox(row, textvariable=self.slot, values=tuple(range(1, 9)), state="readonly", width=5).pack(side="left")
        ttk.Combobox(row, textvariable=self.action, values=sorted(all_actions()), state="readonly", width=22).pack(side="left", padx=8)
        button = ttk.Button(row, text="Preview slot", command=self.preview_button)
        button.pack(side="left")
        self.buttons.append(button)
        ttk.Label(frame, text="RGB: green physically verified; red/blue captured. Effect names remain unverified.").pack(anchor="w")
        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=8)
        self.output = ScrolledText(frame, wrap="none", height=20, font=("TkFixedFont", 10))
        self.output.pack(fill="both", expand=True)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=self.output.xview)
        horizontal.pack(fill="x")
        self.output.configure(xscrollcommand=horizontal.set)
        self.output.configure(state="disabled")
        self.refresh()
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(50, self.poll)

    def log(self, message):
        self.output.configure(state="normal")
        self.output.insert("end", str(message) + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def refresh(self):
        try:
            state = load_state()
            self.dpi.set(str(state["dpi"]))
            self.polling.set(str(state["polling"]))
            self.saved.set("Saved configuration: " + json.dumps(state))
            pair = (state["rgb_ctrl5"], state["rgb_ctrl6"])
            self.rgb.set("")
            for name, packets in list(RGB_NAMED.items()) + [(f"capture-{n}", p) for n, p in RGB_CAPTURED.items()]:
                if tuple(bytes.fromhex(v) for v in pair) == packets:
                    self.rgb.set(name)
                    break
        except (ValueError, RuntimeError, OSError) as exc:
            self.saved.set("Saved configuration unavailable")
            self.log(f"Error: {exc}")

    @staticmethod
    def rgb_operation(value, dry_run, emit):
        if value.startswith("capture-"):
            return service.set_rgb_capture(int(value.split("-", 1)[1]), dry_run, emit)
        return service.set_rgb_named(value, dry_run, emit)

    def run(self, operation, value, dry_run):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.configure(state="disabled")
        self.status.set("Preparing preview…" if dry_run else "Sending configuration…")

        def work():
            try:
                argument = value if operation == self.rgb_operation else int(value)
                operation(argument, dry_run=dry_run, emit=lambda msg: self.messages.put(("log", msg)))
                self.messages.put(("done", "Preview complete - nothing sent or saved." if dry_run else "Configuration sent and saved."))
            except Exception as exc:
                self.messages.put(("error", str(exc)))

        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, message = self.messages.get_nowait()
                self.log(message)
                if kind != "log":
                    self.busy = False
                    self.status.set(("Error: " if kind == "error" else "") + message)
                    for button in self.buttons:
                        button.configure(state="normal")
                    if kind == "done":
                        self.refresh()
        except queue.Empty:
            pass
        self.root.after(50, self.poll)

    def preview_button(self):
        self.log("Captured base: " + EP3[3].hex(" "))
        self.log("Preview only: " + replace_button(EP3[3], int(self.slot.get()), self.action.get()).hex(" "))

    def close(self):
        if self.busy:
            self.status.set("Wait for the current operation to finish before closing.")
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
