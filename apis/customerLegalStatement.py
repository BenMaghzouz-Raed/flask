from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pdfplumber
import re

app = Flask(__name__)

def extract_text_from_textboxes(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text_lines = page.extract_text_lines()
            for line in text_lines:
                text += line['text']
    return text

def extract_information_from_legal_statement(text):
    name_pattern = r"Last Name & First Name:\s*(.*?)\s*N°"
    address_pattern = r"N°, street, Zip:\s*(.*?)\s*City:"
    city_pattern =  r"City:\s*(.*?)\s*Order Number:"
    order_number_pattern = r"Order Number:\s*(.*?)\s*Order"
    order_tracking_number_pattern = r"Tracking Number:\s*(.*?)\s*Please"
    is_damaged_pattern  = r"The package was damaged \s*(.*?)\s*Please"
    received_order_pattern = r"I did not receive the order \s*(.*?)\s*I received "
    incomplete_order_pattern = r"I received an incomplete order \s*(.*?)\s*I did not"
    item_pattern = r"Item\s+n°:\s*(\d+)\s+Size:\s*(\d+)\s*"
    date_place_pattern = r"Date, place:\s*(.*?)\s*Name:"

    name_match = re.search(name_pattern, text, re.DOTALL)
    address_match = re.search(address_pattern, text, re.DOTALL)
    city_match = re.search(city_pattern, text, re.DOTALL)
    order_number_match = re.search(order_number_pattern, text, re.DOTALL)
    order_tracking_number_match = re.search(order_tracking_number_pattern, text, re.DOTALL)
    is_damaged_match = re.search(is_damaged_pattern, text, re.DOTALL)
    received_order_match = re.search(received_order_pattern, text, re.DOTALL)
    incomplete_order__match = re.search(incomplete_order_pattern, text, re.DOTALL)
    items_matches = re.findall(item_pattern, text)
    date_place_matches = re.search(date_place_pattern, text, re.DOTALL)

    name = name_match.group(1) if name_match else None
    address = address_match.group(1) if address_match else None
    city = city_match.group(1) if address_match else None
    order_number = order_number_match.group(1) if order_number_match else None
    tracking_number = order_tracking_number_match.group(1) if order_number_match else None
    is_damaged = is_damaged_match.group(1) if order_number_match else None
    received_order = received_order_match.group(1) if order_number_match else None
    incomplete_order = incomplete_order__match.group(1) if order_number_match else None
    date_place = date_place_matches.group(1) if order_number_match else None
    
    items = []
    for match in items_matches:
        item_number, item_size = match
        items.append({"item_number": item_number, "item_size": item_size})

    return name, address, city, order_number, tracking_number, is_damaged, received_order, incomplete_order, items, date_place

def extract_customer_legal_statement():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    pdf_file = request.files['file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if pdf_file and pdf_file.filename.endswith('.pdf'):
        filename = secure_filename(pdf_file.filename)
        pdf_file.save(filename)
        
        extracted_text = extract_text_from_textboxes(filename)
        name, address, city, order_number, tracking_number, is_damaged, received_order, incomplete_order, items, date_place = extract_information_from_legal_statement(extracted_text)
        
        response = {
            'name': name,
            'address': address,
            'city': city,
            'order_number': order_number,
            'tracking_number': tracking_number,
            'is_damaged': is_damaged,
            'received_order': received_order,
            'incomplete_order': incomplete_order,
            'items': items,
            'date_place': date_place
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Invalid file format. Please upload a PDF file'}), 400

