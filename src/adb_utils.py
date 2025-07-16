import subprocess

def adb_shell(command):
    return subprocess.check_output(
        ['adb', 'shell', command],
        stderr=subprocess.DEVNULL, 
        text=True
    ).strip()

def adb_pull(src, dest):
    subprocess.run(['adb', 'pull', src, dest], check=True)

def adb_delete(path):
    subprocess.run(['adb', 'shell', f'rm -f {path}'], check=True)
