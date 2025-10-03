CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PADCHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
BASE = len(CHARS)
MIN_LENGTH = 8

def encode(n):
    s = ""
    while n > 0:
        s += CHARS[n % BASE]
        n //= BASE
    s = s[::-1]

    real_len = len(s)

    # encode real_len as a single character (assumes len(s) < 64)
    len_char = CHARS[real_len]

    padding = ""
    fake_seed = id(s)
    while len(s) + len(padding) < MIN_LENGTH:
        fake_seed = (fake_seed * 31 + 7) % (10**9)
        padding += PADCHARS[fake_seed % len(PADCHARS)]

    return len_char + s + padding  # prepend length

def decode(s):
    real_len = CHARS.index(s[0])  # decode length from first char
    trimmed = s[1:1 + real_len]
    n = 0
    for c in trimmed:
        n = n * BASE + CHARS.index(c)
    return n

# Test
if __name__ == "__main__":
    original = 45
    coded = encode(original)
    decoded = decode(coded)

    print(f"Coded: {coded}")
    print(f"Decoded: {decoded}")
