import os
from datetime import datetime

from mm_codecs import mm_encode, mm_decode
from ge_pattern_generator import GilbertElliotPatternGenerator
from util import read_generator, write_to, count_bit_errors


class EvaluationRun(object):
    def __init__(self, seed=0, pattern=""):
        self.seed = seed
        self.pattern = pattern
        self.ge = GilbertElliotPatternGenerator(1, 0.99999, 0.1, seed=seed)
        self.result_bit_errors = 0
        self.redundancy = 1
        self.ideal_redundancy = 0
        self.duration = 0
        self.error_ratio = 0

    def run(self):
        src_file = "./resources/original.mp4"
        dst_file = "./resources/received_{}.mp4".format(self.pattern.replace(".txt", ""))

        size = os.path.getsize(src_file)

        start = datetime.now()
        stream_src = read_generator(src_file)
        stream_enc = mm_encode(stream_src)
        stream_tx = self.ge.step(stream_enc, "patterns/" + self.pattern)
        stream_dec = mm_decode(stream_tx)
        write_to(dst_file, stream_dec)
        stop = datetime.now()
        self.duration = (stop - start).total_seconds()

        self.result_bit_errors = count_bit_errors(src_file, dst_file)
        self.error_ratio = (float(self.result_bit_errors) / self.ge.bit_errors)

        self.redundancy = (float(self.ge.bytes_processed) / size - 1)

        ge_error_rate = float(self.ge.bit_errors) / (self.ge.bytes_processed * 8)
        self.ideal_redundancy = 1 / (1 - ge_error_rate) - 1

    def __str__(self):
        return "%8d / %6d = %s | %s / %s | %6ds | %s" % (self.result_bit_errors, self.ge.bit_errors,
                                                         "{:8.2f}%".format(self.error_ratio * 100),
                                                         "{:10.2e}".format(self.redundancy),
                                                         "{:16.2e}".format(self.ideal_redundancy),
                                                         self.duration,
                                                         self.pattern)


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    pattern_files = sorted([f for f in os.listdir(os.path.join(dir_path, "patterns"))])

    print("Residual / Errors = Ratio     | Measured   / Ideal Redundancy | Runtime | Pattern")
    for pattern in pattern_files:
        r = EvaluationRun(pattern=pattern)
        r.run()
        print(r)


if __name__ == "__main__":
    main()
