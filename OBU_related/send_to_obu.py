import subprocess
import os
import sys

# Dynamische Pfade zum Import von Modulen
sys.path.append(os.path.abspath("Data_files"))

def send_file_to_obu(local_file_path, remote_file_name):
    OBU_IP = "[fe80::6e5:48ff:fe01:93e0]"
    OBU_USER = "user"
    REMOTE_DIR = "/home/user/obu_bin"

    if not os.path.exists(local_file_path):
        print(f"❌ Datei nicht gefunden: {local_file_path}")
        return False

    result = subprocess.run([
        "sshpass", "-p", "user",
        "scp", local_file_path, f"{OBU_USER}@{OBU_IP}:{REMOTE_DIR}/{remote_file_name}"
    ])

    if result.returncode == 0:
        print(f"✅ Datei erfolgreich übertragen: {remote_file_name}")
        return True
    else:
        print("❌ Übertragung fehlgeschlagen.")
        return False
