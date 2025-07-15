import subprocess
from src.device_utils import wait_for_device
from src.partition_utils import list_byname_partitions, detect_ab_device

def detect_current_slot():
    """
    Returns the current A/B slot suffix without underscore, e.g. 'a' or 'b'.
    """
    try:
        output = subprocess.check_output([
            "adb", "shell", "getprop ro.boot.slot_suffix"
        ], stderr=subprocess.DEVNULL)
        slot = output.decode().strip()
        # slot_suffix might be '_a' or 'a'
        slot = slot.lstrip('_')
        if slot in ('a', 'b'):
            return slot
    except Exception:
        pass
    return ''


def parse_selection(selection, max_index):
    """
    Parse user selection string into a list of indices.
    Supports comma-separated numbers and ranges (e.g., "1,3-5,7").
    """
    selection = selection.strip().lower()
    if selection in ('all', ''):
        return list(range(1, max_index + 1))

    indices = set()
    for part in selection.replace(' ', '').split(','):
        if '-' in part:
            start, end = part.split('-')
            try:
                start, end = int(start), int(end)
                for i in range(min(start, end), max(start, end) + 1):
                    indices.add(i)
            except ValueError:
                continue
        else:
            try:
                idx = int(part)
                indices.add(idx)
            except ValueError:
                continue
    # Filter only valid indices
    return sorted(i for i in indices if 1 <= i <= max_index)


def main():
    wait_for_device()

    partitions = list_byname_partitions()
    if not partitions:
        print("No partitions found to back up.")
        return

    # Handle dynamic 'super' partition with logical mappings
    if 'super' in partitions:
        print("[+] Detected dynamic partitions (super). Adding logical partitions from /dev/block/mapper...")
        is_ab = detect_ab_device(partitions)
        suffix = ''
        if is_ab:
            slot = detect_current_slot()
            if slot:
                suffix = f"_{slot}"
        for name in ('system', 'vendor', 'product', 'system_ext'):
            partitions[name] = f"/dev/block/mapper/{name}{suffix}"

    is_ab = detect_ab_device(partitions)
    print(f"[+] Detected partition type: {'A/B' if is_ab else 'A-only'}")

    # Present user with partition choices
    print("\nAvailable partitions:")
    names = list(partitions.keys())
    for idx, name in enumerate(names, 1):
        print(f"  {idx}. {name} -> {partitions[name]}")

    selection = input("\nEnter partition numbers to backup (e.g. 1,3-5) or 'all': ")
    nums = parse_selection(selection, len(names))

    if not nums:
        print("No valid selection made. Backing up all partitions.")
        nums = list(range(1, len(names) + 1))

    chosen = [names[i - 1] for i in nums]
    print(f"\nSelected partitions: {', '.join(chosen)}")

    selected_partitions = {name: partitions[name] for name in chosen}

    from src.backup import backup_partitions
    backup_partitions(selected_partitions)

if __name__ == "__main__":
    main()

