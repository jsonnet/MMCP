from typing import Generator


def encode(nibble):  # Input: byte value
    # Input  (d1, d2, d3, d4)
    # Output (p1, p2, d1, p3, d2, d3, d4)

    # Data bits collected
    d = [0] * 4
    d[0] = (nibble >> 3) & 0x01  # d1
    d[1] = (nibble >> 2) & 0x01  # d2
    d[2] = (nibble >> 1) & 0x01  # d3
    d[3] = (nibble >> 0) & 0x01  # d4

    # Hamming bits calculated
    p = [0] * 3
    p[0] = (d[0] + d[1] + d[3]) % 2  # p1
    p[1] = (d[0] + d[2] + d[3]) % 2  # p2
    p[2] = (d[1] + d[2] + d[3]) % 2  # p3

    # Join byte
    code = int(''.join(map(str, [p[0], p[1], d[0], p[2], d[1], d[2], d[3]])), 2)  # 4000 ns improvement
    # code = int(''.join([str(x) for x in [p[0], p[1], d[0], p[2], d[1], d[2], d[3]]]), 2)

    return code


def decode(byte):  # Input: int value
    # Input  (p1, p2, d1, p3, d2, d3, d4, p4)
    # Output (d1, d2, d3, d4)

    # Calculate syndrome
    s = [0] * 3
    # s1 = p1 + d1 + d2 + d4
    # s2 = p2 + d1 + d3 + d4
    # s3 = p3 + d2 + d3 + d4
    s[0] = (((byte >> 6) & 0x01) + ((byte >> 4) & 0x01) + ((byte >> 2) & 0x01) + ((byte >> 0) & 0x01)) % 2
    s[1] = (((byte >> 5) & 0x01) + ((byte >> 4) & 0x01) + ((byte >> 1) & 0x01) + ((byte >> 0) & 0x01)) % 2
    s[2] = (((byte >> 3) & 0x01) + ((byte >> 2) & 0x01) + ((byte >> 1) & 0x01) + ((byte >> 0) & 0x01)) % 2

    # Encode syndrome to more intuitive way (aka binary -> yields pos of error)
    syndrome = (s[2] << 2) | (s[1] << 1) | s[0]

    # if syndrome != 0, correct error by xor at pos with 1 (aka toggle bit)
    if syndrome:
        byte ^= (1 << (7 - syndrome))

    # Return lower nibble
    return ((byte & 0x0f) & -0b1001) | ((((byte >> 4) & 0x01) << 3) & 0b1000)


# python3 -m timeit 'CODE'
interleaved = True


def mm_encode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:
    for byte in source:
        # 25000 ns

        # As we're using Hamming(7,4) byte (8 bits) needs to be divided in half
        ls_nibble = ord(byte) & 0x0f  # Least significant half byte
        ms_nibble = (ord(byte) & 0xf0) >> 4  # Most significant half byte

        # Interleaving
        ls_nibble = str(bin(encode(ls_nibble)))[2:].zfill(7)
        ms_nibble = str(bin(encode(ms_nibble)))[2:].zfill(7)

        if interleaved:
            il = "".join(
                map("".join, zip(ls_nibble[:4], ls_nibble[4:] + ms_nibble[0], ms_nibble[1:5], ms_nibble[5:] + "00")))
        else:
            il = ls_nibble + ms_nibble + "00"

        # Output
        yield (bytes([int(il[:8], 2)]))
        yield (bytes([int(il[8:], 2)]))


def mm_decode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:
    for byte in source:
        # 9000 ns

        # De-interleaving
        tls_nibble = str(bin(ord(byte)))[2:].zfill(8)
        tms_nibble = str(bin(ord(next(source))))[2:].zfill(8)

        if interleaved:
            il = "".join(map("".join, zip(tls_nibble[:4], tls_nibble[4:], tms_nibble[:4], tms_nibble[4:])))
        else:
            il = tls_nibble + tms_nibble

        # Decode Hamming code back to 4 bits
        ls_nibble = decode(int(il[:7], 2))
        ms_nibble = decode(int(il[7:-2], 2))

        # Output
        yield bytes([(ms_nibble << 4) | ls_nibble])
