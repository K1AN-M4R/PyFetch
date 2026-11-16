import os
import platform
import shutil
import ctypes
import textwrap
import re


RESET = "\033[0m"
BOLD = "\033[1m"

PURPLE = "\033[38;5;141m"
CYAN = "\033[38;5;51m"
WHITE = "\033[97m"
GRAY = "\033[38;5;245m"
GREEN = "\033[38;5;120m"
YELLOW = "\033[38;5;221m"
RED = "\033[38;5;203m"


def color(text, code):
    return f"{code}{text}{RESET}"


def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)


# ---------------------------------------------------------------------------
# System info gathering
# ---------------------------------------------------------------------------

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

        if ctypes.windll.kernel32.GlobalMemoryStatusEx(
            ctypes.byref(status)
        ):
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
    """Return a lowercase distro id (e.g. 'ubuntu', 'arch', 'fedora')."""
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

        used = disk.used / 1024**3
        total = disk.total / 1024**3
        free = disk.free / 1024**3
        percent = (disk.used / disk.total) * 100

        return used, total, free, percent

    except OSError:
        return None, None, None, None


def get_uptime():
    try:
        if platform.system() == "Linux":
            with open("/proc/uptime", encoding="utf-8") as file:
                seconds = float(file.read().split()[0])

        elif platform.system() == "Windows":
            seconds = (
                ctypes.windll.kernel32.GetTickCount64() / 1000
            )

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
    """Render a usage bar like [#######-----] 65%"""
    if percent is None:
        return "Unavailable"

    filled = int(length * percent / 100)
    filled = max(0, min(length, filled))

    if percent >= 85:
        bar_color = RED
    elif percent >= 60:
        bar_color = YELLOW
    else:
        bar_color = GREEN

    bar = "#" * filled + "-" * (length - filled)
    return f"[{color(bar, bar_color)}] {percent:.1f}%"


# ---------------------------------------------------------------------------
# ASCII logos (one per distro/OS, colorized)
# ---------------------------------------------------------------------------

def logo_linux_generic():
    art = [
        "      .--.      ",
        "     |o_o |     ",
        "     |:_/ |     ",
        "    //   \\ \\    ",
        "   (|     | )   ",
        "  /'\\_   _/`\\   ",
        "  \\___)=(___/   ",
    ]
    return [color(line, WHITE) for line in art]


def logo_ubuntu():
    art = [
        "         _          ",
        "     ---(_)        ",
        " _/  ---  \\        ",
        "(_) |   |          ",
        " \\  ---  _/        ",
        "     ---(_)        ",
    ]
    return [color(line, RED) for line in art]


def logo_arch():
    art = [
        "       /\\       ",
        "      /  \\      ",
        "     /\\   \\     ",
        "    /      \\    ",
        "   /   ,,   \\   ",
        "  /   |  |   \\  ",
        " /_-''    ''-_\\ ",
    ]
    return [color(line, CYAN) for line in art]


def logo_debian():
    art = [
        "   _____    ",
        "  /  __ \\   ",
        " |  /    |  ",
        " |  \\___-   ",
        " -_         ",
        "   --_      ",
    ]
    return [color(line, RED) for line in art]


def logo_fedora():
    art = [
        "      _____     ",
        "     /   __)\\   ",
        "     |  /  \\ \\  ",
        "  ___|  |__/ /  ",
        " / (_    _)_/   ",
        " \\   |  |       ",
        "  \\__|  |       ",
    ]
    return [color(line, PURPLE) for line in art]


def logo_mint():
    art = [
        " _____________  ",
        "|  ___________| ",
        "| |   _     _  | ",
        "| |  | |   | | | ",
        "| |  | |___| | | ",
        "| |_____________| ",
        "|_______________| ",
    ]
    return [color(line, GREEN) for line in art]


def logo_windows():
    art = [
        "  ##### #####  ",
        "  ##### #####  ",
        "  ##### #####  ",
        "               ",
        "  ##### #####  ",
        "  ##### #####  ",
        "  ##### #####  ",
    ]
    return [color(line, CYAN) for line in art]


