import os
import random
from tlo_devs_commons.streams import AutoTruncatingChunkedStreamable

# 1:1 copied from scratch.py from initial setup project
# TODO: rework into an actual test

if __name__ == '__main__':
    chunk_size_ = 32
    stream = AutoTruncatingChunkedStreamable(chunk_size_)
    stream_location = b""
    for i in range(9):
        print(f"Start Iteration {i + 1}")
        random_bytes = os.urandom(
            random.randint(30, 35)
        )
        y_n = "not " if len(random_bytes) != chunk_size_ else ""
        print(f"Generated {len(random_bytes)} random bytes, len does {y_n}match")
        stream.write(random_bytes)
        stream_location += stream.read()
