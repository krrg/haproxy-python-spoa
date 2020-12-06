import ctypes
import ipaddress
import io


class SpopDataTypes:
    NULL = 0
    BOOL = 1
    INT32 = 2
    UINT32 = 3
    INT64 = 4
    UINT64 = 5
    IPV4 = 6
    IPV6 = 7
    STRING = 8
    BINARY = 9



SINGLE_BYTE_MAX = 0xF0
MIDDLE_BYTE_MASK = 0x80
TERMINAL_BYTE_MASK = 0x00


def __is_middle_byte(byte: int) -> bool:
    return byte > MIDDLE_BYTE_MASK


def parse_varint(buffer: io.BytesIO) -> int:
    head = buffer.read(1)[0]

    print("Raw head byte", hex(head))

    if head < SINGLE_BYTE_MAX:
        return head

    shift = 4
    actual_value = head
    while True:
        next_byte = buffer.read(1)[0]
        actual_value += next_byte << shift
        shift += 7

        if next_byte < MIDDLE_BYTE_MASK:
            return actual_value


def parse_int32(buffer: io.BytesIO) -> int:
    return ctypes.c_int32(
        parse_varint(buffer)
    ).value


def parse_int64(buffer: io.BytesIO) -> int:
    return ctypes.c_int64(
        parse_varint(buffer)
    ).value


def parse_uint32(buffer: io.BytesIO) -> int:
    return ctypes.c_uint32(
        parse_varint(buffer)
    ).value


def parse_uint64(buffer: io.BytesIO) -> int:
    return ctypes.c_uint64(
        parse_varint(buffer)
    ).value


def parse_ipv4(buffer: io.BytesIO) -> ipaddress.IPv4Address:
    ipv4_struct = buffer.read(4)
    return ipaddress.IPv4Address(ipv4_struct)


def parse_ipv6(buffer: io.BytesIO) -> ipaddress.IPv6Address:
    ipv6_struct = buffer.read(16)
    return ipaddress.IPv6Address(ipv6_struct)


def parse_binary(buffer: io.BytesIO) -> bytes:
    bytes_length = parse_varint(buffer)
    return buffer.read(bytes_length)


def parse_string(buffer: io.BytesIO) -> str:
    _bytes = parse_binary(buffer)
    # The actual encoding is not well documented, but other agents have used ASCII.
    # Based on some offhand remarks in an Haproxy blog post, this seems probable.
    return _bytes.decode("ascii")


def parse_typed_data(buffer: io.BytesIO):
    type_flags = buffer.read(1)[0]

    # The order of the octets is backwards from what the documentation says,
    #  but this is how Haproxy _actually_ behaves.
    type = type_flags & 0x0F
    flags = (type_flags & 0xF0) >> 4

    if type == SpopDataTypes.NULL:
        return None
    elif type == SpopDataTypes.BOOL:
        return bool(flags & 0b1000)
    elif type == SpopDataTypes.INT32:
        return parse_int32(buffer)
    elif type == SpopDataTypes.UINT32:
        return parse_uint32(buffer)
    elif type == SpopDataTypes.INT64:
        return parse_int64(buffer)
    elif type == SpopDataTypes.UINT64:
        return parse_uint64(buffer)
    elif type == SpopDataTypes.IPV4:
        return parse_ipv4(buffer)
    elif type == SpopDataTypes.IPV6:
        return parse_ipv6(buffer)
    elif type == SpopDataTypes.STRING:
        return parse_string(buffer)
    elif type == SpopDataTypes.BINARY:
        return parse_binary(buffer)
    else:
        raise ValueError(f"Data type `{type}` is unknown, your copy of Haproxy is likely counterfeit ( ͡° ͜ʖ ͡° )")


def write_varint(value: int) -> bytes:
    byte_conv_params = {
        "byteorder": "little",
        "signed": False,
    }

    if value < SINGLE_BYTE_MAX:
        return value.to_bytes(1, **byte_conv_params)

    byte_list = []

    header_byte = (value | SINGLE_BYTE_MAX).to_bytes(1, **byte_conv_params)[0]
    byte_list.append(header_byte)
    value = (value - SINGLE_BYTE_MAX) >> 4

    while value >= MIDDLE_BYTE_MASK:
        middle_byte = (value | MIDDLE_BYTE_MASK).to_bytes(1, **byte_conv_params)[0]
        byte_list.append(middle_byte)
        value = (value - MIDDLE_BYTE_MASK) >> 7

    terminal_byte = value.to_bytes(1, **byte_conv_params)[0]
    byte_list.append(terminal_byte)

    return bytes(byte_list)


def write_binary(value: bytes) -> bytes:
    length_bytes = write_varint(len(value))
    return length_bytes + value


def write_string(value: str) -> bytes:
    return write_binary(value.encode("ascii"))

