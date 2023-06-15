import argparse
import logging
import sys
import pathlib

import stressio.stressio as stressio


parser = argparse.ArgumentParser(prog="stressio")
parser.add_argument(
    "-d",
    "--disk-device",
    default="/dev/sda",
    help="This is the WHOLE-DISK device filename (with or without \"/dev/\"), \
        e.g. \"sda\" or \"/dev/sda\".  The script finds a filesystem on that \
        device, mounts it if necessary, and runs the tests on that mounted \
        filesystem.",
    type=str)
parser.add_argument(
    "-m",
    "--max-load",
    default=30,
    help="The maximum acceptable CPU load, as a percentage.",
    type=int)
parser.add_argument(
    "-x",
    "--xfer",
    default=4096,
    help="The amount of data to read from the disk, in mebibytes.",
    type=int)
parser.add_argument(
    "-v",
    "--verbose",
    help="If present, produce more verbose output.",
    action="store_true")
args = parser.parse_args()


def main():
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO)

    if not args.disk_device.startswith("/dev/"):
        device_name = "".join(("/dev/", args.disk_device))
    else:
        device_name = args.disk_device

    if not pathlib.Path(device_name).is_block_device():
        logging.error(f"Unknown block device {device_name}\n")
        parser.print_help()
        sys.exit(1)

    try:
        logging.info(f"Testing CPU load when reading \
{args.xfer} MiB from {device_name}")
        logging.info(f"Maximum acceptable CPU load is {args.max_load}")

        stressio.flush(device_name)
        do_compute = stressio.set_load(stressio.get_aggregate_cpu_stats())

        logging.debug("Beginning disk read....")
        stressio.stress_disk(device_name, args.xfer)
        logging.debug("Disk read complete!")

        do_compute(stressio.get_aggregate_cpu_stats())
    except Exception as err:
        logging.error(err)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
