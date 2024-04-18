from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pdfplumber
import re

def extract_text_from_textboxes(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text_lines = page.extract_text_lines()
            for line in text_lines:
                text += line['text']
    return text

def extract_information_from_legal_statement(text):
    tracking_number_pattern = r"Tracking Number: \s*(.*?)\s*Please Answer"
    first_response_pattern = r"damaged to the customer'slocation \(please type Yes or No\)\? \s*(.*?)\s*Were"
    second_response_pattern = r"have affected the delivery of this order\(please type Yes or No\)\? \s*(.*?)\s*Please answer"
    grams_pattern = r"kilos\?\s*(.*?)\s* Gram\(s\)"
    kilos_pattern = r"Gram\(s\)\s*(.*?)\s* Kilogram"
    name_pattern = r"Name: \s*(.*?)\s*Carrier:"
    carrier_pattern = r"Carrier: \s*(.*?)\s*We"
    
    tracking_number_match = re.search(tracking_number_pattern, text, re.DOTALL)
    first_response_match = re.search(first_response_pattern, text, re.DOTALL)
    second_response_match = re.search(second_response_pattern, text, re.DOTALL)
    grams_match = re.search(grams_pattern, text, re.DOTALL)
    kilos_match = re.search(kilos_pattern, text, re.DOTALL)
    name_match = re.search(name_pattern, text, re.DOTALL)
    carrier_match = re.search(carrier_pattern, text, re.DOTALL)
    
    tracking_number = tracking_number_match.group(1) if tracking_number_match else None
    first_reponse = first_response_match.group(1).strip().replace(" ", "") if first_response_match else None
    second_reponse = second_response_match.group(1).strip().replace(" ", "") if second_response_match else None
    grams = grams_match.group(1).replace(" ", "") if grams_match else None
    kilos = kilos_match.group(1).replace(" ", "") if kilos_match else None
    name = name_match.group(1).strip().replace(" ", "") if name_match else None
    carrier = carrier_match.group(1).strip() if carrier_match else None

    return tracking_number, first_reponse, second_reponse, grams, kilos, name, carrier

def extract_additional_information():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    pdf_file = request.files['file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if pdf_file and pdf_file.filename.endswith('.pdf'):
        filename = secure_filename(pdf_file.filename)
        pdf_file.save(filename)
        
        extracted_text = extract_text_from_textboxes(filename)
        tracking_number, first_response, second_response, grams, kilos, name, carrier = extract_information_from_legal_statement(extracted_text)
        
        response = {
            'tracking_number': tracking_number,
            'package_delivered_damaged': first_response,
            'delivery_affected': second_response,
            'grams': grams,
            'kilos': kilos,
            'name': name,
            'carrier': carrier
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Invalid file format. Please upload a PDF file'}), 400

