#!/usr/bin/env python3
### Ana Anzulović

import os
import subprocess
import re

def find_matching_files(directory):
    umd_files = []
    bonding_files = []

    for filename in os.listdir(directory):
        if filename.endswith('.umd.dat'):
            umd_files.append(filename)
        elif filename.endswith('.bonding.dat'):
            bonding_files.append(filename)

    print('Matching pairs of umd.dat and bonding.dat files:')
    for umd_file in umd_files:
        common_prefix = extract_common_prefix([umd_file])
        matching_bonding_files = [file for file in bonding_files if file.startswith(common_prefix)]
        for matching_bonding_file in matching_bonding_files:  # Use a different variable name here
            print(f"  {umd_file} - {matching_bonding_file}")

    return umd_files, bonding_files

def extract_common_prefix(file_list):
    common_prefix = os.path.commonprefix(file_list)
    return re.sub(r'\.umd\.dat$|\.bonding\.dat$', '', common_prefix)

def run_speciation_script(umd_file, bonding_file):
    cmd = [
        'speciation_and_angles.py',
        '-f', bonding_file,
        '-c', 'O',
        '-a', 'Si,Al',
        '-r', '1',
        '-m', '0',
        '-u', umd_file
    ]
    subprocess.run(cmd, cwd=os.getcwd())

if __name__ == "__main__":
    current_directory = os.getcwd()
    umd_files, bonding_files = find_matching_files(current_directory)
    matching_pairs = []
    for umd_file in umd_files:
        common_prefix = extract_common_prefix([umd_file])
        matching_bonding_files = [file for file in bonding_files if file.startswith(common_prefix)]

        for matching_bonding_file in matching_bonding_files:
            run_speciation_script(umd_file, matching_bonding_file)
            matching_pairs.append((umd_file, matching_bonding_file))
