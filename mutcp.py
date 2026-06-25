import sys
import random

SYN = 1
ACK = 2
FIN = 4

def compute_checksum(data):
    if len(data) % 2 == 1:
        data += b'\x00'

    total = 0
    for i in range(0, len(data), 2):
        word = int.from_bytes(data[i:i+2], "big")
        total += word
    # lines 33-37 are to handle the carrying of a bit, which AI helped me with
        while total > 0xFFFF:
            total = (total & 0xFFFF) + (total >> 16)

    checksum = ~total & 0xFFFF
    
    return checksum

def build_packet(seqnum, acknum, flags, payload=b""):
    seqnum_bytes = seqnum.to_bytes(4, "big")
    acknum_bytes = acknum.to_bytes(4, "big")
    flags_bytes = flags.to_bytes(1, "big")
    payload_length = len(payload).to_bytes(3, "big")
    checksum_bytes = (0).to_bytes(2, "big")

    header = seqnum_bytes + acknum_bytes + flags_bytes + payload_length +  checksum_bytes
   
    packet = header + payload

    checksum = compute_checksum(packet)
    checksum_bytes = checksum.to_bytes(2, "big")
    
    header = seqnum_bytes + acknum_bytes + flags_bytes + payload_length +  checksum_bytes
    
    packet = header + payload

    return packet

def parse_packet(packet):
    seqnum = int.from_bytes(packet[0:4], "big")
    acknum = int.from_bytes(packet[4:8], "big")
    flags = packet[8]
    payload_len = int.from_bytes(packet[9:12], "big")
    checksum = int.from_bytes(packet[12:14], "big")
    payload = packet[14:14+payload_len]

    return {
        "seqnum": seqnum,
        "acknum": acknum,
        "flags": flags,
        "length": payload_len,
        "checksum": checksum,
        "payload": payload,
    }

def verify_checksum(packet):
    return compute_checksum(packet) == 0

def unreliable_send(sock, packet, addr, dropprob, biterrprob):

    if random.random() < dropprob:
        print("packet dropped by chance", file=sys.stderr)
        return

    pkt = bytearray(packet)

    for i in range(len(pkt)):

        for bit in range(8):

            if random.random() < biterrprob:

                pkt[i] ^= (1 << bit)

    sock.sendto(bytes(pkt), addr)
