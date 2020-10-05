import threading
from typing import Optional


class AutoTruncatingChunkedStreamable:
    """
    A stream-like class implementing parts of the BytesIO interface.
    Will auto-truncate on write,
    whenever the effective buffer size exceeds chunk_size.

    This keeps the lowest possible memory footprint while still
    simulating a stream that is fully reflected into memory.
    """
    def __init__(self, chunk_size: int) -> None:
        # Public re-entrant lock that can serve as a manual escape-hatch,
        # for shared-resource calls
        self.lock = threading.RLock()
        self._buffer = b""
        self._chunk_size = chunk_size
        # We do bookkeeping for this value because at very large sizes,
        # its cheaper than invoking len(self._buffer)
        self._buffer_size = 0
        # This value exists to simulate a stream that is being traversed
        self._read = 0

    def write(self, data: bytes) -> int:
        if self._buffer_size >= self._chunk_size:
            with self.lock:
                self._buffer = self._buffer[self._chunk_size:]
                self._buffer_size -= self._chunk_size
        data_len = len(data)
        with self.lock:
            self._buffer += data
            del data
            self._buffer_size += data_len
        return data_len

    def read(self,
             chunk_size: int = None,
             *, anon: bool = False) -> Optional[bytes]:
        """
        Reads from the stream and returns one chunk,
        only if there is at least one chunk-length in the buffer.
        """
        chunk_size = chunk_size or self._chunk_size
        if not self._chunk_size == chunk_size:
            raise ValueError(
                "Param chunk_size must be identical to instance._chunk_size\n"
                f"Expected: {self._chunk_size}; Actual: {chunk_size}"
            )
        if chunk_size > self._buffer_size:
            return bytes()
        with self.lock:
            # If we do an anonymous read, do not increment the read counter.
            # Since slicing is non atomic its included in the thread-lock
            if anon:
                return self._buffer[:self._read + chunk_size]
            else:
                self._read += chunk_size
                return self._buffer[:self._read]

    def tell(self) -> int:
        return self._read
