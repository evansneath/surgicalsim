#!/usr/bin/env python

"""Collect Results

A small script that takes multiple result files from different runs in the
current working directory and creates a single comma-separated file.
"""

import os.path

DATA_DIR = './results'
OUT_FILE = './collected.txt'

out_text = []
first_pass = True

print 'Collecting data'

# Get all 'run_*.txt' files in the given data directory
os.chdir(DATA_DIR)
run_files = os.listdir('./')

for run_file in run_files:
    # Determine if this is actually a data file
    if 'run_' not in run_file:
        continue

    with open(run_file, 'r') as f:
        # Strip all of the raw data
        lines = f.readlines()[4:]

        for i, line in enumerate(lines):
            if first_pass:
                # First time at this line, append it to the text
                out_text.append([])
            else:
                # Get rid of the first column (episode number)
                line = line.split(', ')[1]
            
            # Get rid of the newline character
            line = line.rstrip('\n')

            # Add the data to the table row
            out_text[i].append(line)

    first_pass = False

# Write to the output file
with open(OUT_FILE, 'w+') as f:
    for line in out_text:
        line = ', '.join(line) + '\n'
        f.write(line)

print 'Done'

exit()
