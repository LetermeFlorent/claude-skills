import struct

SOF = set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
PNG, RIFF, WEBP, JPEG = bytes.fromhex("89504e470d0a1a0a"), b"RIFF", b"WEBP", bytes.fromhex("ffd8")
HEADER_BYTES = 262_144
SHORTS_LE, INTS_BE, LITTLE = "<HH", ">II", "little"


def _jpeg(head):
    index = len(JPEG)
    while index + 9 < len(head):
        if head[index] != 0xFF:
            index += 1
        elif head[index + 1] in SOF:
            height, width = struct.unpack(">HH", head[index + 5:index + 9])
            return width, height
        else:
            index += 2 + struct.unpack(">H", head[index + 2:index + 4])[0]
    return None


def _webp(head):
    chunk = head[12:16]
    if chunk == b"VP8X":
        return int.from_bytes(head[24:27], LITTLE) + 1, int.from_bytes(head[27:30], LITTLE) + 1
    if chunk == b"VP8L":
        bits = int.from_bytes(head[21:25], LITTLE)
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    width, height = struct.unpack(SHORTS_LE, head[26:30])
    return width & 0x3FFF, height & 0x3FFF


def dimensions(path):
    try:
        with open(path, "rb") as handle:
            head = handle.read(HEADER_BYTES)
        if head.startswith(PNG):
            return struct.unpack(INTS_BE, head[16:24])
        if head[:3] == b"GIF":
            return struct.unpack(SHORTS_LE, head[6:10])
        if head[:2] == b"BM":
            width, height = struct.unpack("<ii", head[18:26])
            return width, abs(height)
        if head[:4] == RIFF and head[8:12] == WEBP:
            return _webp(head)
        if head.startswith(JPEG):
            return _jpeg(head)
        box = head.find(b"ispe")
        return struct.unpack(INTS_BE, head[box + 8:box + 16]) if box > 0 else None
    except (OSError, struct.error):
        return None
