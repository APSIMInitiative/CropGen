import os
import psutil

class MemoryUsageTracker:
    def __init__(self):
        self.last_mem_mb = 0.0
        self.current_mem_mb = 0.0
        self.mem_change_mb = 0.0

    def capture_memory_usage_snapshot(self):
        self.last_mem_mb = self.current_mem_mb
        
        # Capture the current memory usage using psutil
        process = psutil.Process(os.getpid())
        mem_bytes = process.memory_info().rss

        self.current_mem_mb = self._convert_bytes_to_mb(mem_bytes)
        self.mem_change_mb = self.current_mem_mb - self.last_mem_mb

    def __str__(self):
        return (f"MemoryUsageTracker - CurrentMemMB: {self.current_mem_mb:.2f} MB, "
                f"LastMemMB: {self.last_mem_mb:.2f} MB, "
                f"MemChangeMB: {self.mem_change_mb:.2f} MB")

    @staticmethod
    def _convert_bytes_to_mb(mem_bytes):
        return mem_bytes / (1024.0 * 1024.0)