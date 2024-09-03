'''
Some tools to generate the stats needed for keeping track of progress (through the web interface)
'''

import csv
import re

from utils.erics_syllabifier import syllabifier
from utils.utils import Colors, open_syllable, DICHRONA, base_alphabet, base


def non_hidden_quantity(word):
    '''
    >>> non_hidden_quantity('δυστυχές')
    >>> ['τυ']
    '''
    non_hidden_quantities = []
    syllables = syllabifier(word)
    if syllables:
        for syllable in syllables:
            if open_syllable(syllable) and any(char in DICHRONA for char in syllable):
                non_hidden_quantities.append(syllable)
    return non_hidden_quantities


def extract_macron_positions(macron_column):
    '''
    >>> extract_macron_positions('_4^6')
    >>> [4, 6]
    >>> extract_macron_positions('')
    >>> []
    '''
    # Extract integers from the macron column (_4^6 format)
    pattern = re.compile(r'[_^](\d+)')
    return [int(match.group(1)) for match in pattern.finditer(macron_column)]


def macronized_non_hidden_dichrona(line):
    '''
    >>> line = 'Αἴγινα	n-s---fn-	αἴγινα	_4^6'
    >>> macronized_non_hidden_dichrona(line)
    >>> 2
    '''
    columns = list(csv.reader([line], delimiter='\t'))[0]
    if len(columns) < 4:
        print(f'{Colors.RED}Skipping line (not enough columns): {line}{Colors.ENDC}')
        return 0

    token = columns[0]
    macron_positions = extract_macron_positions(columns[3])
    count = 0

    for syllable in non_hidden_quantity(token):
        syllable_start_index = token.find(syllable)
        position_counter = 0
        for index, char in enumerate(token):
            if re.search(base_alphabet, base(char)):
                position_counter += 1
            if syllable_start_index <= index < syllable_start_index + len(syllable):
                if char in DICHRONA and position_counter in macron_positions:
                    count += 1
                    break  # We only count this syllable once

    return count


def unmacronized_non_hidden_dichrona(line):
    '''
    >>> line = 'μάλιστα	d-------s	μάλα	^2^4^7	wiktionary'
    >>> 0
    >>> line = 'μάλιστα	d-------s	μάλα	^2^7	wiktionary'
    >>> 0
    >>> line = 'μάλιστα	d-------s	μάλα	^7	wiktionary'
    >>> 1
    >>> line = 'μάλιστα	d-------s	μάλα		wiktionary'
    >>> 2
    '''
    # Extract columns from the line
    columns = line.split('\t')
    
    # Check if line has enough columns
    if len(columns) < 4:
        print(f'{Colors.RED}Skipping line (not enough columns): {line}{Colors.ENDC}')
        return 0

    # Extract token from the first column
    token = columns[0]

    # Get the list of non-hidden quantities
    total_non_hidden_quantities = len(non_hidden_quantity(token))

    # Subtract the number of macronized non-hidden dichrona from the total
    macronized_count = macronized_non_hidden_dichrona(line)

    # Return the unmacronized count
    return total_non_hidden_quantities - macronized_count


def has_work_to_do(line):
    '''
    Line still has unmacronized unhidden dichrona (priority)

    >>> line = 'μάλιστα	d-------s	μάλα	^4^7	wiktionary'
    >>> True
    >>> line = 'μάλιστα	d-------s	μάλα	^2^4^7	wiktionary'
    >>> False
    '''
    return unmacronized_non_hidden_dichrona(line) > 0


############### COUNTERS #########################


def macronized_non_hidden_dichrona_in_tsv(input_tsv):
    total_count = 0
    first_line = True  # Flag to identify the header

    with open(input_tsv, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')

        for row in reader:
            if first_line:
                # Skip the header line
                first_line = False
                continue

            if row:
                line = '\t'.join(row)  # Join the row back into a line
                #print(line)
                total_count += macronized_non_hidden_dichrona(line)

    return total_count


def total_non_hidden_quantities_in_tsv(input_tsv):
    total_sum = 0
    first_line = True  # Flag to identify the header

    with open(input_tsv, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')

        for row in reader:
            if first_line:
                # Skip the header line
                first_line = False
                continue

            if row:
                word = row[0]
                non_hidden_quantities = non_hidden_quantity(word)
                total_sum += len(non_hidden_quantities)

    return total_sum


def count_macrons_in_tsv(input_tsv):
    macron_pattern = re.compile(r'[\^_](\d{1,2})')  # Matches ^1 to ^99 or _1 to _99
    total_macrons = 0

    with open(input_tsv, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')
        first_line = True  # Flag to skip the header

        for row in reader:
            if first_line:
                first_line = False
                continue

            if row and len(row) >= 4:
                macron_column = row[3]
                macrons = macron_pattern.findall(macron_column)
                total_macrons += len(macrons)

    return total_macrons


def count_unique_first_column(input_tsv):
    unique_values = set()

    with open(input_tsv, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')
        first_line = True  # Flag to skip the header

        for row in reader:
            if first_line:
                first_line = False
                continue

            if row:
                first_column_value = row[0]
                unique_values.add(first_column_value)

    return len(unique_values)


def count_empty_macron(input_tsv):
    empty_count = 0

    with open(input_tsv, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')
        first_line = True  # Flag to skip the header

        for row in reader:
            if first_line:
                first_line = False
                continue

            if row:
                if len(row) < 4 or row[3] == '':
                    empty_count += 1

    return empty_count


############### PRINT #########################


input_tsv = 'macrons.tsv'

print(f'There are non-hidden dichrona: {total_non_hidden_quantities_in_tsv(input_tsv)}')
print(f'out of which {Colors.GREEN}{macronized_non_hidden_dichrona_in_tsv(input_tsv)}{Colors.ENDC} are macronized.')
print(f'Macrons: {count_macrons_in_tsv(input_tsv)}')
print(f"Number of unique first column values: {count_unique_first_column(input_tsv)}")
print(f"Count of lines with empty fourth column: {Colors.RED}{count_empty_macron(input_tsv)}{Colors.ENDC}")
