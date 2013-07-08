#!/usr/bin/env python

import os.path

def main():
    out_file = './collected.txt'
    out_text = []
    first_pass = True

    print 'Gathering data'

    # Get all 'run' files in the current directory
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
                    out_text.append([])
                else:
                    line = line.split(', ')[1]
                
                # Get rid of the newline character
                line = line.rstrip('\n')

                # Add the data to the table row
                out_text[i].append(line)

        first_pass = False

    # Write to the output file
    with open(out_file, 'w+') as f:
        for line in out_text:
            line = ', '.join(line) + '\n'
            f.write(line)

    print 'Done'

    return

if __name__ == '__main__':
    main()
    exit()
