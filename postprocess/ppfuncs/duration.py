def _get_duration_string(sig):
    words = sig.split()
    for i in range(len(words)):
        if words[i] == 'for':
            return ' '.join(words[i:])
    return None

