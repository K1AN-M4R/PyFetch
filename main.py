
import os
import platform
import shutil


def get_memory():
    """Get RAM information on Linux or Windows."""

    if os.path.exists("/proc/meminfo"):
        memory = {}

        with open("/proc/meminfo", encoding="utf-8") as file:
            for line in file:
                key, value = line.split(":", 1)
                memory[key] = int(value.strip().split()[0])

        total = memory.get("MemTotal", 0) / (1024 ** 2)
        available = memory.get("MemAvailable", 0) / (1024 ** 2)
        used = total - available

        return used, total

    if platform.system() == "Windows":
        import ctypes

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
            total = status.total_phys / (1024 ** 3)
            used = (status.total_phys - status.avail_phys) / (1024 ** 3)
            return used, total

    return None, None


def get_cpu_name():
    """Get CPU name when available."""

    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as file:
                for line in file:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass

    return platform.processor() or "Unknown CPU"


def main():
    os_name = f"{platform.system()} {platform.release()}"
    python_version = platform.python_version()
    cpu_name = get_cpu_name()

    used, total = get_memory()

    try:
        disk = shutil.disk_usage(os.path.expanduser("~"))
        disk_used = (disk.total - disk.free) / (1024 ** 3)
        disk_total = disk.total / (1024 ** 3)
        storage = f"{disk_used:.1f} GB / {disk_total:.1f} GB"
    except OSError:
        storage = "Unavailable"

    ram = (
        f"{used:.1f} GB / {total:.1f} GB"
        if total is not None
        else "Unavailable"
    )


    info = [
        ("OS", os_name),
        ("Python", python_version),
        ("CPU", cpu_name),
        ("RAM", ram),
        ("Storage", storage),
    ]


    label_width = 12

    content_width = max(
        2 + label_width + 3 + len(value)
        for label, value in info
    )

    width = max(48, content_width + 2)

    title = " PyFetch "
    footer = " Made with Python"


    width = max(width, len(title) + 4, len(footer) + 4)

    print()
    print("╭" + "─" * (width - 2) + "╮")
    print("│" + title.center(width - 2) + "│")
    print("├" + "─" * (width - 2) + "┤")

    for label, value in info:
        line = f"  {label:<{label_width}} : {value}"
        print("│" + line.ljust(width - 2) + "│")

    print("│" + " " * (width - 2) + "│")
    print("│" + footer.center(width - 2) + "│")
    print("╰" + "─" * (width - 2) + "╯")
    print()


if __name__ == "__main__":
    main()
