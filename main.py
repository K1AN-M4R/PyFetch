
import os
import platform
import shutil
import ctypes
import textwrap


RESET = "\033[0m"
BOLD = "\033[1m"

PURPLE = "\033[38;5;141m"
CYAN = "\033[38;5;51m"
WHITE = "\033[97m"
GRAY = "\033[38;5;245m"


def color(text, code):
    return f"{code}{text}{RESET}"


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

        return (
            f"{used:.1f} GB / {total:.1f} GB "
            f"({percent:.1f}% used, {free:.1f} GB free)"
        )

    except OSError:
        return "Unavailable"


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

        return f"{days}d {hours}h {minutes}m"

    except (OSError, ValueError):
        return "Unavailable"


def make_border(width, left, right):
    return left + "=" * (width - 2) + right


def center(text, width):
    return text.center(width)


def make_header(width):
    title = (
        color("Py", PURPLE + BOLD)
        + color("Fetch", CYAN + BOLD)
    )

    print(color(make_border(width, "+", "+"), PURPLE))
    print(
        color("|", PURPLE)
        + center(title, width - 2)
        + color("|", PURPLE)
    )
    print(color(make_border(width, "+", "+"), CYAN))


def make_footer(width):
    print(color("+" + "=" * (width - 2) + "+", PURPLE))

    footer = (
        color("[ ", PURPLE)
        + color("Made with ", GRAY)
        + color("Python", CYAN + BOLD)
        + color(" ]", PURPLE)
    )

    print(
        color("|", PURPLE)
        + center(footer, width - 2)
        + color("|", PURPLE)
    )

    print(color(make_border(width, "+", "+"), CYAN))


def main():
    used, total, available = get_memory()

    if total is not None:
        ram_used = f"{used:.2f} GB"
        ram_available = f"{available:.2f} GB"
        ram_percent = f"{(used / total) * 100:.1f}%"
        ram_total = f"{total:.2f} GB"
    else:
        ram_used = "Unavailable"
        ram_available = "Unavailable"
        ram_percent = "Unavailable"
        ram_total = "Unavailable"

    info = [
        ("OS", get_os_name()),
        ("Kernel", platform.release()),
        ("Architecture", platform.machine()),
        ("Hostname", platform.node() or "Unknown"),
        ("CPU", get_cpu_name()),
        ("CPU Cores", str(os.cpu_count() or "Unknown")),
        ("CPU Frequency", get_cpu_frequency()),
        ("RAM Total", ram_total),
        ("RAM Used", ram_used),
        ("RAM Available", ram_available),
        ("RAM Usage", ram_percent),
        ("Storage", get_storage()),
        ("Uptime", get_uptime()),
        ("Python", platform.python_version()),
        ("Python Path", os.path.abspath(os.sys.executable)),
    ]

    label_width = 14

    required_width = max(
        label_width + len(value) + 7
        for label, value in info
    ) + 2

    terminal_width = shutil.get_terminal_size((80, 20)).columns
    width = max(40, min(required_width, terminal_width))

    value_width = max(10, width - label_width - 7)

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    os.system("")

    print()
    make_header(width)

    for label, value in info:
        parts = textwrap.wrap(
            value,
            width=value_width,
            break_long_words=True,
            break_on_hyphens=False
        ) or [""]

        for index, part in enumerate(parts):
            if index == 0:
                prefix = "  "
                label_text = f"{label:<{label_width}}"
            else:
                prefix = "  "
                label_text = " " * label_width

            plain = prefix + label_text + " : " + part
            padding = max(0, width - 2 - len(plain))

            line = (
                color(prefix, WHITE)
                + color(label_text, PURPLE + BOLD)
                + color(" : ", GRAY)
                + color(part, WHITE)
                + " " * padding
            )

            print(
                color("|", PURPLE)
                + line
                + color("|", PURPLE)
            )

    make_footer(width)
    print()


if __name__ == "__main__":
    main()
