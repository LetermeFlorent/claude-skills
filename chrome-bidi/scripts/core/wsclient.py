import base64
import contextlib
import hashlib
import os
import socket
import struct
import time
from urllib.parse import urlsplit

from core.common import ENCODING

ACCEPT_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
CHUNK = 1 << 16
CONTINUATION, TEXT, BINARY, CLOSE, PING, PONG = 0, 1, 2, 8, 9, 10
FIN = 0x80
MASKED = 0x80
NORMAL_CLOSE = 1000
HEAD_END = b"\r\n\r\n"
BYTE_ORDER = "big"
MASK_KEY_SIZE = 4
HANDSHAKE_KEY_SIZE = 16
DEFAULT_PORT = 80
SWITCHING_PROTOCOLS = "101"
HEADER_SIZE = 2
LENGTH_MASK = 0x7F
OPCODE_MASK = 0x0F
LENGTH_16 = 126
LENGTH_64 = 127
SIZE_16 = 2
SIZE_64 = 8
FRAME_16_LIMIT = 1 << 16
CLOSE_CODE_SIZE = 2
CLOSED_BY_PEER = "connection closed by the other side"


class WebSocketError(Exception):
    pass


def apply_mask(payload, key):
    if not payload:
        return payload
    repeated = (key * (len(payload) // MASK_KEY_SIZE + 1))[:len(payload)]
    mixed = int.from_bytes(payload, BYTE_ORDER) ^ int.from_bytes(repeated, BYTE_ORDER)
    return mixed.to_bytes(len(payload), BYTE_ORDER)


class WebSocket:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = bytearray()
        self.parts = []

    @classmethod
    def connect(cls, url, timeout):
        parts = urlsplit(url)
        sock = socket.create_connection((parts.hostname, parts.port or DEFAULT_PORT), timeout=timeout)
        key = base64.b64encode(os.urandom(HANDSHAKE_KEY_SIZE)).decode()
        target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        request = (f"GET {target} HTTP/1.1\r\nHost: {parts.netloc}\r\nUpgrade: websocket\r\n"
                   f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        client = cls(sock)
        try:
            sock.sendall(request.encode("ascii"))
            client.check_handshake(key, time.monotonic() + timeout)
        except BaseException:
            sock.close()
            raise
        return client

    def check_handshake(self, key, deadline):
        while HEAD_END not in self.buffer:
            self.fill(len(self.buffer) + 1, deadline)
        head, _, rest = bytes(self.buffer).partition(HEAD_END)
        self.buffer = bytearray(rest)
        lines = head.decode("latin-1").split("\r\n")
        status = lines[0].split()
        fields = (line.partition(":") for line in lines[1:])
        headers = {name.strip().lower(): value.strip() for name, _, value in fields}
        expected = base64.b64encode(hashlib.sha1((key + ACCEPT_GUID).encode()).digest()).decode()
        if len(status) < 2 or status[1] != SWITCHING_PROTOCOLS:
            raise WebSocketError(f"handshake refused: {lines[0]}")
        if headers.get("sec-websocket-accept") != expected:
            raise WebSocketError("handshake answered with a wrong accept key")

    def fill(self, count, deadline):
        while len(self.buffer) < count:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError("websocket read timed out")
            self.sock.settimeout(left)
            data = self.sock.recv(CHUNK)
            if not data:
                raise WebSocketError(CLOSED_BY_PEER)
            self.buffer += data

    def read_frame(self, deadline):
        self.fill(HEADER_SIZE, deadline)
        first, second = self.buffer[0], self.buffer[1]
        length, offset = second & LENGTH_MASK, HEADER_SIZE
        if length in (LENGTH_16, LENGTH_64):
            size = SIZE_16 if length == LENGTH_16 else SIZE_64
            self.fill(HEADER_SIZE + size, deadline)
            length = int.from_bytes(self.buffer[HEADER_SIZE:HEADER_SIZE + size], BYTE_ORDER)
            offset += size
        key_end = offset + (MASK_KEY_SIZE if second & MASKED else 0)
        self.fill(key_end + length, deadline)
        payload = bytes(self.buffer[key_end:key_end + length])
        if second & MASKED:
            payload = apply_mask(payload, bytes(self.buffer[offset:key_end]))
        del self.buffer[:key_end + length]
        return bool(first & FIN), first & OPCODE_MASK, payload

    def receive(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            try:
                final, opcode, payload = self.read_frame(deadline)
            except (TimeoutError, socket.timeout):
                return None
            if opcode == PING:
                self.send_frame(PONG, payload)
            elif opcode == CLOSE:
                self.send_frame(CLOSE, payload[:CLOSE_CODE_SIZE])
                raise WebSocketError(CLOSED_BY_PEER)
            elif opcode in (CONTINUATION, TEXT, BINARY):
                self.parts.append(payload)
                if final:
                    message, self.parts = b"".join(self.parts), []
                    return message.decode(ENCODING, errors="replace")

    def send_frame(self, opcode, payload):
        size = len(payload)
        if size < LENGTH_16:
            header = struct.pack(">BB", FIN | opcode, MASKED | size)
        elif size < FRAME_16_LIMIT:
            header = struct.pack(">BBH", FIN | opcode, MASKED | LENGTH_16, size)
        else:
            header = struct.pack(">BBQ", FIN | opcode, MASKED | LENGTH_64, size)
        key = os.urandom(MASK_KEY_SIZE)
        self.sock.sendall(header + key + apply_mask(payload, key))

    def send_text(self, text):
        self.send_frame(TEXT, text.encode(ENCODING))

    def close(self):
        with contextlib.suppress(OSError):
            self.send_frame(CLOSE, struct.pack(">H", NORMAL_CLOSE))
        self.sock.close()
