# Reliable File Transfer Protocol

A custom reliable file transfer protocol built in Python using UDP sockets. The project implements core TCP reliability mechanisms including a three-way handshake, sequence numbers, acknowledgments, checksums, retransmissions, and connection teardown.

The protocol transfers files between a client and server while handling packet loss and bit-level corruption.

---

## Features

* UDP-based file transfer
* Three-way connection handshake
* Sequence number tracking
* Acknowledgment packets
* Internet checksum validation
* Packet loss simulation
* Bit-error simulation
* Stop-and-wait retransmission protocol
* Timeout-based packet recovery
* Reliable delivery of text and binary files
* FIN-based connection termination

---

## Technologies

* Python
* UDP Sockets
* TCP/IP Concepts
* Reliable Transport Protocols
* Checksums
* Sequence Numbers
* File Transfer

---

## Architecture

```text
Client
   │
   │ SYN
   ▼
Server
   │
   │ SYN-ACK
   ▼
Client
   │
   │ ACK
   ▼
Connection Established

Client Request
   │
   ▼
File Transfer

Data Packet
   │
   ▼
ACK

Data Packet
   │
   ▼
ACK

...

FIN Packet
```

---

## Protocol Header Format

Each packet contains a custom 14-byte header:

| Field                 | Size    |
| --------------------- | ------- |
| Sequence Number       | 4 bytes |
| Acknowledgment Number | 4 bytes |
| Flags                 | 1 byte  |
| Payload Length        | 3 bytes |
| Checksum              | 2 bytes |

Supported flags:

* SYN
* ACK
* FIN

---

## Reliability Mechanisms

The protocol implements:

### Three-Way Handshake

1. Client sends SYN
2. Server replies with SYN-ACK
3. Client replies with ACK

### Error Detection

Packets are protected using an Internet checksum.

Corrupted packets are discarded and retransmitted.

### Packet Loss Recovery

The server uses timeout-based retransmission.

If an acknowledgment is not received within one second, the packet is resent.

### Ordered Delivery

Sequence numbers ensure packets are processed in the correct order.

Unexpected packets are discarded.

---

## Running the Server

```bash
python mutcps.py PORT DROPPROB BITERRPROB
```

Example:

```bash
python mutcps.py 5000 0.10 0.01
```

---

## Running the Client

Display file contents:

```bash
python mutcpc.py 127.0.0.1 5000 example.txt
```

Save output to disk:

```bash
python mutcpc.py 127.0.0.1 5000 image.jpg > image.jpg
```

---

## Example Features Demonstrated

* Reliable file transfer over UDP
* Packet retransmission
* Packet corruption detection
* Simulated network unreliability
* Custom transport protocol implementation

---

## Future Improvements

* Sliding window protocol
* Selective acknowledgments
* Congestion control
* Flow control
* Multi-client support
* Full TCP-style connection teardown

---

## Screenshots

### Three-Way Handshake

(Add screenshot)

### Successful File Transfer

(Add screenshot)

### Packet Loss and Retransmission

(Add screenshot)

### Bit Error Detection

(Add screenshot)
