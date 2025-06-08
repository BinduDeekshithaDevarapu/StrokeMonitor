import os
import tkinter as tk
from tkinter import scrolledtext, font
from pynput import keyboard

LOG_FILE = "keystrokes.txt"

class KeyLoggerApp:
    def __init__(self):
        self.buffer = []
        self.buffer_limit = 1000
        self.recording = True
        self.search_focused = False

        # Load previously saved keystrokes
        self.load_buffer()

        self.root = tk.Tk()
        self.root.title("KeyLogger App")
        self.root.geometry("700x500")
        self.root.minsize(500, 300)
        self.root.configure(bg="#2e2e2e")

        self.font_regular = font.Font(family="Segoe UI", size=11)
        self.font_bold = font.Font(family="Segoe UI", size=11, weight="bold")
        self.bg_color = "#2e2e2e"
        self.text_bg = "#1e1e1e"
        self.text_fg = "#f0f0f0"
        self.highlight_bg = "#ffd54f"
        self.highlight_fg = "#000000"
        self.btn_bg = "#007acc"
        self.btn_fg = "#ffffff"
        self.entry_bg = "#3c3c3c"
        self.entry_fg = "#f0f0f0"

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Search bar
        search_frame = tk.Frame(self.root, bg=self.bg_color)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        search_frame.columnconfigure(1, weight=1)

        lbl_search = tk.Label(search_frame, text="Search:", bg=self.bg_color, fg=self.text_fg, font=self.font_bold)
        lbl_search.grid(row=0, column=0, sticky="w")

        self.search_entry = tk.Entry(search_frame, bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.entry_fg,
                                     relief="flat", font=self.font_regular)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(8,0))
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Text display
        self.text_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=self.font_regular,
                                                      bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                                      relief="flat", undo=True)
        self.text_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.text_display.config(state=tk.DISABLED)

        # Button frame
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        btn_frame.columnconfigure((0,1), weight=1)

        self.toggle_button = tk.Button(btn_frame, text="Stop Recording", command=self.toggle_recording,
                                       bg=self.btn_bg, fg=self.btn_fg, font=self.font_bold,
                                       activebackground="#005a9e", activeforeground="#ffffff",
                                       relief="flat", cursor="hand2", padx=15, pady=8)
        self.toggle_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        clear_button = tk.Button(btn_frame, text="Clear Text", command=self.clear_text,
                                 bg="#cc3300", fg=self.btn_fg, font=self.font_bold,
                                 activebackground="#aa2200", activeforeground="#ffffff",
                                 relief="flat", cursor="hand2", padx=15, pady=8)
        clear_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # Update UI
        self.update_ui()

    def load_buffer(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                self.buffer = list(f.read())

    def save_buffer(self):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(''.join(self.buffer))

    def clear_text(self):
        self.buffer.clear()
        self.save_buffer()
        self.update_ui()

    def on_search_focus_in(self, event):
        self.search_focused = True

    def on_search_focus_out(self, event):
        self.search_focused = False

    def on_search_change(self, event):
        self.highlight_search()

    def toggle_recording(self):
        self.recording = not self.recording
        self.toggle_button.config(text="Stop Recording" if self.recording else "Start Recording")

    def on_press(self, key):
        if self.search_focused or not self.recording:
            return
        try:
            char = key.char
            if char:
                self.buffer.append(char)
        except AttributeError:
            if key == keyboard.Key.space:
                self.buffer.append(' ')
            elif key == keyboard.Key.enter:
                self.buffer.append('\n')
            elif key == keyboard.Key.tab:
                self.buffer.append('\t')
            elif key == keyboard.Key.backspace:
                if self.buffer:
                    self.buffer.pop()

        if len(self.buffer) > self.buffer_limit:
            excess = len(self.buffer) - self.buffer_limit
            self.buffer = self.buffer[excess:]

        self.save_buffer()

    def update_ui(self):
        text = ''.join(self.buffer)
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete('1.0', tk.END)
        self.text_display.insert(tk.END, text)
        self.text_display.config(state=tk.DISABLED)
        self.highlight_search()
        self.root.after(200, self.update_ui)

    def highlight_search(self):
        self.text_display.tag_remove("highlight", "1.0", tk.END)
        query = self.search_entry.get()
        if not query:
            return
        idx = '1.0'
        while True:
            idx = self.text_display.search(query, idx, nocase=1, stopindex=tk.END)
            if not idx:
                break
            end_idx = f"{idx}+{len(query)}c"
            self.text_display.tag_add("highlight", idx, end_idx)
            idx = end_idx
        self.text_display.tag_config("highlight", background=self.highlight_bg, foreground=self.highlight_fg)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyLoggerApp()
    app.run()
