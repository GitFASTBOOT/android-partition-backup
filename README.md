# 🚀 Android Partition Backup Tool

**Safely dump and backup all Android partitions over ADB with one command!**  
This Python-based tool helps you pull critical partitions from your rooted Android device using `adb` + `dd`, automatically organizing them on your PC.

---

## 🎥 Demo

![Demo GIF](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/test.gif)

## 🖼 Screenshot

![Static Image](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/test.png)

[⬇️ Download test.gif](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/test.gif)  
[⬇️ Download test.png](https://github.com/GitFASTBOOT/android-partition-backup/raw/main/assets/test.png)

---

## 🔧 Features

✅ Fully automated ADB device detection  
✅ Lists partitions dynamically from `/dev/block/by-name`  
✅ Detects A-only and A/B partition schemes  
✅ Dumps partitions using `dd` (requires root access)  
✅ Pulls images from device and cleans up afterward  

---

## 🧠 Why use this?

Whether you're:
- A developer dumping boot, vendor, and system images for modding or analysis,
- A tinkerer creating a fail-safe image set before flashing,
- Or just want fine control over what gets backed up from your device...

**This tool gives you simple, scriptable control with readable Python logic.**

---

## 📁 Project Structure

```bash
android-partition-backup/
├── main.py                # Entry point with interactive selection prompt
├── src/
│   ├── __init__.py
│   ├── adb_utils.py       # adb shell/pull/delete helpers
│   ├── device_utils.py    # ADB device connection wait
│   ├── partition_utils.py # Partition listing logic
│   └── backup.py          # Partition filtering, pulling, and cleanup
``` 

---

## ⚙️ Requirements

- ✅ Python 3.6+
- ✅ `adb` installed and available in your system's `PATH`
- ⚠️ **Rooted device** (this script uses `su` with `dd`)

---

## 🚀 Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GitFASTBOOT/android-partition-backup.git
   cd android-partition-backup
   ```
2. **Run the backup tool**:
   ```bash
   python3 main.py
   ```
3. **Follow the interactive prompts**:
   - The tool will wait for your device and detect A/B or A-only layout.
   - It will list partitions with indices:
     ```
     [+] Detected partition type: A/B

     Available partitions:
       1. super -> /dev/block/bootdevice/by-name/super
       3. boot -> /dev/block/bootdevice/by-name/boot
       4. userdata -> /dev/block/bootdevice/by-name/userdata
     ```
   - **Select partitions**:
     - **Single**: `2` to back up only the vendor partition.
     - **Multiple**: `1,3,4` to select system, boot, and userdata.
     - **Ranges**: `2-4` to back up vendor through userdata.
     - **All**: `all` or press Enter to back up every partition.
   - The script supports parsing comma-separated values and ranges (e.g., `1,3-5,7`).
   - If no valid input is provided, it defaults to backing up all partitions.
4. 🎉 **Backup output**:
   - You’ll see a confirmation:
     ```
     Selected partitions: system, boot, userdata
     ```
   - Images are saved under `android_backup/`:
     ```bash
     android_backup/
     ├── system.img
     ├── boot.img
     ├── userdata.img
     └── ...
     ```

---

## 🚫 Exclusions

By default, the tool **skips**:
- `userdata` (usually encrypted and very large) — unless explicitly selected.
- Raw block devices like `mmcblk0*`.

---

## 🧩 Customization

- Adjust exclusion logic in `src/backup.py`.
- Modify partition filtering in `src/partition_utils.py`.
- Want a non-interactive CLI? Integrate `argparse` for scripted use.

---

## 🛡 Disclaimer

> ⚠️ Use responsibly. Backing up partitions can expose sensitive data. Only run on devices you own or have permission to modify.

---

## 🤝 Contribute

Pull requests and issues are welcome! Fork, tweak, and send a PR with your improvements.

---

## 💬 Author

Made with ❤️ by [GitFASTBOOT]

