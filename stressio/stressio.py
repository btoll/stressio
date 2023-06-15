import functools
import logging
import subprocess


def compute_cpu_load(start_load, end_load):
    start_total = sum(start_load)
    end_total = sum(end_load)

    diff_idle = end_load[3] - start_load[3]
    diff_total = end_total - start_total
    diff_used = diff_total - diff_idle
    cpu_load = int((diff_used * 100) / diff_total) if diff_total != 0 else 0

    logging.debug(f"Start CPU time = {start_total}")
    logging.debug(f"End CPU time = {end_total}")
    logging.debug(f"CPU time used = {diff_used}")
    logging.debug(f"Total elapsed time = {diff_total}")

    logging.info(f"Detected disk read CPU load is {cpu_load}")


def flush(device_name):
    try:
        subprocess.run(
            ["sudo", "blockdev", "--flushbufs", device_name],
            check=True,
            timeout=60)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise


def get_aggregate_cpu_stats():
    try:
        with open("/proc/stat", "r") as f:
            # Will read the following line, which is an aggregate of all the CPUs on
            # the system since the system first booted:
            #
            #       cpu  10263763 81754 4812820 32308895 90050 0 35175 0 0 0
            #
            # They translate to:
            #   1. user: normal processes executing in user mode
            #   2. nice: niced processes executing in user mode
            #   3. system: processes executing in kernel mode
            #   4. idle: twiddling thumbs
            #   5. iowait: In a word, iowait stands for waiting for I/O to complete
            #   6. irq: servicing interrupts
            #   7. softirq: servicing softirqs
            #   8. steal: involuntary wait
            #   9. guest: running a normal guest
            #  10. guest_nice: running a niced guest
            #
            # Obviously, we don't want the beginning "cpu" text, so skip it.
            return [int(n) for n in f.readline().split()[1:]]
    except OSError:
        raise


def set_load(start_load):
    return functools.partial(compute_cpu_load, start_load)


def stress_disk(device_name, xfer):
    try:
        completed_process = subprocess.run(
            ["sudo",
                "dd",
                f"if={device_name}",
                "of=/dev/null",
                "bs=1048576",
                f"count={xfer}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            timeout=60)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise
