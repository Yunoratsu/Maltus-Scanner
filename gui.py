import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
from scanner import scan_port
from utils import resolve_host

# --- Theme Configuration ---
BG_DARK = "#11111b"
BG_SURFACE = "#1e1e2e"
FG_TEXT = "#cdd6f4"
ACCENT = "#89b4fa"
OPEN_COLOR = "#a6e3a1"
CLOSED_COLOR = "#f38ba8"
SAVE_BTN_COLOR = "#b4befe"

# --- Global Control ---
is_stopping = False

# --- Functions ---

def start_scan():
    global is_stopping
    is_stopping = False

    host = entry_host.get().strip()
    if not host:
        messagebox.showerror("Error", "Please enter a hostname")
        return

    ip = resolve_host(host)
    if not ip:
        messagebox.showerror("Error", "Invalid hostname")
        return

    # Header for the log
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"{'='*40}\nSCAN REPORT\nTarget: {host} ({ip})\nStarted: {now}\n{'='*40}\n\n"

    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, header, "info")

    try:
        start_port = int(entry_start_port.get())
        end_port = int(entry_end_port.get())
    except ValueError:
        messagebox.showerror("Error", "Ports must be integers")
        return

    progress_bar["maximum"] = end_port - start_port + 1
    progress_bar["value"] = 0

    def run_scan():
        global is_stopping
        for i, port in enumerate(range(start_port, end_port + 1), start=1):
            if is_stopping:
                text_output.insert(tk.END, "\n[!] Scan stopped by user.\n", "closed")
                break

            if scan_port(ip, port):
                text_output.insert(tk.END, f"Port {port:5} : OPEN\n", "open")
            else:
                # Optionally hide closed ports by commenting the next line
                text_output.insert(tk.END, f"Port {port:5} : closed\n", "closed")

            text_output.see(tk.END)
            progress_bar["value"] = i

        text_output.insert(tk.END, f"\n--- Scan Complete at {datetime.now().strftime('%H:%M:%S')} ---\n", "info")

    threading.Thread(target=run_scan, daemon=True).start()

def stop_scan_action():
    global is_stopping
    is_stopping = True

def save_log():
    log_content = text_output.get("1.0", tk.END).strip()
    if not log_content:
        messagebox.showwarning("Empty Log", "No data to save!")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Scan Results"
    )

    if file_path:
        try:
            with open(file_path, "w") as f:
                f.write(log_content)
            messagebox.showinfo("Success", "Log saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

# --- UI Setup ---

root = tk.Tk()
root.title("Maltus Port Scanner")
root.geometry("650x700")
root.configure(bg=BG_DARK)

try:
    root.iconbitmap("eye-closed.ico")
except:
    pass

style = ttk.Style()
style.theme_use('clam')
style.configure("TFrame", background=BG_DARK)
style.configure("TLabel", background=BG_DARK, foreground=FG_TEXT, font=("Segoe UI", 10))
style.configure("Horizontal.TProgressbar", thickness=10, troughcolor=BG_SURFACE, background=ACCENT, borderwidth=0)

frame = ttk.Frame(root, padding=25)
frame.pack(fill="both", expand=True)

# Inputs
ttk.Label(frame, text="Target Hostname").grid(column=0, row=0, sticky="w")
entry_host = tk.Entry(frame, bg=BG_SURFACE, fg=FG_TEXT, insertbackground=FG_TEXT,
                      relief="flat", font=("Segoe UI", 11), borderwidth=8)
entry_host.grid(column=0, row=1, columnspan=4, sticky="we", pady=(5, 15))

ttk.Label(frame, text="Start Port").grid(column=0, row=2, sticky="w")
entry_start_port = tk.Entry(frame, bg=BG_SURFACE, fg=FG_TEXT, insertbackground=FG_TEXT,
                            relief="flat", borderwidth=8, width=10)
entry_start_port.insert(0, "1")
entry_start_port.grid(column=0, row=3, sticky="w")

ttk.Label(frame, text="End Port").grid(column=1, row=2, sticky="w", padx=10)
entry_end_port = tk.Entry(frame, bg=BG_SURFACE, fg=FG_TEXT, insertbackground=FG_TEXT,
                          relief="flat", borderwidth=8, width=10)
entry_end_port.insert(0, "1024")
entry_end_port.grid(column=1, row=3, sticky="w", padx=10)

# Button Container
btn_frame = tk.Frame(frame, bg=BG_DARK)
btn_frame.grid(column=2, row=3, columnspan=2, sticky="e")

btn_scan = tk.Button(btn_frame, text="SCAN", command=start_scan, bg=ACCENT,
                     fg=BG_DARK, font=("Segoe UI", 9, "bold"), relief="flat", width=10, cursor="hand2")
btn_scan.pack(side="left", padx=2)

btn_stop = tk.Button(btn_frame, text="STOP", command=stop_scan_action, bg=CLOSED_COLOR,
                     fg=BG_DARK, font=("Segoe UI", 9, "bold"), relief="flat", width=10, cursor="hand2")
btn_stop.pack(side="left", padx=2)

btn_save = tk.Button(btn_frame, text="SAVE", command=save_log, bg=SAVE_BTN_COLOR,
                     fg=BG_DARK, font=("Segoe UI", 9, "bold"), relief="flat", width=10, cursor="hand2")
btn_save.pack(side="left", padx=2)

# Output Box
text_output = tk.Text(frame, width=60, height=20, bg=BG_SURFACE, fg=FG_TEXT,
                      padx=15, pady=15, font=("Consolas", 10), relief="flat")
text_output.grid(column=0, row=4, columnspan=4, pady=20)

# Progress
progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", style="Horizontal.TProgressbar")
progress_bar.grid(column=0, row=5, columnspan=4, sticky="we")

# Tags
text_output.tag_config("open", foreground=OPEN_COLOR)
text_output.tag_config("closed", foreground=CLOSED_COLOR)
text_output.tag_config("info", foreground=ACCENT)

root.mainloop()