import os
import platform
import shutil
import ctypes
import textwrap
import argparse
import json
import re


RESET = "\033[0m"
BOLD = "\033[1m"

PURPLE = "\033[38;5;141m"
CYAN = "\033[38;5;51m"
BLUE = "\033[38;5;75m"
WHITE = "\033[97m"
GRAY = "\033[38;5;245m"
GREEN = "\033[38;5;120m"
YELLOW = "\033[38;5;221m"
RED = "\033[38;5;203m"
ORANGE = "\033[38;5;215m"
MAGENTA = "\033[38;5;213m"

THEME_COLORS = {
    "purple": PURPLE,
    "cyan": CYAN,
    "blue": BLUE,
    "green": GREEN,
    "yellow": YELLOW,
    "red": RED,
    "orange": ORANGE,
    "magenta": MAGENTA,
    "white": WHITE,
    "gray": GRAY,
}


def color(text, code):
    return f"{code}{text}{RESET}"


def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".pyfetchrc.json")


def load_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)


def get_memory():
    if os.path.exists("/proc/meminfo"):
        memory = {}

        with open("/proc/meminfo", encoding="utf-8") as file:
            for line in file:
                key, value = line.split(":", 1)
                memory[key] = int(value.strip().split()[0])

        total = memory.get("MemTotal", 0) / 1024**2
        available = memory.get("MemAvailable", 0) / 1024**2
        used = total - available

        return used, total, available

    if platform.system() == "Windows":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("memory_load", ctypes.c_ulong),
                ("total_phys", ctypes.c_ulonglong),
                ("avail_phys", ctypes.c_ulonglong),
                ("total_page", ctypes.c_ulonglong),
                ("avail_page", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong),
                ("avail_virtual", ctypes.c_ulonglong),
                ("avail_extended", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)

        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            total = status.total_phys / 1024**3
            available = status.avail_phys / 1024**3
            used = total - available

            return used, total, available

    return None, None, None


def get_cpu_name():
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as file:
                for line in file:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass

    return platform.processor() or "Unknown CPU"


def get_cpu_frequency():
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as file:
                for line in file:
                    if line.lower().startswith("cpu mhz"):
                        mhz = float(line.split(":", 1)[1].strip())
                        return f"{mhz / 1000:.2f} GHz"
        except (OSError, ValueError):
            pass

    return "Unavailable"


def get_distro_id():
    if platform.system() != "Linux":
        return platform.system().lower()

    try:
        with open("/etc/os-release", encoding="utf-8") as file:
            data = {}
            for line in file:
                if "=" in line:
                    key, _, value = line.strip().partition("=")
                    data[key] = value.strip().strip('"')
            return data.get("ID", "linux").lower()
    except OSError:
        return "linux"


