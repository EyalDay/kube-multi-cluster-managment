def memory_chunk(size_in_kb):
    l = []
    for i in range(0, int(size_in_kb)):
        l.append("*" * 1024)  # 1KB
    return l