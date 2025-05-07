# RSU-Studienarbeit
Dieses Repo dient dem Versenden von Nachrichten über DSRC IEEE 802.11p mit einer MK5 OBU.
Über ein Dashboard kann das Verhalten gesteuert werden


Wenn statt einem Linux-System unter Windows gearbeitet wird müssen folgende Dinge angepasst werden:
- Im File "send_to_obu.py" muss Zeile 18 "sshpass" auskommentiert werden, dieser Befehl funktioniert unter Windows nicht, bei Linux Systemen muss dieser über die Command-Line des Systems hinzugefügt werden
