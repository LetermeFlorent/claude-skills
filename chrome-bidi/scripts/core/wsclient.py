import base64
import contextlib
import os
import socket
import struct
import time
from urllib.parse import urlsplit


class WebSocketError(Exception):
    pass


def apply_mask(payload, key):
    if not payload:
        return payload
    repeated = (key * (len(payload) // 4 + 1))[:len(payload)]
    return (int.from_bytes(payload, "big") ^ int.from_bytes(repeated, "big")).to_bytes(len(payload), "big")


class WebSocket:
    def __init__(self, url, timeout):
        parts = urlsplit(url)
        self.sock = socket.create_connection((parts.hostname, parts.port), timeout=timeout)
        self.buffer = bytearray()
        self.parts = []
        key = base64.b64encode(os.urandom(16)).decode()
        try:
            self.sock.sendall((f"GET {parts.path} HTTP/1.1\r\nHost: {parts.netloc}\r\nUpgrade: websocket\r\n"
                               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                               "Sec-WebSocket-Version: 13\r\n\r\n").encode())
            deadline = time.monotonic() + timeout
            while b"\r\n\r\n" not in self.buffer:
                self.fill(len(self.buffer) + 1, deadline)
            head, _, rest = bytes(self.buffer).partition(b"\r\n\r\n")
            self.buffer = bytearray(rest)
            status = head.split(b"\r\n")[0].decode("latin-1")
            if " 101 " not in status:
                raise WebSocketError(f"handshake refused: {status}")
        except BaseException:
            self.sock.close()
            raise

    def fill(self, count, deadline):
        while len(self.buffer) < count:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError("websocket read timed out")
            self.sock.settimeout(left)
            data = self.sock.recv(1 << 16)
            if not data:
                raise WebSocketError("connection closed by the other side")
            self.buffer += data

    def read_frame(self, deadline):
        self.fill(2, deadline)
        first, length, offset = self.buffer[0], self.buffer[1] & 0x7F, 2
        if length > 125:
            size = 2 if length == 126 else 8
            self.fill(2 + size, deadline)
            length, offset = int.from_bytes(self.buffer[2:2 + size], "big"), 2 + size
        self.fill(offset + length, deadline)
        payload = bytes(self.buffer[offset:offset + length])
        del self.buffer[:offset + length]
        return first & 0x80, first & 0x0F, payload

    def receive(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            try:
                final, opcode, payload = self.read_frame(deadline)
            except (TimeoutError, socket.timeout):
                return None
            if opcode == 9:
                self.send(10, payload)
            elif opcode == 8:
                self.send(8, payload[:2])
                raise WebSocketError("connection closed by the other side")
            elif opcode in (0, 1, 2):
                self.parts.append(payload)
                if final:
                    message, self.parts = b"".join(self.parts), []
                    return message.decode("utf-8", errors="replace")

    def send(self, opcode, payload):
        size = len(payload)
        if size < 126:
            header = struct.pack(">BB", 0x80 | opcode, 0x80 | size)
        elif size < 1 << 16:
            header = struct.pack(">BBH", 0x80 | opcode, 0xFE, size)
        else:
            header = struct.pack(">BBQ", 0x80 | opcode, 0xFF, size)
        key = os.urandom(4)
        self.sock.sendall(header + key + apply_mask(payload, key))

    def close(self):
        with contextlib.suppress(OSError):
            self.send(8, struct.pack(">H", 1000))
        self.sock.close()
