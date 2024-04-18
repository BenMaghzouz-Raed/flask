from flask import jsonify, request
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def CardBinValidator():
    """Extract Credit Card information by Bin Number"""
    with sync_playwright() as p:
        bin_number = request.json['body']

        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
                
        page.goto(f"https://bincheck.io/fr/details/{bin_number}")
        page.wait_for_timeout(2000)
        
        print("Card Bin Number : ", bin_number, "\n")
        
        is_valid_selector = page.inner_text("//div[contains(@class, 'relative') and contains(@class, 'px-5') and contains(@class, 'py-6') and contains(@class, 'mx-auto') and contains(@class, 'max-w-7xl') and contains(@class, '2xl:max-w-7xl') and contains(@class, 'md:mt-5')]")
        
        is_valid = None
        
        if "valid" in is_valid_selector:
            is_valid = True
            print("Is Valid : ", is_valid)
        else:
            is_valid = False
            print("Not Valid")
        
        html = page.content()
        
        soup = BeautifulSoup(html, "html.parser")
        
        values = {
            "valid": is_valid,
            "BIN/IIN": soup.find("td", string="BIN/IIN").find_next_sibling("td").text.strip(),
            "Card Brand": soup.find("td", string="Marque de carte").find_next_sibling("td").text.strip(),
            "Card Type": soup.find("td", string="Type de carte").find_next_sibling("td").text.strip(),
            "Card Level": soup.find("td", string="Niveau de carte").find_next_sibling("td").text.strip(),
            "Issuer / Bank Name": soup.find("td", string="Nom de l'émetteur / Banque").find_next_sibling("td").text.strip(),
            "Issuer / Bank Website": soup.find("td", string="Site Web de l'émetteur / de la banque").find_next_sibling("td").text.strip(),
            "Issuer / Bank Phone": soup.find("td", string="Émetteur / Téléphone de la banque").find_next_sibling("td").text.strip(),
            "ISO Country Name": soup.find("td", string="Nom du pays ISO").find_next_sibling("td").text.strip()
        }
        
        browser.close()
        return jsonify({'result': values}), 200