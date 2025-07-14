from src.device_utils import wait_for_device
from src.partition_utils import list_byname_partitions, detect_ab_device
from src.backup import backup_partitions

def main():
    wait_for_device()

    partitions = list_byname_partitions()
    if not partitions:
        return

    is_ab = detect_ab_device(partitions)
    print(f"[+] Detected partition type: {'A/B' if is_ab else 'A-only'}")

    backup_partitions(partitions)

if __name__ == "__main__":
    main()

