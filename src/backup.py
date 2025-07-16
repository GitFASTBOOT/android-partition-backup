import os
import subprocess
import time

BACKUP_DIR = "android_backup"
DEFAULT_SPEED_MBPS = 40  # assumed transfer speed in MB/s

def get_all_partitions():
    print("Fetching all partitions from /dev/block/by-name...")
    result = subprocess.run(
        ["adb", "shell", "su -c 'ls -l /dev/block/by-name'"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Failed to fetch partition list:", result.stderr)
        return {}

    partitions = {}
    for line in result.stdout.splitlines():
        if "->" in line:
            parts = line.strip().split()
            name = parts[-3]
            target = parts[-1]
            full_path = f"/dev/block/{target}"
            partitions[name] = full_path

    partitions['mmcblk0'] = '/dev/block/mmcblk0'
    partitions['partitions'] = '/dev/block/mapper/partitions'
    return partitions

def get_partition_size(path):
    """Return size in bytes of the partition at given path"""
    result = subprocess.run(
        ["adb", "shell", f"su -c 'blockdev --getsize64 {path}'"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except:
        return None

def human_readable_size(bytes_size):
    if bytes_size >= 1 << 30:
        return f"{bytes_size / (1 << 30):.2f} GB"
    elif bytes_size >= 1 << 20:
        return f"{bytes_size / (1 << 20):.2f} MB"
    else:
        return f"{bytes_size / (1 << 10):.2f} KB"

def estimate_time(size_bytes, speed_mbps=DEFAULT_SPEED_MBPS):
    return size_bytes / (speed_mbps * 1024 * 1024)

def backup_partitions(partitions, output_dir=BACKUP_DIR):
    os.makedirs(output_dir, exist_ok=True)

    for name, path in partitions.items():
        output_file = os.path.join(output_dir, f"{name}.img")
        print(f"\nBacking up {name} ({path})")

        size_bytes = get_partition_size(path)
        if size_bytes:
            size_hr = human_readable_size(size_bytes)
            eta = estimate_time(size_bytes)
            print(f" - Estimated size: {size_hr}")
            print(f" - Estimated time: {eta:.1f} seconds (at {DEFAULT_SPEED_MBPS} MB/s)")
        else:
            print(" - Could not determine partition size.")

        cmd = [
            "adb", "exec-out",
            f"su -c 'dd if={path} bs=4M'"
        ]

        try:
            with open(output_file, 'wb') as f:
                start_time = time.time()
                proc = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    shell=False,
                )
                _, err = proc.communicate()
                elapsed = time.time() - start_time

                if proc.returncode != 0:
                    print(f"Error backing up {name}: {err.decode().strip()}")
                else:
                    print(f"Successfully backed up {name} in {elapsed:.1f} seconds.")

        except Exception as e:
            print(f"Exception during backup of {name}: {e}")

if __name__ == '__main__':
    partitions = get_all_partitions()
    if partitions:
        backup_partitions(partitions)
    else:
        print("No partitions found. Make sure your device is connected and rooted.")

