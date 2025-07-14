from .adb_utils import adb_shell

def list_byname_partitions():
    print("[*] Listing /dev/block/by-name...")
    try:
        listing = adb_shell("ls -l /dev/block/by-name")
        partitions = {}
        for line in listing.splitlines():
            parts = line.split()
            if len(parts) >= 9:
                name = parts[-3]
                full_path = "/dev/block/by-name/" + name
                partitions[name] = full_path
        return partitions
    except Exception:
        print("[-] Failed to list /dev/block/by-name")
        return {}

def detect_ab_device(partitions):
    uses_a = any(name.endswith("_a") for name in partitions.keys())
    uses_b = any(name.endswith("_b") for name in partitions.keys())
    return uses_a and uses_b

def dump_partition(part_name, full_path):
    output_file = f"/sdcard/{part_name}.img"
    print(f"[*] Dumping {part_name} → {output_file}")
    adb_shell(f"su -c 'dd if={full_path} of={output_file}'")
    return output_file

