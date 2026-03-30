def format_duration(seconds):
    seconds = int(seconds)
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    
    if h:
        return f"{h}h {m}m {s}s"
    
    return f"{m}m {s}s"