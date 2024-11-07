import csv
from utils.stats import has_work_to_do

def reorder_tsv(input_filepath, output_filepath):
    with open(input_filepath, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        lines_with_work = []
        lines_without_work = []

        # Separate the lines that pass has_work_to_do from those that don't
        header = next(reader)  # Keep the header untouched
        for row in reader:
            line = '\t'.join(row)  # Convert list back to tab-separated string for function
            if has_work_to_do(line):
                lines_with_work.append(row)
            else:
                lines_without_work.append(row)

    # Write the output in the desired order
    with open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        
        # Write the header first
        writer.writerow(header)
        
        # Write the rows with work to do first
        writer.writerows(lines_with_work)
        
        # Add the Rainbow CSV comment line
        writer.writerow(['#'])  # Rainbow CSV interprets this as a comment
        
        # Write the remaining rows without work
        writer.writerows(lines_without_work)

# Usage:
input_filepath = 'macrons.tsv'
output_filepath = 'reordered_macrons.tsv'
reorder_tsv(input_filepath, output_filepath)
