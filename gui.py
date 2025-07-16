import os
import subprocess
import threading
import time
import sys
from tkinter import filedialog, Listbox, StringVar, END, MULTIPLE, BOTH, RIGHT, LEFT, Y, X, TclError, Text, Scrollbar, VERTICAL
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from src.device_utils import wait_for_device, detect_current_slot
from src.partition_utils import list_byname_partitions, detect_ab_device, get_partition_size
from src.backup import backup_partitions

# Utility to format sizes
def format_size(mb):
    return f"{mb/1024:.2f} GB" if mb >= 1024 else f"{mb:.1f} MB"

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, message):
        self.text_widget.after(0, self.text_widget.insert, END, message)
        self.text_widget.after(0, self.text_widget.see, END)
    def flush(self):
        pass

class PartitionBackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Partition Backup Tool")
        self.root.geometry("1080x720")
        self.root.resizable(True, True)

        self.output_dir = ""
        self.partition_info = {}
        self.all_partition_names = []
        self.filtered_partition_names = []

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Partition List
        center_frame = ttk.Frame(main_frame)
        center_frame.grid(row=0, column=0, sticky="nsew")
        ttk.Label(center_frame, text="Search Partitions:").pack(anchor="w")
        self.search_var = StringVar()
        self.search_var.trace("w", self.filter_partitions)
        ttk.Entry(center_frame, textvariable=self.search_var, width=40).pack(fill=X, pady=5)

        partition_frame = ttk.Frame(center_frame)
        partition_frame.pack(fill=BOTH, expand=True)
        scrollbar = ttk.Scrollbar(partition_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.partition_box = Listbox(partition_frame, selectmode=MULTIPLE, width=60, height=20, yscrollcommand=scrollbar.set)
        self.partition_box.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.partition_box.yview)
        self.size_label = ttk.Label(center_frame, text="Total size: 0 MB | Selected: 0 MB")
        self.size_label.pack(anchor="w", pady=5)

        # Backup Log
        log_frame = ttk.LabelFrame(main_frame, text="Backup Log", padding=5)
        log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10,0))
        self.log_text = Text(log_frame, height=10, wrap="word")
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)
        log_scroll = Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        log_scroll.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=log_scroll.set)

        # Actions
        right_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        right_frame.grid(row=0, column=1, sticky="n", padx=(10,0))
        ttk.Button(right_frame, text="Select Backup Folder", command=self.select_folder, width=25).pack(pady=10)
        ttk.Button(right_frame, text="Start Backup", command=self.start_backup_thread, width=25).pack(pady=10)
        self.folder_label = ttk.Label(right_frame, text="No folder selected", wraplength=180, foreground="gray")
        self.folder_label.pack(pady=5)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        self.partition_box.bind("<<ListboxSelect>>", self.update_selected_size)
        self.redirect_stdout()
        threading.Thread(target=self.load_partitions, daemon=True).start()

    def redirect_stdout(self):
        sys.stdout = StdoutRedirector(self.log_text)
        sys.stderr = StdoutRedirector(self.log_text)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Backup Folder")
        if folder:
            self.output_dir = folder
            self.folder_label.config(text=folder)
            self.root.after(0, lambda: Messagebox.show_info("Output Directory Set", f"Selected: {folder}"))

    def load_partitions(self):
        wait_for_device()
        partitions = list_byname_partitions()
        is_ab = detect_ab_device(partitions)
        suffix = f"_{detect_current_slot()}" if is_ab else ""
        # Merge additional mappings
        for name in ["system","system_ext","vendor","product","odm"]:
            full = f"{name}{suffix}" if is_ab else name
            path = f"/dev/block/mapper/{full}"
            try:
                subprocess.check_call(["adb","shell",f"ls {path}"], stderr=subprocess.DEVNULL)
                partitions[name] = path
            except:
                continue
        self.all_partition_names = sorted(partitions.keys())
        # Incremental insertion
        total = len(self.all_partition_names)
        for idx, name in enumerate(self.all_partition_names, 1):
            path = partitions[name]
            size_mb, _ = get_partition_size(path)
            size_str = format_size(size_mb)
            self.partition_info[name] = (path, size_mb, size_str)
            # Insert into listbox progressively
            self.root.after(0, lambda n=name, p=path, s=size_str: self.partition_box.insert(END, f"{n} -> {p} ({s})"))
            time.sleep(0.05)
        # Update filter to initialize size label
        self.root.after(0, self.filter_partitions)

    def filter_partitions(self, *args):
        term = self.search_var.get().lower()
        self.partition_box.delete(0, END)
        total = 0
        self.filtered_partition_names = []
        for name in self.all_partition_names:
            if term in name.lower():
                path, size_mb, size_str = self.partition_info[name]
                total += size_mb
                self.partition_box.insert(END, f"{name} -> {path} ({size_str})")
                self.filtered_partition_names.append(name)
        self.size_label.config(text=f"Total size: {format_size(total)} | Selected: 0 MB")

    def update_selected_size(self, event=None):
        sel = self.partition_box.curselection()
        total_sel = sum(self.partition_info[self.filtered_partition_names[i]][1] for i in sel)
        total = sum(self.partition_info[n][1] for n in self.filtered_partition_names)
        self.size_label.config(text=f"Total size: {format_size(total)} | Selected: {format_size(total_sel)}")

    def start_backup_thread(self):
        threading.Thread(target=self.start_backup, daemon=True).start()

    def start_backup(self):
        if not self.output_dir:
            self.root.after(0, lambda: Messagebox.show_error("Error","Please select a backup folder first."))
            return
        sel = self.partition_box.curselection()
        if not sel:
            self.root.after(0, lambda: Messagebox.show_error("Error","Select at least one partition to backup."))
            return
        selected = {self.filtered_partition_names[i]: self.partition_info[self.filtered_partition_names[i]][0] for i in sel}
        os.makedirs(self.output_dir, exist_ok=True)
        try:
            backup_partitions(selected, output_dir=self.output_dir)
            self.root.after(0, lambda: Messagebox.show_info("Success","Backup completed successfully!"))
        except Exception as e:
            self.root.after(0, lambda: Messagebox.show_error("Backup Failed",str(e)))

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PartitionBackupGUI(root)
    root.mainloop()

