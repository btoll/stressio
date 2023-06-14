import argparse
import subprocess
import sys
from pathlib import Path

import stressio.stressio as stressio
import logging


parser = argparse.ArgumentParser(prog="stressio")
parser.add_argument("-d", "--disk-device", default="/dev/sda", help="This is the WHOLE-DISK device filename (with or without \"/dev/\"), e.g. \"sda\" or \"/dev/sda\". The script finds a filesystem on that device, mounts it if necessary, and runs the tests on that mounted filesystem.", type=str)
parser.add_argument("-m", "--max-load", default=30, help="The maximum acceptable CPU load, as a percentage.", type=int)
parser.add_argument("-x", "--xfer", default=4096, help="The amount of data to read from the disk, in mebibytes.", type=int)
parser.add_argument("-v", "--verbose", help="If present, produce more verbose output.", action="store_true")
args = parser.parse_args()


def get_cpu_stats():
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
            aggregates = [int(n) for n in f.readline().split()[1:]]
            return aggregates, sum(aggregates), aggregates[3]
    except OSError:
        raise


def main():
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO)

    device_name = "".join(("/dev/", args.disk_device)) if not args.disk_device.startswith("/dev/") else args.disk_device

    if not Path(device_name).is_block_device():
        logging.info("Unknown block device \"$disk_device\"")
        parser.print_help()
        sys.exit(1)

    try:
        logging.info(f"Testing CPU load when reading {args.xfer} MiB from {device_name}")
        logging.info(f"Maximum acceptable CPU load is {args.max_load}")

        # Raise an exception when exit code of the subprocess is non-zero with
        # `check=True` argument.
        subprocess.run(
            ["sudo", "blockdev", "--flushbufs", device_name],
            check=True,
            timeout=30)

        start_stats, start_total, start_system_stat = get_cpu_stats()

        logging.debug("Beginning disk read....")

        completed_process = subprocess.run(
            ["sudo",
                "dd",
                f"if={device_name}",
                "of=/dev/null",
                "bs=1048576",
                f"count={args.xfer}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            timeout=30)

        logging.debug("Disk read complete!")

        end_stats, end_total, end_system_stat = get_cpu_stats()

        diff_idle = end_system_stat - start_system_stat
        diff_total = end_total - start_total
        diff_used = diff_total - diff_idle
        cpu_load = int((diff_used * 100) / diff_total) if diff_total != 0 else 0

        logging.debug(f"Start CPU time = {start_total}")
        logging.debug(f"End CPU time = {end_total}")
        logging.debug(f"CPU time used = {diff_used}")
        logging.debug(f"Total elapsed time = {diff_total}")

        logging.info(f"Detected disk read CPU load is {cpu_load}")
    except subprocess.CalledProcessError as err:
        print(f"[ERROR]: {err}")
        sys.exit(1)
    except subprocess.TimeoutExpired as err:
        print(f"[ERROR]: {err}.")
        sys.exit(1)
    except OSError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
