#!/bin/bash

# Netzwerk konfigurieren
ifconfig eth0 192.168.1.10 netmask 255.255.255.0 up

# chconfig Setup
chconfig -s -w CCH -i wave-raw -c 168 -r a -e 0x88B6 -a 3

# test-tx starten (z. B. im Hintergrund, falls es dauerhaft läuft)
test-tx -c 168 -t -z 4040 &

# Python-Skript starten
python3 /home/user/watch_and_send_polling.py
