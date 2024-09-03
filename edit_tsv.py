from flask import Flask, render_template, request, redirect, url_for
from utils.stats import has_work_to_do
from utils.utils import DICHRONA
import csv

app = Flask(__name__)

# Load the TSV data
def load_tsv(filepath):
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        data = list(reader)  # List of lists
    return data

# Save the TSV data
def save_tsv(filepath, data):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(data)  # Save as a list of lists

# Route to display and edit TSV data
@app.route('/', methods=['GET', 'POST'])
def edit_tsv():
    filepath = 'macrons.tsv'  # Path to your TSV file

    if request.method == 'POST':
        # Update the TSV with submitted data
        updated_data = []
        rows = request.form.getlist('row')

        # Rebuild the rows by splitting the input back into individual columns
        for row in rows:
            updated_data.append(row.split('\t'))  # Re-split row into columns

        # Save the updated TSV data
        save_tsv(filepath, updated_data)
        return redirect(url_for('edit_tsv'))

    # Load the TSV data for GET request
    data = load_tsv(filepath)

    # Separate the header from the data (skip the first line in checks)
    header = data[0]
    filtered_data = [row for row in data[1:] if has_work_to_do('\t'.join(row))]

    # Add the header back to filtered data to display in the table
    filtered_data.insert(0, header)

    return render_template('edit_tsv.html', data=filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
