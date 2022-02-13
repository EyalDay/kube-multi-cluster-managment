import math

def memory_chunk(size_in_kb):
    l = []
    for i in range(0, math.ceil(size_in_kb)):
        l.append("*" * 1024)  # 1KB
    return l