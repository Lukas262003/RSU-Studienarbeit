#!/usr/bin/env python3

import os
import time
import subprocess
import hashlib

WATCH_DIR = "/home/user/obu_bin"
MK5_IP = "192.168.1.10"
PORT = "4040"
PKT_RATE = "5"
NUM_PKTS = "10"

# Speichert letzte Hashwerte der Dateien
last_hashes = {}

def hash_file(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

while True:
    for filename in os.listdir(WATCH_DIR):
        if not filename.endswith(".bin"):
            continue

        full_path = os.path.join(WATCH_DIR, filename)
        if not os.path.isfile(full_path):
            continue

        try:
            new_hash = hash_file(full_path)
        except Exception as e:
            print("Fehler beim Lesen von {}: {}".format(full_path, e))
            continue

        if full_path not in last_hashes or last_hashes[full_path] != new_hash:
            print("Aenderung erkannt an {}, sende...".format(filename))
            subprocess.Popen([
                "python3", "/home/user/send_own_payload.py",
                MK5_IP, PORT, PKT_RATE, NUM_PKTS, full_path
            ])
            last_hashes[full_path] = new_hash

    time.sleep(2)  # alle 5 Sekunden prüfen
