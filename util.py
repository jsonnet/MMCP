def read_generator(src):
    f = open(src, "rb")
    byte = f.read(1)
    while byte != b"":
        yield byte
        byte = f.read(1)
    f.close()


def write_to(dst, src):
    with open(dst, "wb") as f:
        for byte in src:
            f.write(byte)


def count_bit_errors(filename_a, filename_b):
    errors = 0
    file_a = read_generator(filename_a)
    file_b = read_generator(filename_b)

    byte_a = next(file_a)
    exhausted_a = False
    byte_b = next(file_b)
    exhausted_b = False
    while not exhausted_a and not exhausted_b:
        if byte_a != byte_b:
            res = ord(byte_a) ^ ord(byte_b)
            errors += bin(res).count("1")
        try:
            byte_a = next(file_a)
        except StopIteration:
            exhausted_a = True

        try:
            byte_b = next(file_b)
        except StopIteration:
            exhausted_b = True

    if not exhausted_a:
        errors += len(list(file_a)) * 8

    if not exhausted_b:
        errors += len(list(file_b)) * 8

    file_a.close()
    file_b.close()
    return errors


def bit_array_to_bit_string(bit_array):
    return ''.join(map(str, bit_array))


def bit_string_to_bit_array(bit_string):
    return map(int, list(bit_string))


def bit_string_to_byte(bit_string):
    return int(bit_string, 2)


def byte_to_bit_string(byte):
    return "{0:08b}".format(byte)
