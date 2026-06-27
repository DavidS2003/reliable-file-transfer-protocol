import socket
from mutcp import *
import random
import sys 

if len(sys.argv) < 4:
    print('enter an ip, port, and filename', file=sys.stderr)
    sys.exit()
ip = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#pkt = build_packet( seqnum=0, acknum=0, flags=0, payload=b"hello server")
#sock.sendto(pkt, (ip, port))
client_isn = random.getrandbits(32)
syn_pkt = build_packet(seqnum=client_isn, acknum=0, flags=SYN)

sock.sendto(syn_pkt, (ip, port))
print('Sent SYN', file=sys.stderr)

data, addr = sock.recvfrom(4096)
print("SYN-ACK recieved", file=sys.stderr)

while not verify_checksum(data):
    print("Corrupted packet dropped.", file=sys.stderr)
    data, addr = sock.recvfrom(4096)

pkt = parse_packet(data)

server_isn = pkt["seqnum"]

if pkt["flags"] & SYN and pkt["flags"] & ACK and pkt["acknum"] == client_isn + 1:
    ack_pkt = build_packet(seqnum=client_isn + 1, acknum=server_isn + 1, flags=ACK)
    sock.sendto(ack_pkt, (ip, port))
    print("ACK sent", file=sys.stderr)

filename_bytes = filename.encode()

request_pkt = build_packet(seqnum=0, acknum=0, flags=0, payload=filename_bytes)

sock.sendto(request_pkt, (ip, port))

expected_seq = 0

while True:
    data, _ = sock.recvfrom(4096)

    if not verify_checksum(data):
        print("corrupted packet dropped", file=sys.stderr)
        continue

    pkt = parse_packet(data)

    if pkt["seqnum"] != expected_seq:
        continue

    sys.stdout.buffer.write(pkt["payload"])
    sys.stdout.buffer.flush()

    ack_pkt = build_packet(seqnum=0, acknum=pkt["seqnum"] + len(pkt["payload"]), flags=ACK)

    sock.sendto(ack_pkt, (ip, port))

    expected_seq += len(pkt["payload"])

    if pkt["flags"] & FIN:
        break

