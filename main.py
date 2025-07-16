import os
from src.device_utils import wait_for_device, get_device_info, detect_current_slot
from src.partition_utils import list_byname_partitions, detect_ab_device, get_partition_size
from src.backup import backup_partitions
from src.selection_utils import parse_selection

def main():
    wait_for_device()

    # Print Device Info
    print("\n[+] Device Information:")
    info = get_device_info()
    for key, value in info.items():
        print(f"    {key}: {value}")

    partitions = list_byname_partitions()
    if not partitions:
        print("No partitions found to back up.")
        return

    if 'super' in partitions:
        print("[+] Detected dynamic partitions (super). Adding logical partitions from /dev/block/mapper...")
        is_ab = detect_ab_device(partitions)
        suffix = f"_{detect_current_slot()}" if is_ab else ''
        for name in ('system', 'vendor', 'product', 'system_ext'):
            partitions[name] = f"/dev/block/mapper/{name}{suffix}"

    is_ab = detect_ab_device(partitions)
    print(f"[+] Detected partition type: {'A/B' if is_ab else 'A-only'}")

    # Precompute partition sizes
    partition_info = {}
    for name, path in partitions.items():
        size_mb, size_str = get_partition_size(path)
        partition_info[name] = (path, size_mb, size_str)

    print("\nAvailable partitions:")
    names = list(partitions.keys())
    for idx, name in enumerate(names, 1):
        _, _, size_str = partition_info[name]
        print(f"  {idx}. {name} -> {partitions[name]} ({size_str})")

    selection = input("\nEnter partition numbers to backup (e.g. 1,3-5) or 'all': ")
    nums = parse_selection(selection, len(names))

    if not nums:
        print("No valid selection made. Backing up all partitions.")
        nums = list(range(1, len(names) + 1))

    chosen = [names[i - 1] for i in nums]
    print(f"\nSelected partitions: {', '.join(chosen)}")

    selected_partitions = {name: partitions[name] for name in chosen}

    default_dir = os.path.join(os.getcwd(), "android_backup")
    custom_dir = input(f"\nEnter output backup folder path (leave empty to use default: {default_dir}): ").strip()
    output_dir = custom_dir if custom_dir else default_dir

    os.makedirs(output_dir, exist_ok=True)
    backup_partitions(selected_partitions, output_dir=output_dir)

if __name__ == "__main__":
    main()