def logo_mac():
    art = [
        "      .:'      ",
        "   __ :'__     ",
        ".'`  `-'  ``.  ",
        ":          :   ",
        ":          `.  ",
        " :    `.    :  ",
        "  `.    `.  :  ",
        "    `.    `.'  ",
    ]
    return [color(line, WHITE) for line in art]


LOGO_MAP = {
    "ubuntu": logo_ubuntu,
    "arch": logo_arch,
    "archlinux": logo_arch,
    "debian": logo_debian,
    "fedora": logo_fedora,
    "linuxmint": logo_mint,
    "mint": logo_mint,
    "windows": logo_windows,
    "darwin": logo_mac,
    "macos": logo_mac,
}


def get_logo():
    system = platform.system()

    if system == "Windows":
        return logo_windows()
    if system == "Darwin":
        return logo_mac()

    distro_id = get_distro_id()
    builder = LOGO_MAP.get(distro_id, logo_linux_generic)
    return builder()


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def make_border(width, left, right):
    return left + "=" * (width - 2) + right


def center(text, width):
    plain_len = len(strip_ansi(text))
    total_pad = max(0, width - plain_len)
    left_pad = total_pad // 2
    right_pad = total_pad - left_pad
    return " " * left_pad + text + " " * right_pad


def pad(text, width):
    plain_len = len(strip_ansi(text))
    return text + " " * max(0, width - plain_len)


def make_header(width):
    title = color("Py", PURPLE + BOLD) + color("Fetch", CYAN + BOLD)

    print(color(make_border(width, "+", "+"), PURPLE))
    print(color("|", PURPLE) + center(title, width - 2) + color("|", PURPLE))
    print(color(make_border(width, "+", "+"), CYAN))


def make_footer(width):
    print(color(make_border(width, "+", "+"), PURPLE))

    footer = (
        color("[ ", PURPLE)
        + color("Made with ", GRAY)
        + color("Python", CYAN + BOLD)
        + color(" ]", PURPLE)
    )

    print(color("|", PURPLE) + center(footer, width - 2) + color("|", PURPLE))
    print(color(make_border(width, "+", "+"), CYAN))


def build_info_lines(label_width, value_width):
    used, total, available = get_memory()

    if total is not None:
        ram_total = f"{total:.2f} GB"
        ram_used_val = used
        ram_percent = (used / total) * 100
    else:
        ram_total = "Unavailable"
        ram_used_val = None
        ram_percent = None

    disk_used, disk_total, disk_free, disk_percent = get_storage()

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
        parts = textwrap.wrap(
            plain_value,
            width=value_width,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]

        # If the value carries color codes (e.g. the usage bar), don't wrap —
        # keep it on one line so escape sequences stay intact.
        if value != plain_value:
            parts = [value]

        for index, part in enumerate(parts):
            label_text = f"{label:<{label_width}}" if index == 0 else " " * label_width
            rendered = (
                color(label_text, PURPLE + BOLD)
                + color(" : ", GRAY)
                + (part if value != plain_value else color(part, WHITE))
            )
            lines.append(rendered)

    return lines


def main():
    logo = get_logo()
    logo_width = max(len(strip_ansi(line)) for line in logo) + 2

    terminal_width = shutil.get_terminal_size((100, 30)).columns
    label_width = 12
    value_width = max(20, terminal_width - logo_width - label_width - 10)

    info_lines = build_info_lines(label_width, value_width)

    content_height = max(len(logo), len(info_lines))
    logo = logo + [""] * (content_height - len(logo))
    info_lines = info_lines + [""] * (content_height - len(info_lines))

    total_width = logo_width + 3 + max(len(strip_ansi(l)) for l in info_lines) + 4

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    os.system("")

    print()
    make_header(total_width)

    for logo_line, info_line in zip(logo, info_lines):
        left = pad(logo_line, logo_width)
        row = color("  ", WHITE) + left + color(" | ", GRAY) + info_line
        padding = max(0, total_width - 2 - len(strip_ansi(row)))
        print(color("|", PURPLE) + row + " " * padding + color("|", PURPLE))

    make_footer(total_width)
    print()


if __name__ == "__main__":
    main()
