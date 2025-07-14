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

\`\`\`
android-partition-backup/
├── main.py                # Entry point
├── src/
│   ├── __init__.py
│   ├── adb_utils.py       # adb shell/pull/delete helpers
│   ├── device_utils.py    # ADB device connection wait
│   ├── partition_utils.py # Partition listing and dumping logic
│   └── backup.py          # Partition filtering, pulling, and cleanup
\`\`\`

---

## ⚙️ Requirements

- ✅ Python 3.6+
- ✅ `adb` installed and available in your system's `PATH`
- ⚠️ **Rooted device** (this script uses `su` with `dd`)

---

## 🚀 Usage

1. **Clone the repository**:
   \`\`\`bash
   git clone https://github.com/GitFASTBOOT/android-partition-backup.git
   cd android-partition-backup
   \`\`\`

2. **Run the backup tool**:
   \`\`\`bash
   python3 main.py
   \`\`\`

3. 🎉 Sit back and relax! The tool will:
   - Wait for device connection
   - List available partitions
   - Detect A/B layout (or A-only)
   - Dump partitions via `dd` to `/sdcard`
   - Pull them to your PC inside `android_backup/`
   - Delete temp files from the device

---

## 📦 Output Example

After a successful run, your output will look like:

\`\`\`
android_backup/
├── boot.img
├── vbmeta.img
├── recovery.img
├── system.img
├── ... and more
\`\`\`

---

## 🚫 Exclusions

For safety, the tool **skips** the following by default:
- `userdata` (usually encrypted and very large)
- `mmcblk0` devices (raw blocks)

---

## 🧠 Tips

- Make sure your device is in **ADB mode with root access**.
- Use `adb shell su` to enable root on adb
- You can edit `backup.py` to include or exclude specific partitions.

---

## 🧩 Customization

Want to tweak the tool?
- Change exclusion logic in `src/backup.py`
- Modify partition filtering in `src/partition_utils.py`
- Log to file? Add logging instead of print.
- Convert to a CLI tool with `argparse`? Easy to extend!

---

## 🛡 Disclaimer

> ⚠️ Use this tool responsibly. Backing up and dumping partitions can expose sensitive information.  
> Always test on devices you own or have permission to modify.

---

## 🤝 Contribute

Pull requests and issues are welcome!  
Got a feature request? Open an issue or fork and send a PR.

---

## 💬 Author

Made with ❤️ by [GitFASTBOOT]  
Feel free to reach out or suggest improvements.
