import socket
from mutcp import *
import random
import sys 

if len(sys.argv) < 4:
    print("enter a port, drop-prob, and biterr-prob", file=sys.stderr)
    sys.exit()

port = int(sys.argv[1])
dropprob = float(sys.argv[2])
biterrprob = float(sys.argv[3])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", port)) 
print("Server listening...", file=sys.stderr)

while True:
    data, addr = sock.recvfrom(4096)

    print("packet received from", addr, file=sys.stderr)

    if not verify_checksum(data):
        print("corrupted packet dropped", file=sys.stderr)
        continue

    pkt = parse_packet(data)

    # print("SEQ:", pkt["seqnum"], file=sys.stderr)
    # print("ACK:", pkt["acknum"], file=sys.stderr)
    # print("FLAGS:", pkt["flags"], file=sys.stderr)
    # print("LEN:", pkt["length"], file=sys.stderr)
    # print("PAYLOAD:", pkt["payload"], file=sys.stderr)
    
    if pkt["flags"] & SYN:
        server_isn = random.getrandbits(32)
        response = build_packet(seqnum=server_isn, acknum=pkt["seqnum"] + 1, flags=SYN | ACK)
        unreliable_send(sock, response, addr, dropprob, biterrprob)
        #sock.sendto(response, addr)
        print("Sent SYN-ACK", file=sys.stderr)
        while True:
            data, addr = sock.recvfrom(4096)
            if verify_checksum(data):
                        break
            print("Corrupted ACK dropped", file=sys.stderr)
        print('Recieved ACK', file=sys.stderr)
        pkt = parse_packet(data)
        
        if pkt["flags"] & ACK and pkt["acknum"] == server_isn + 1:
            print("Handshake complete", file=sys.stderr)

            while True:
                data, addr = sock.recvfrom(4096)
                if verify_checksum(data):
                    break
                print("Corrupted Request", file=sys.stderr)
                
            pkt = parse_packet(data)

            filename = pkt["payload"].decode()
            
            print("Client requested:", filename, file=sys.stderr)
            
            try:
                with open(filename, "rb") as f:
                    print("File opened successfully", file=sys.stderr)

                    seq = 0
                    sock.settimeout(1.0)
                    while True:
                        chunk = f.read(250)

                        if chunk:
                            pkt = build_packet( seqnum=seq, acknum=0, flags=0, payload=chunk)
                            
                            while True:
                                unreliable_send(sock, pkt, addr, dropprob, biterrprob)
                                #sock.sendto(pkt, addr)
                                try:
                                    ack_pkt, _ = sock.recvfrom(4096)
                                except socket.timeout:
                                    print("timeout...", file=sys.stderr)
                                    continue

                                if not verify_checksum(ack_pkt):
                                    print("corrupted packet dropped", file=sys.stderr)
                                    continue

                                parsed = parse_packet(ack_pkt)
                                
                                if parsed["flags"] & ACK and parsed["acknum"] == seq + len(chunk):
                                    break
                            seq += len(chunk)
                        else:
                            fin_pkt = build_packet(seqnum=seq, acknum=0, flags=FIN, payload=b"")
                            
                            #sock.sendto(fin_pkt, addr)
                            unreliable_send(sock, fin_pkt, addr, dropprob, biterrprob)
                            break
                sock.settimeout(None)
            
            except FileNotFoundError:
                print("File not found", file=sys.stderr)
            
                fin_pkt = build_packet(seqnum=0, acknum=0, flags=FIN, payload=b"")
            
                #sock.sendto(fin_pkt, addr)
                unreliable_send(sock, fin_pkt, addr, dropprob, biterrprob)
                break
