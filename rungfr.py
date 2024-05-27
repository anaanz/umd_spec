#!/usr/bin/env python3
#!/bin/sh
### go to the directory where you want to run gofrs (for example the temperature folder that contains all the subdirectories with diff volumes)
### this script finds all the umd.dat files in subdirectories of the folder from which it is being ran, it creates a gofr directory, copies all the umds to gofr directory and then runs gofr_new.py script on all of them
### prerequisite: your gofr script must be executable (you've put it to PATH)
### Ana Anzulović

import os
import shutil
import subprocess

def find_umd_dat_files(directory='.'):
    umd_dat_files = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(directory):
        if 'msd' in dirs: # skips the gofr directory
            dirs.remove('msd')
        # Check for files ending with 'umd.dat'
        for file in files:
            if file.endswith('umd.dat'):
                umd_dat_files.append(os.path.join(root, file))
    return umd_dat_files

def create_gofr_directory():
    gofr_directory = os.path.join(os.getcwd(), 'gofr')  # Use os.path.join for creating the path
    # Create 'gofr' directory if it doesn't exist
    if not os.path.exists(gofr_directory):
        os.makedirs(gofr_directory)
        print("I have created the 'gofr' directory.")
    
    return gofr_directory

def copy_umd_dat_files(umd_dat_files, destination_directory):
    for file_path in umd_dat_files:
        shutil.copy(file_path, destination_directory)

def run_gofr_script(umd_file):
    command = f"gofr_new.py -f {umd_file}" # change the title of the script you want to be ran
    subprocess.run(command, shell=True)

def remove_umd_dat_files(directory):
    for file in os.listdir(directory):
        if file.endswith('.umd.dat'):
            file_path = os.path.join(directory, file)
            os.remove(file_path)
            print(f"Removed: {file_path}")

def main():
    current_directory = os.getcwd()
    umd_dat_files = find_umd_dat_files(current_directory)

    if umd_dat_files:
        print("List of umd.dat files:")
        for file_path in umd_dat_files:
            print(file_path)

        gofr_directory = create_gofr_directory()

        # Copy umd.dat files to 'gofr' directory
        copy_umd_dat_files(umd_dat_files, gofr_directory)

        # Change to 'gofr' directory
        os.chdir(gofr_directory)
        print("Changed to the 'gofr' directory.")

        # Run gofr_new.py script (replace this with the actual command to run your script)
        for file_path in umd_dat_files:
            run_gofr_script(os.path.basename(file_path))  # Use only the filename, not the full path

        # Remove .umd.dat files from 'gofr' directory
        # remove_umd_dat_files(gofr_directory)

    else:
        print("No umd.dat files found in the current directory and its subdirectories.")

if __name__ == "__main__":
    main()
