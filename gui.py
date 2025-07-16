import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, Listbox, StringVar, END, MULTIPLE, BOTH, LEFT, RIGHT, Y, X, TclError
import threading
import os
import subprocess
import time
from src.device_utils import wait_for_device, get_device_info, detect_current_slot
from src.partition_utils import list_byname_partitions, detect_ab_device, get_partition_size
from src.backup import backup_partitions

def show_info_safe(title, message):
    try:
        root.after(0, lambda: Messagebox.show_info(title, message))
    except TclError as e:
        print(f"[UI Error] Cannot show info messagebox: {e}")

def show_error_safe(title, message):
    try:
        root.after(0, lambda: Messagebox.show_error(title, message))
    except TclError as e:
        print(f"[UI Error] Cannot show error messagebox: {e}")

class PartitionBackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("\U0001F4E6 Android Partition Backup Tool")
        self.root.geometry("1080x720")
        self.root.resizable(True, True)

        self.output_dir = ""
        self.partition_info = {}  # Stores name: (path, size_mb, size_str)
        self.all_partition_names = []
        self.filtered_partition_names = []
        self.loading = False
        self.loading_progress = 0
        self.total_partitions = 0

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        left_frame = ttk.LabelFrame(main_frame, text="\U0001F4F1 Device Info", padding=10)
        left_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        self.device_info_labels = {}
        for key in ["Codename", "Manufacturer", "Model", "Architecture", "Device Type", "Current Slot"]:
            lbl = ttk.Label(left_frame, text=f"{key}: ---", font=("Segoe UI", 10))
            lbl.pack(anchor="w", pady=3)
            self.device_info_labels[key] = lbl

        center_frame = ttk.Frame(main_frame)
        center_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(center_frame, text="\U0001F50D Search Partitions:").pack(anchor="w")

        self.search_var = StringVar()
        self.search_var.trace("w", self.update_partition_list)
        search_entry = ttk.Entry(center_frame, textvariable=self.search_var, width=40)
        search_entry.pack(fill=X, pady=5)

        partition_frame = ttk.Frame(center_frame)
        partition_frame.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(partition_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.partition_box = Listbox(partition_frame, selectmode=MULTIPLE, width=60, height=20, yscrollcommand=scrollbar.set)
        self.partition_box.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.partition_box.yview)

        # Loading indicator
        self.loading_label = ttk.Label(center_frame, text="Loading partitions...", foreground="gray")
        self.loading_label.pack(anchor="w", pady=5)
        
        self.progress_var = ttk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            center_frame, 
            variable=self.progress_var, 
            maximum=100, 
            mode='determinate',
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill=X, pady=5)
        self.progress_bar.pack_forget()  # Hide initially

        self.size_label = ttk.Label(center_frame, text="Total size: 0 MB | Selected: 0 MB")
        self.size_label.pack(anchor="w", pady=5)

        right_frame = ttk.LabelFrame(main_frame, text="⚙️ Actions", padding=10)
        right_frame.grid(row=0, column=2, sticky="n", padx=(10, 0))

        ttk.Button(right_frame, text="\U0001F4C2 Select Backup Folder", command=self.select_folder, width=25).pack(pady=10)
        ttk.Button(right_frame, text="⬇️ Start Backup", command=self.start_backup_thread, width=25).pack(pady=10)

        self.folder_label = ttk.Label(right_frame, text="No folder selected", wraplength=180, foreground="gray")
        self.folder_label.pack(pady=5)

        self.partition_box.bind("<<ListboxSelect>>", self.update_selected_size)

        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Start loading partitions
        self.start_loading_partitions()

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Backup Folder")
        if folder:
            self.output_dir = folder
            self.folder_label.config(text=folder)
            Messagebox.show_info("Output Directory Set", f"Selected: {folder}")

    def start_loading_partitions(self):
        """Start the partition loading process in a background thread"""
        self.loading = True
        self.loading_label.config(text="Loading partitions...")
        self.progress_bar.pack(fill=X, pady=5)  # Show progress bar
        threading.Thread(target=self.load_partitions).start()

    def update_loading_progress(self, current, total):
        """Update the loading progress indicator"""
        self.loading_progress = current
        self.total_partitions = total
        progress_percent = (current / total) * 100 if total > 0 else 0
        self.progress_var.set(progress_percent)
        self.loading_label.config(
            text=f"Loading partitions... ({current}/{total})"
        )

    def load_partitions(self):
        """Load partitions in the background with incremental updates"""
        try:
            # First get basic device info and partition names
            wait_for_device()
            self.update_device_info()
            
            partitions = list_byname_partitions()
            if not partitions:
                show_error_safe("Error", "No partitions found!")
                return

            # Add required partitions
            required_names = ["system", "system_ext", "vendor", "product", "odm"]
            is_ab = detect_ab_device(partitions)
            suffix = f"_{detect_current_slot()}" if is_ab else ""
            
            for name in required_names:
                full_name = f"{name}{suffix}" if is_ab else name
                path = f"/dev/block/mapper/{full_name}"
                try:
                    subprocess.check_call(["adb", "shell", f"ls {path}"], stderr=subprocess.DEVNULL)
                    partitions[name] = path
                except:
                    continue
            
            # Initialize partition info with placeholders
            self.all_partition_names = sorted(partitions.keys())
            self.partition_info = {
                name: (partitions[name], 0, "Loading...")
                for name in self.all_partition_names
            }
            
            # Update UI with initial list
            self.root.after(0, self.update_partition_list)
            self.root.after(0, self.update_loading_progress, 0, len(self.all_partition_names))
            
            # Now load sizes incrementally
            for i, name in enumerate(self.all_partition_names, 1):
                if not self.loading:  # Check if loading was canceled
                    return
                    
                path = partitions[name]
                size_mb, size_str = get_partition_size(path)
                self.partition_info[name] = (path, size_mb, size_str)
                
                # Update progress every partition
                self.root.after(0, self.update_loading_progress, i, len(self.all_partition_names))
                
                # Update UI with new size
                self.root.after(0, self.update_partition_row, name)
                
                # Small delay to show incremental loading
                time.sleep(0.1)
            
            # Loading complete
            self.root.after(0, self.loading_complete)
            
        except Exception as e:
            show_error_safe("Error", f"Failed to load partitions:\n{e}")
            self.root.after(0, self.loading_complete)

    def loading_complete(self):
        """Handle completion of partition loading"""
        self.loading = False
        self.progress_bar.pack_forget()  # Hide progress bar
        self.loading_label.config(text="Partitions loaded!", foreground="green")
        self.root.after(3000, lambda: self.loading_label.pack_forget())  # Hide after 3 seconds

    def update_device_info(self):
        info = get_device_info()
        for key, lbl in self.device_info_labels.items():
            lbl.config(text=f"{key}: {info.get(key, '---')}")

    def update_partition_list(self, *args):
        """Update the partition list based on search term"""
        search_term = self.search_var.get().lower()
        self.partition_box.delete(0, END)
        
        # Filter partition names based on search term
        self.filtered_partition_names = [
            name for name in self.all_partition_names 
            if search_term in name.lower()
        ]
        
        total_size = 0
        for name in self.filtered_partition_names:
            path, size_mb, size_str = self.partition_info[name]
            total_size += size_mb
            self.partition_box.insert(END, f"{name} -> {path} ({size_str})")
            
        self.size_label.config(text=f"Total size: {total_size:.1f} MB | Selected: 0 MB")

    def update_partition_row(self, name):
        """Update a specific partition row in the listbox"""
        if name not in self.filtered_partition_names:
            return
            
        # Find the index of the partition in the filtered list
        try:
            idx = self.filtered_partition_names.index(name)
        except ValueError:
            return
            
        path, size_mb, size_str = self.partition_info[name]
        new_text = f"{name} -> {path} ({size_str})"
        
        # Update the listbox item
        self.partition_box.delete(idx)
        self.partition_box.insert(idx, new_text)
        
        # Update total size
        total_size = sum(self.partition_info[name][1] for name in self.filtered_partition_names)
        self.size_label.config(text=f"Total size: {total_size:.1f} MB | Selected: 0 MB")

    def update_selected_size(self, event=None):
        total_selected = 0
        selected_indices = self.partition_box.curselection()
        
        for i in selected_indices:
            name = self.filtered_partition_names[i]
            _, size_mb, _ = self.partition_info[name]
            total_selected += size_mb
            
        # Calculate total size for filtered partitions
        total_size = sum(self.partition_info[name][1] for name in self.filtered_partition_names)
            
        self.size_label.config(text=f"Total size: {total_size:.1f} MB | Selected: {total_selected:.1f} MB")

    def start_backup_thread(self):
        threading.Thread(target=self.start_backup).start()

    def start_backup(self):
        if not self.output_dir:
            show_error_safe("Error", "Please select a backup folder first.")
            return

        selected_indices = self.partition_box.curselection()
        if not selected_indices:
            show_error_safe("Error", "Please select at least one partition to backup.")
            return

        selected_partitions = {
            self.filtered_partition_names[i]: self.partition_info[self.filtered_partition_names[i]][0]
            for i in selected_indices
        }

        os.makedirs(self.output_dir, exist_ok=True)
        try:
            backup_partitions(selected_partitions, output_dir=self.output_dir)
            show_info_safe("Success", "Backup completed successfully!")
        except Exception as e:
            show_error_safe("Backup Failed", f"{e}")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PartitionBackupGUI(root)
    root.mainloop()
