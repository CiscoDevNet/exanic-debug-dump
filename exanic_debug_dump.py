import sys
import os
from argparse import ArgumentParser
import subprocess
import shutil
import gzip
from datetime import datetime

__version__ = "1.0.3"
__author__ = "Christopher Hart"
__email__ = "chart2@cisco.com"

PRODUCT = "smartnic"
PRODUCT_PRETTY = "Nexus SmartNIC"
TIMESTAMP = datetime.utcnow().strftime("%F-%HH%MM%S.%f")
FILENAME = "{0}_{1}_debug_dump_{2}.log".format(os.uname()[1], PRODUCT, TIMESTAMP)
FILEPATH = "{0}/{1}".format(os.getenv("HOME"), FILENAME)
FINAL_FILENAME = "{0}.gz".format(FILENAME)
FINAL_FILEPATH = "{0}.gz".format(FILEPATH)
ISSUES = (
    "Please direct bug reports and questions to the GitHub Issues page at "
    "<https://github.com/exablaze-oss/exanic-debug-dump/issues>"
)

__copyright__ = (
    "Copyright (C) 2021 Cisco Systems, Inc.\n"
    "Cisco {0} Debug Dump comes with ABSOLUTELY NO WARRANTY.\n"
    "This is free software, and you are welcome to redistribute it\n"
    "under certain conditions. Please review the LICENSE file for details."
).format(PRODUCT_PRETTY)

# Each element in this list is either a string, or a callable. If an element is
# a string, we assume that the string is command that needs to be executed
# directly by os.system(). If the element is a callable, then we call that
# function while passing in the 
COMMANDS = [
    "date",
    "hostname",
    "sudo lspci -vv",
    "which exanic-config",
    "sudo exanic-config -v",
    "ls /dev/exanic*",
    "dmesg",
    "uptime",
    "cat /proc/cmdline",
    "cat /proc/cpuinfo",
    "cat /proc/meminfo",
    "cat /etc/os-release",
    "uname -a",
    "sudo ipmiutil sensor",
    "sudo ipmiutil sel",
    "sudo ipmiutil health",
    "yum list installed",
    "apt list --installed",
    "dkms status",
    "chkconfig --list ntpd",
    "ntpq -p",
    "ntpstat",
    "ls /etc/udev/rules.d/",
    "cat /etc/udev/rules.d/exanic*",
    "top -b -n 1 | head -n 5",
    "cat /proc/interrupts",
    "cat /proc/stat",
    "date",
]

def run_string_command(command, file):
        file.write("`{0}`\n".format(command))
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True
        )
        stdout, stderr = p.communicate()
        if stdout:
            file.write(stdout)
        if stderr:
            file.write(stderr)
        file.write("\n")

def run_commands(filepath):
    print("Executing Debug Dump commands...")
    with open(filepath, "a+") as outfile:
        outfile.write(
            "---------- Cisco {0} Debug Dump ----------\n".format(PRODUCT_PRETTY)
        )
        for command in COMMANDS:
            if isinstance(command, str):
                run_string_command(command, outfile)
            elif callable(command):
                command(command, outfile)


def parse_arguments():
    parser = ArgumentParser(
        description=(
            "This script captures debug information relevant to troubleshooting a "
            "Cisco {0} installation. By default, a debug dump will be located at "
            "'{1}'. This location can be overridden by the '-o' argument. This "
            "script will prompt for superuser credentials, as some commands must "
            "be run with sudo.".format(PRODUCT_PRETTY, FINAL_FILEPATH)
        ),
        epilog=ISSUES
    )
    parser.add_argument(
        "--output-filepath",
        "-o",
        action="store",
        default=FINAL_FILEPATH,
        help=(
            "This argument will define the filepath (absolute or relative) and "
            "filename where the debug dump will be written. Note that this file "
            "will be gunzipped, so '.gz' will be appended to the end of the "
            "filename."
        )
    )
    parser.add_argument(
        "--disable-compression",
        "-c",
        action="store_true",
        default=False,
        help=(
            "This argument will disable gunzip compression of the debug dump "
            "created by this script."
        )
    )
    parser.add_argument(
        "--version",
        "-V",
        action="store_true",
        default=False,
        help=(
            "This argument will display the version of the script and exit."
        )
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.version:
        version = (
            "Cisco {0} Debug Dump v{1}\n"
            "\n"
            "{2}\n"
            "\n"
            "Originally written by {3} <{4}>\n"
            "{5}".format(
                PRODUCT_PRETTY,
                __version__,
                __copyright__,
                __author__,
                __email__,
                ISSUES
            )
        )
        print(version)
        sys.exit()
    os.system("sudo -v")
    filepath = args.output_filepath if args.output_filepath else FILEPATH
    final_filepath = "{0}.gz".format(args.output_filepath) if args.output_filepath else FINAL_FILEPATH
    run_commands(filepath)
    if not args.disable_compression:
        print("Compressing Debug Dump...")
        with open(filepath, "rb") as f_in, gzip.open("{0}.gz".format(filepath), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    print("Debug Dump has completed!")
    if args.disable_compression:
        print("File location: {0}".format(filepath))
    else:
        print("File location: {0}".format(final_filepath))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
