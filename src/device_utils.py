import subprocess
import time

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

