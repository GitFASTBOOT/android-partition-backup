import os
from .adb_utils import adb_pull, adb_delete
from .partition_utils import dump_partition

BACKUP_DIR = "android_backup"

def backup_partitions(partitions, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for name, path in partitions.items():
        lname = name.lower()
        if "userdata" in lname or "mmcblk0" in path:
            continue
        try:
            dumped_file = dump_partition(name, path)
            print(f"[+] Pulling {dumped_file} to PC...")
            local_file = os.path.join(output_dir, os.path.basename(dumped_file))
            adb_pull(dumped_file, local_file)

            print(f"[-] Deleting {dumped_file} from device...")
            adb_delete(dumped_file)
        except Exception as e:
            print(f"[!] Failed to backup {name}: {e}")

    print("\n[✓] Backup completed! Saved to:", output_dir)