def get_os_name():
    if platform.system() == "Linux":
        try:
            with open("/etc/os-release", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except OSError:
            pass

    return f"{platform.system()} {platform.release()}"


def get_storage():
    try:
        path = os.path.expanduser("~")
        disk = shutil.disk_usage(path)

        total = disk.total / 1024**3
        percent = (disk.used / disk.total) * 100

        return total, percent

    except OSError:
        return None, None


def get_uptime():
    try:
        if platform.system() == "Linux":
            with open("/proc/uptime", encoding="utf-8") as file:
                seconds = float(file.read().split()[0])

        elif platform.system() == "Windows":
            seconds = ctypes.windll.kernel32.GetTickCount64() / 1000

        else:
            return "Unavailable"

        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours or days:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")

        return " ".join(parts)

    except (OSError, ValueError):
        return "Unavailable"


def make_bar(percent, length=20):
    if percent is None:
        return "Unavailable"

    filled = max(0, min(length, int(length * percent / 100)))

    if percent >= 85:
        bar_color = RED
    elif percent >= 60:
        bar_color = YELLOW
    else:
        bar_color = GREEN

    bar = "#" * filled + "-" * (length - filled)
    return f"[{color(bar, bar_color)}] {percent:.1f}%"


def logo_linux():
    art = """
        .--.
       |o_o |
       |:_/ |
      //   \\ \\
     (|     | )
    /'\\_   _/`\\
    \\___)=(___/
      /     \\
     (_)   (_)
""".strip("\n").splitlines()
    return [color(line, WHITE) for line in art]


def logo_ubuntu():
    art = """
             .-/+oo+/-.
         -+sssssssssss+-
       .ossssssssssssssso.
      /ssssshdmmmhyssssss/
     +ssshdMMMMMMMMmhsssss+
    /sshNMMNyyyyyyyNMMNhss/
   .ssdMMMNsssssssshNMMMds.
   +shNMMNysssssssssyNMMNhs+
   .ssdMMMNsssssssshNMMMds.
    /sshNMMNyyyyyyyNMMNhss/
     +ssshdMMMMMMMMmhsssss+
      /ssssshdmmmhyssssss/
       .ossssssssssssssso.
         -+sssssssssss+-
             .-/+oo+/-.
""".strip("\n").splitlines()
    return [color(line, ORANGE) for line in art]


def logo_arch():
    art = """
                    /\\
                   /  \\
                  /    \\
                 /      \\
                /        \\
               /    /\\    \\
              /    /  \\    \\
             /    /    \\    \\
            /    /      \\    \\
           /  ,,/        \\,,  \\
          /_-''            ''-_\\
""".strip("\n").splitlines()
    return [color(line, CYAN) for line in art]


def logo_debian():
    art = """
        .--~~~--.
      .'  @@@@@  '.
     /   @@@@@@@   \\
    |   @@@  @@@@   |
    |  @@@      @@  |
    |   @@  **  @@  |
     \\   @@ ** @@  /
      '.  @@@@@  .'
        '--___--'
          '--.__
""".strip("\n").splitlines()
    return [color(line, RED) for line in art]


def logo_fedora():
    art = """
        _______
      /         \\
     |   _____   |
     |  | f   |  |
     |  | |___|  |
     |  | |      |
      \\ |_|      /
       \\_________/
""".strip("\n").splitlines()
    return [color(line, BLUE) for line in art]


def logo_mint():
    art = """
 ___________________
|  _______________  |
| |               | |
| |  _   |   _    | |
| | | |  |  | |   | |
| | |_|  |  |_|   | |
| |_______________| |
|___________________|
""".strip("\n").splitlines()
    return [color(line, GREEN) for line in art]


def logo_windows():
    block = "##########"
    gap = "  "
    lines = []
    for _ in range(4):
        lines.append(color(block, RED) + gap + color(block, GREEN))
    lines.append("")
    for _ in range(4):
        lines.append(color(block, BLUE) + gap + color(block, YELLOW))
    return lines


def logo_macos():
    art = """
          ,  ,
           \\/
         .-""-.
        /      \\
       |        |
       |        )
        \\      /
         '-..-'
""".strip("\n").splitlines()
    return [color(line, WHITE) for line in art]


def logo_opensuse():
    art = """
          ____
       .-'    '-.
      /   .--.    \\
     |   ( oo )    |
      \\   '--'  __/
       '-.___.-'  \\
       /           \\
      |   ______    |
       \\_/      \\__/
""".strip("\n").splitlines()
    return [color(line, GREEN) for line in art]


def logo_manjaro():
    block = "####"
    gap = "   "
    bars = color("##", GREEN) + " " + color("##", GREEN) + " " + color("##", GREEN)
    lines = []
    for _ in range(6):
        lines.append(color(block, GREEN) + gap + bars)
    return lines


def logo_popos():
    art = """
          .------.
        .'        '.
       /    ____     \\
      |    /    \\    |
      |    \\____/    |
       \\      ||     /
        '.    ||   .'
          '----''--'
""".strip("\n").splitlines()
    return [color(line, CYAN) for line in art]


def logo_kali():
    art = """
        /\\_/\\
       ( o.o )
      ,-' ' '-.
     /    |    \\
    (    /-\\    )
     \\__/   \\__/
       /     \\
      (_)   (_)
""".strip("\n").splitlines()
    return [color(line, BLUE) for line in art]


LOGO_MAP = {
    "linux": logo_linux,
    "ubuntu": logo_ubuntu,
    "arch": logo_arch,
    "archlinux": logo_arch,
    "debian": logo_debian,
    "fedora": logo_fedora,
    "mint": logo_mint,
    "linuxmint": logo_mint,
    "windows": logo_windows,
    "macos": logo_macos,
    "darwin": logo_macos,
    "opensuse": logo_opensuse,
    "opensuse-leap": logo_opensuse,
    "opensuse-tumbleweed": logo_opensuse,
    "manjaro": logo_manjaro,
    "popos": logo_popos,
    "pop": logo_popos,
    "kali": logo_kali,
}


def get_logo(forced=None):
    if forced:
        return LOGO_MAP.get(forced.lower(), logo_linux)()

    system = platform.system()

    if system == "Windows":
        return logo_windows()
    if system == "Darwin":
        return logo_macos()

    return LOGO_MAP.get(get_distro_id(), logo_linux)()


def make_border(width, left, right):
    return left + "=" * (width - 2) + right


def center(text, width):
    plain_len = len(strip_ansi(text))
    total_pad = max(0, width - plain_len)
    left_pad = total_pad // 2
    right_pad = total_pad - left_pad
    return " " * left_pad + text + " " * right_pad


def pad(text, width):
    return text + " " * max(0, width - len(strip_ansi(text)))


def make_header(width, theme):
    title = color("Py", theme + BOLD) + color("Fetch", CYAN + BOLD)

    print(color(make_border(width, "+", "+"), theme))
    print(color("|", theme) + center(title, width - 2) + color("|", theme))
    print(color(make_border(width, "+", "+"), CYAN))


def make_footer(width, theme):
    print(color(make_border(width, "+", "+"), theme))

    footer = (
        color("[ ", theme)
        + color("Made with ", GRAY)
        + color("Python", CYAN + BOLD)
        + color(" ]", theme)
    )

    print(color("|", theme) + center(footer, width - 2) + color("|", theme))
    print(color(make_border(width, "+", "+"), CYAN))


def build_info_lines(label_width, value_width, theme):
    used, total, _ = get_memory()

    if total is not None:
        ram_total = f"{total:.2f} GB"
        ram_percent = (used / total) * 100
    else:
        ram_total = "Unavailable"
        ram_percent = None

    disk_total, disk_percent = get_storage()

    info = [
        ("OS", get_os_name()),
        ("Kernel", platform.release()),
        ("Architecture", platform.machine()),
        ("Hostname", platform.node() or "Unknown"),
        ("CPU", get_cpu_name()),
        ("CPU Cores", str(os.cpu_count() or "Unknown")),
        ("CPU Freq", get_cpu_frequency()),
        ("RAM", f"{ram_total}  {make_bar(ram_percent)}" if ram_percent is not None else "Unavailable"),
        ("Storage", f"{disk_total:.1f} GB  {make_bar(disk_percent)}" if disk_percent is not None else "Unavailable"),
        ("Uptime", get_uptime()),
        ("Python", platform.python_version()),
    ]

    lines = []
    for label, value in info:
        plain_value = strip_ansi(value)
        has_color = value != plain_value

        parts = [value] if has_color else (
            textwrap.wrap(plain_value, width=value_width, break_long_words=True, break_on_hyphens=False)
            or [""]
        )

        for index, part in enumerate(parts):
            label_text = f"{label:<{label_width}}" if index == 0 else " " * label_width
            rendered = (
                color(label_text, theme + BOLD)
                + color(" : ", GRAY)
                + (part if has_color else color(part, WHITE))
            )
            lines.append(rendered)

    return lines


def parse_args():
    hidden_aliases = {
        "archlinux", "linuxmint", "darwin",
        "opensuse-leap", "opensuse-tumbleweed", "pop",
    }

    parser = argparse.ArgumentParser(description="PyFetch - a simple terminal system info tool")
    parser.add_argument(
        "logo",
        nargs="?",
        default=None,
        choices=sorted(set(LOGO_MAP.keys()) - hidden_aliases),
        help="Force a specific OS logo instead of auto-detecting",
    )
    parser.add_argument(
        "--color", "-c",
        default=None,
        choices=sorted(THEME_COLORS.keys()),
        help="Set the accent color used for borders, title and labels",
    )
    parser.add_argument(
        "--save-config", "-s",
        action="store_true",
        help="Save the given --color/logo as the new defaults",
    )
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Remove any saved defaults",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config()
    notices = []

    if args.reset_config:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        config = {}
        notices.append("Cleared saved config.")

    logo_choice = args.logo or config.get("logo")
    color_choice = args.color or config.get("color")

    if args.save_config:
        if args.logo:
            config["logo"] = args.logo
        if args.color:
            config["color"] = args.color
        save_config(config)
        notices.append(f"Saved defaults to {CONFIG_PATH}")

    theme = THEME_COLORS.get(color_choice, PURPLE)

    logo = get_logo(logo_choice)
    logo_width = max(len(strip_ansi(line)) for line in logo) + 2

    terminal_width = shutil.get_terminal_size((100, 30)).columns
    label_width = 12
    value_width = max(20, terminal_width - logo_width - label_width - 10)

    info_lines = build_info_lines(label_width, value_width, theme)

    content_height = max(len(logo), len(info_lines))
    logo += [""] * (content_height - len(logo))
    info_lines += [""] * (content_height - len(info_lines))

    total_width = logo_width + 3 + max(len(strip_ansi(line)) for line in info_lines) + 4

    os.system("cls" if os.name == "nt" else "clear")
    os.system("")

    print()
    make_header(total_width, theme)

    for logo_line, info_line in zip(logo, info_lines):
        row = color("  ", WHITE) + pad(logo_line, logo_width) + color(" | ", GRAY) + info_line
        padding = max(0, total_width - 2 - len(strip_ansi(row)))
        print(color("|", theme) + row + " " * padding + color("|", theme))

    make_footer(total_width, theme)
    print()

    for notice in notices:
        print(color(notice, theme))


if __name__ == "__main__":
    main()
