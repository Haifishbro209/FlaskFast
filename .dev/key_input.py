import os
import sys


def get_key() -> str:
    """Wait for a single keypress and return it as a string.
    Works on Windows, Linux and macOS.
    """
    if os.name == "nt":          # Windows
        import msvcrt
        return msvcrt.getch().decode("utf-8", errors="ignore")
    else:                         # Linux / macOS
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch
