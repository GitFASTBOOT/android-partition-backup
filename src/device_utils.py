import subprocess
import time
from .adb_utils import adb_shell

def wait_for_device():
    print("[*] Waiting for device", end="", flush=True)
    while True:
        try:
            devices = subprocess.check_output(["adb", "devices"], text=True)
            if len(devices.strip().splitlines()) > 1:
                print("\n[✓] Device connected!")
                break
        except subprocess.CalledProcessError:
            pass
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.5)
        print("\b\b\b   \b\b\b", end="", flush=True)

def detect_current_slot():
    try:
        slot = adb_shell("getprop ro.boot.slot_suffix").lstrip('_')
        if slot in ('a', 'b'):
            return slot
    except Exception:
        pass
    return ''

def get_device_info():
    props = {
        "Codename": "ro.product.device",
        "Manufacturer": "ro.product.manufacturer",
        "Model": "ro.product.model",
        "Architecture": "ro.product.cpu.abi"
    }
    info = {}
    for key, prop in props.items():
        try:
            output = adb_shell(f"getprop {prop}")
            info[key] = output
        except:
            info[key] = "Unknown"

    try:
        ab_device = adb_shell("getprop ro.boot.slot_suffix")
        info["Current Slot"] = ab_device.replace("_", "") if ab_device else "Unknown"
        info["Device Type"] = "A/B" if ab_device else "A-only"
    except:
        info["Current Slot"] = "Unknown"
        info["Device Type"] = "Unknown"

    return info
