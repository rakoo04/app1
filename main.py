import PyPDF2
import pandas as pd
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    # Get PDF file from request
    pdf_file = request.files['file']
    # Extract text from PDF
    parsed_text = extract_text(pdf_file)
    # Create DataFrame from parsed text
    df = create_dataframe(parsed_text)
    # Save DataFrame to CSV file
    csv_file = 'output.csv'
    df.to_csv(csv_file, index=False)
    # Send CSV file in response
    return send_file(csv_file, as_attachment=True)

def extract_text(pdf_file):
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    num_pages = len(pdf_reader.pages)
    text_pages = []

    for i in range(num_pages):
        page = pdf_reader.pages[i]
        page_text = page.extract_text()

        # Remove text outside main area of the page
        page_text = page_text.split('\n')
        page_text = [line.strip() for line in page_text if line.strip()]
        text_pages.extend(page_text)

    # Convert text pages to list of dictionaries
    result = []
    for line in text_pages:
        result.append({'text': line})

    return result

def create_dataframe(parsed_text):
    # Create DataFrame from parsed text
    df = pd.DataFrame(parsed_text)

    # Filter out rows with less than 30 characters
    df = df[df['text'].str.len() >= 30]

    # Drop duplicates, keeping only the first occurrence
    df = df.drop_duplicates(subset=['text'], keep='first')

    # Calculate length of each text string and add as new column
    df['text_length'] = df['text'].str.len()

    return df

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
