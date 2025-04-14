#!/usr/bin/env python3

import time
import socket
import sys
import os

def PrintUsage(ProgramName):
    print("""
    Usage: {} <Addr> <Port> <PktRate> <NumPkts> <BinFile>
      <Addr>     = IP address of the MK5 (e.g. 127.0.0.1)
      <Port>     = UDP port (e.g. 4040)
      <PktRate>  = Packets per second to send
      <NumPkts>  = Total packets to send (-1 = infinite)
      <BinFile>  = Path to binary file used as payload source
    """.format(ProgramName))

def main(addr, port, pkt_rate, num_pkts, bin_file):
    with open(bin_file, "rb") as f:
        payload_data = f.read()

    payload_len = len(payload_data)
    pkt_len = payload_len + 27  # add 27 bytes for overwritten header space

    if pkt_len < 62:
        print("WARNING: Payload is too short. Padding to 62 bytes.")
        pkt_len = 62

    print("Calculated PktLen: {}".format(pkt_len))

    PktPeriod = 1.0 / pkt_rate
    txsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    txsock.bind(('', 50000))
    txsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    Target = (addr, port)

    log = open("txlog.txt", "w")
    log.write("# SeqNum Payload\n")

    pkt_count = 0

    try:
        while pkt_count < num_pkts or num_pkts == -1:
            pktbuf = bytearray()
            pktbuf += b"\x00" * 27  # placeholder for test-tx header

            chunk = payload_data[:pkt_len - 27]
            if len(chunk) < (pkt_len - 27):
                chunk += b"\x00" * (pkt_len - 27 - len(chunk))  # pad with nulls

            pktbuf += chunk

            txsock.sendto(pktbuf, Target)
            log.write("{:08d} {}\n".format(pkt_count, "".join("{:02x}".format(b) for b in chunk)))

            pkt_count += 1
            time.sleep(PktPeriod)

        log.close()
        txsock.close()
        print("Transmitted {} packets.".format(pkt_count))

    except KeyboardInterrupt:
        print("Stopped by user.")
        log.close()
        txsock.close()

if __name__ == '__main__':
    if len(sys.argv) != 6:
        PrintUsage(sys.argv[0])
        sys.exit(1)

    addr = sys.argv[1]
    port = int(sys.argv[2])
    pkt_rate = int(sys.argv[3])
    num_pkts = int(sys.argv[4])
    bin_file = sys.argv[5]

    main(addr, port, pkt_rate, num_pkts, bin_file)
