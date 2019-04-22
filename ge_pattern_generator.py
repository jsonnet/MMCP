import ast
import math
import random
from datetime import datetime


class GilbertElliotPatternGenerator(object):
    def __init__(self, k=1, h=0.1, tau=0.1, seed=0, size_of_pattern=21):
        self.inGoodState = True
        self.rng = random.Random()
        self.rng.seed(seed)
        self.k = k      # good state reliability probability
        self.h = h      # bad state reliability probability
        self.tau = tau  # transition probability
        self.size_of_pattern = size_of_pattern
        self.bit_errors = 0
        self.bytes_processed = 0

    def generate_pattern(self):
        output = bytearray()
        for j in range(2**self.size_of_pattern):
            pattern = 0
            for i in [1, 2, 4, 8, 16, 32, 64, 128]:
                reliability_threshold = self.k if self.inGoodState else self.h
                flipped = self.rng.uniform(0, 1) > reliability_threshold
                if flipped:
                    self.bit_errors += 1
                    pattern += i
                transition = self.rng.uniform(0, 1) < self.tau
                if transition:
                    self.inGoodState = not self.inGoodState
            output.append(pattern)

        return output

    def step(self, bytes_in, pattern_filename):
        pattern_file = open(pattern_filename, 'rb')
        pattern_file.readline()
        pattern_bytes = pattern_file.read()
        pattern_length = len(pattern_bytes)
        i = -1
        for b in bytes_in:
            self.bytes_processed += 1
            i = (i+1) % pattern_length
            current_byte = pattern_bytes[i]
            if current_byte == 0:
                yield b
            else:
                self.bit_errors += bin(current_byte).count("1")
                yield bytes([ord(b) ^ current_byte])

    @staticmethod
    def compress(s):
        last_symbol = s[0]
        j = 0
        output = []
        for i in range(len(s)):
            current_symbol = s[i]
            if current_symbol == last_symbol:
                j += 1
            else:
                output.append((last_symbol, j))
                j = 1
            last_symbol = current_symbol
        output.append((last_symbol, j))
        return output

    @staticmethod
    def uncompress(compressed_list):
        out = bytearray()
        for item in compressed_list:
            for i in range(item[1]):
                out.append(item[0])
        return out


def main():
    start = datetime.now()
    ge = GilbertElliotPatternGenerator(k=1, h=0.99999, tau=0.0001, seed=30, size_of_pattern=21)

    generated_list = ge.generate_pattern()
    f = open("patterns/ge_pattern_" + str(datetime.now().replace(microsecond=0)).replace(":", "-") + ".txt",
             'wb')
    f.write(bytes(ge.bit_errors) + b" errors in " + bytes(2**ge.size_of_pattern) + b"\n")
    f.write(generated_list)

    end = datetime.now()
    duration = (end - start).total_seconds()
    print(f"Duration to generate pattern: {duration}s")


if __name__ == "__main__":
    main()
