#!/bin/bash

help=0
show_version=0
compress_file=1
version="1.0.2"

# Borrowed from the following post: https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        -h|--help)
        help=1
        shift # past argument
        shift # past value
        ;;
        -o|--output-filepath)
        output_filepath="$2"
        shift # past argument
        shift # past value
        ;;
        -c|--disable-compression)
        compress_file=0
        shift # past argument
        shift # past value
        ;;
        -V|--version)
        show_version=1
        shift # past argument
        shift # past value
        ;;
        *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

product="exanic"
product_pretty="ExaNIC"
timestamp="$(date +%F-%HH%MM%S.%N)"
filename="${HOSTNAME}_${product}_debug_dump_${timestamp}.log"
filepath="${HOME}/${filename}"
final_filename="${filename}.gz"
final_filepath="${filepath}.gz"

if [ ${help} -eq 1 ]
then
    echo "This script captures debug information relevant to troubleshooting a"
    echo "Cisco ${product_pretty} installation."
    echo ""
    echo "By default, this debug dump will be located at the following location:"
    echo ""
    echo ${final_filepath}
    echo ""
    echo "This location can be overridden by the '-o' argument."
    echo ""
    echo "This script will prompt for superuser credentials, as some commands"
    echo "must be run with sudo."
    echo ""
    echo "Usage:"
    echo "    -o: Define the filepath (absolute or relative) and filename where"
    echo "        the debug dump will be placed. Note that this file will be"
    echo "        gunzipped, so '.gz' will be appended to the end of it."
    echo "    -c: Disable gunzip compression of resulting debug dump."
    echo "    -V: Display version information and exit."
    echo "    -h: Display this help message and exit."
    echo ""
    echo "Please direct bug reports and questions to the GitHub Issues page"
    echo "at <https://github.com/exablaze-oss/exanic-debug-dump/issues>"
    exit 1
fi

if [ ${show_version} -eq 1 ]
then
    echo "Cisco ${product_pretty} Debug Dump v${version}"
    echo ""
    echo "Copyright (C) 2020 Cisco Systems, Inc."
    echo "Cisco ${product_pretty} Debug Dump comes with ABSOLUTELY NO WARRANTY."
    echo "This is free software, and you are welcome to redistribute it"
    echo "under certain conditions. Please review the LICENSE file for"
    echo "details."
    echo ""
    echo "Originally written by Christopher Hart <chart2@cisco.com>."
    echo "Please direct bug reports and questions to the GitHub Issues page"
    echo "at <https://github.com/exablaze-oss/exanic-debug-dump/issues>"
    exit 1
fi

# If output filepath is defined, override filepath variable with new location
if [ -n "${output_filepath}" ]
then
    filepath="${output_filepath}"
fi

sudo -v

cmds=(
    "date"
    "hostname"
    "sudo lspci -vv"
    "which exanic-config"
    "sudo exanic-config -v"
    "ls /dev/exanic*"
    "dmesg"
    "uptime"
    "cat /proc/cmdline"
    "cat /proc/cpuinfo"
    "cat /proc/meminfo"
    "cat /etc/os-release"
    "uname -a"
    "sudo ipmiutil sensor"
    "sudo ipmiutil sel"
    "sudo ipmiutil health"
    "yum list installed"
    "apt list --installed"
    "dkms status"
    "chkconfig --list ntpd"
    "ntpq -p"
    "ntpstat"
    "ls /etc/udev/rules.d/"
    "cat /etc/udev/rules.d/exanic*"
    "top -b -n 1 | head -n 5"
    "cat /proc/interrupts"
    "cat /proc/stat"
    "date"
)

echo "Executing Debug Dump commands..."

echo "---------- Cisco ${product_pretty} Debug Dump ----------" &>> $filepath
for cmd in "${cmds[@]}"; do
    echo \`$cmd\` &>> $filepath
    eval $cmd &>> $filepath
    echo "" &>> $filepath # Newline
done

if [ ${compress_file} -eq 1 ]
then
    echo "Compressing Debug Dump..."
    gzip $filepath
fi

echo "Debug Dump has completed!"

if [ ${compress_file} -eq 1 ]
then
    echo "File location: ${final_filepath}" 
else
    echo "File location: ${filepath}"
fi
