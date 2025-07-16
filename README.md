# 🚀 Android Partition Backup Tool

Safely dump and backup all Android partitions over ADB with one command!  
This Python-based tool lets you pull critical partitions from your rooted Android device using `adb` + `dd`, automatically organizing them on your PC.

---

## 🎥 Demo

### 🔹 CLI Demo  
![CLI Demo GIF](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/cli.gif)  
![CLI Demo PNG](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/cli.png)

### 🔹 GUI Demo  
![GUI Demo GIF](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/gui.gif)  
![GUI Demo PNG](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/gui.png)

---

## 🔧 Features

- ✅ Fully automated ADB device detection  
- ✅ Lists partitions dynamically from `/dev/block/by-name` and `/dev/block/mapper`  
- ✅ Detects A-only and A/B partition schemes  
- ✅ Dumps partitions using `dd` (requires root access)  
- ✅ Pulls partition images to your PC and cleans up device afterward  

### 🖥 GUI Features
- Interactive partition selection (checkboxes)  
- Partition search filter  
- Total and selected partition size display  
- Lets you choose the backup directory  
- Dynamically detects common partitions: `system`, `vendor`, `product`, `odm`, `system_ext`  
- Detects and supports A/B slot suffixes  

---

## 🧠 Why use this?

Whether you're:
- A developer dumping boot/vendor/system images for modding or analysis  
- A tinkerer creating a full backup before flashing  
- Someone who wants fine control over what gets backed up...  

This tool gives you simple, scriptable control using clean, readable Python logic.

---

## 📁 Project Structure

```
android-partition-backup/
├── main.py                # CLI mode entry point
├── gui.py                 # GUI app (with ttkbootstrap interface)
├── requirements.txt       # Python dependencies
├── assets/                # Demo GIFs and images
└── src/
    ├── __init__.py
    ├── adb_utils.py       # ADB command helpers
    ├── backup.py          # Partition filtering, pulling, cleanup
    ├── device_utils.py    # ADB device connection
    ├── partition_utils.py # Partition listing logic
    └── selection_utils.py # CLI selection handler
```

---

## 📦 Requirements

### System
- Python 3.8+  
- ADB installed and in your system PATH  
- Rooted Android device with USB debugging enabled  

### Python Packages
- `ttkbootstrap >= 1.10.1`  
- `Pillow >= 10.3.0`  
- `adb-shell >= 0.4.4`  
- `psutil >= 5.9.8`  

Install all with:

```
pip install -r requirements.txt
```

---

## 🚀 Usage

1. **Clone the Repository**  
```bash
git clone https://github.com/GitFASTBOOT/android-partition-backup.git
cd android-partition-backup
```

2. **Install Dependencies**  
```bash
pip install -r requirements.txt
```

3. **Run the Tool**  

**GUI Mode:**  
```bash
python gui.py
```

**CLI Mode:**  
```bash
python main.py
```

---

## 🚫 Exclusions (by default)

- `userdata` — usually encrypted and very large  
- Raw block devices like `mmcblk0*`  

You can always modify the logic if you want to include them.

---

## 🧩 Customization

Want to tweak behavior?
- Edit `src/backup.py` to change exclusion logic  
- Modify `src/partition_utils.py` to customize how partitions are filtered  
- Add `argparse` to `main.py` for fully scripted non-interactive backups  

---

## ⚠️ Safety Notes

- Requires unlocked bootloader and root access  
- Backup files may contain sensitive personal data  
- Skips risky or very large partitions by default for safety  

---

## 🤝 Contribute

Pull requests and issues are welcome!  
Fork the repo, improve the tool, and send a PR.

---

## 💬 Author

Made with ❤️ by [GitFASTBOOT](https://github.com/GitFASTBOOT)
