import re
import struct

HEAD_SIZE = 64 * 1024
PNG = b"\x89PNG\r\n\x1a\n"
JPEG = b"\xff\xd8\xff"
GIF = (b"GIF87a", b"GIF89a")
BMP = b"BM"
RIFF, WEBP = b"RIFF", b"WEBP"
SVG = re.compile(rb"<svg[\s>]", re.IGNORECASE)
SVG_SIZE = re.compile(rb'<svg[^>]*?\swidth="(\d+)(?:px)?"[^>]*?\sheight="(\d+)(?:px)?"', re.IGNORECASE | re.DOTALL)
JPEG_FRAMES = set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
JPEG_STANDALONE = set(range(0xD0, 0xDA)) | {0x01}
SIZE_MASK = 0x3FFF
VP8L_SHIFT = 14


def _jpeg_size(data):
    index = 2
    while index + 9 <= len(data):
        if data[index] != 0xFF:
            return None
        marker = data[index + 1]
        if marker in JPEG_STANDALONE or marker == 0xFF:
            index += 1 if marker == 0xFF else 2
            continue
        length = struct.unpack(">H", data[index + 2:index + 4])[0]
        if marker in JPEG_FRAMES:
            height, width = struct.unpack(">HH", data[index + 5:index + 9])
            return width, height
        index += 2 + length
    return None


def _webp_size(data):
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    if chunk == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack("<HH", data[26:30])
        return width & SIZE_MASK, height & SIZE_MASK
    if chunk == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & SIZE_MASK) + 1, ((bits >> VP8L_SHIFT) & SIZE_MASK) + 1
    return None


def _svg_size(data):
    found = SVG_SIZE.search(data)
    return (int(found.group(1)), int(found.group(2))) if found else None


def kind(data):
    if data.startswith(PNG):
        return "png", (struct.unpack(">II", data[16:24]) if len(data) >= 24 else None)
    if data.startswith(JPEG):
        return "jpeg", _jpeg_size(data)
    if data[:6] in GIF:
        return "gif", (struct.unpack("<HH", data[6:10]) if len(data) >= 10 else None)
    if data.startswith(RIFF) and data[8:12] == WEBP:
        return "webp", _webp_size(data)
    if data.startswith(BMP) and len(data) >= 26:
        width, height = struct.unpack("<ii", data[18:26])
        return "bmp", (width, abs(height))
    if SVG.search(data[:2048]):
        return "svg", _svg_size(data)
    return None, None


def probe(path):
    with open(path, "rb") as handle:
        return kind(handle.read(HEAD_SIZE))


def size_text(size):
    return f"{size[0]}x{size[1]}" if size else "size unknown"
