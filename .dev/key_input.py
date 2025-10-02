import sys
import os

def get_key():
    """
    Wartet auf einen Tastendruck und gibt die Taste zurück.
    Funktioniert auf Windows, Linux und Mac.
    """
    if os.name == 'nt':  # Windows
        import msvcrt
        return msvcrt.getch().decode('utf-8', errors='ignore')
    else:  # Linux/Mac
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            taste = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return taste