from playwright.sync_api import sync_playwright
from flask import jsonify, request
import time
import phonenumbers
from phonenumbers import geocoder, carrier, parse, is_valid_number
import json

def get_country():
        phone_number = request.json['body']
        try:
            number = phonenumbers.parse(phone_number)
            if is_valid_number(number):
                country = geocoder.country_name_for_number(number, "en")
                return jsonify(country), 200
            else:
                return jsonify({"Invalid phone number"}), 200
        except:
            return jsonify({"Unknown"}), 200

def validate_phone_number():
    phone_number = request.json['body']
    try:
        num_obj = parse(phone_number)
        if is_valid_number(num_obj):
            return jsonify(True), 200
        else:
            return jsonify(False), 200
    except phonenumbers.NumberParseException:
        return jsonify(False), 200

def get_carrier_name():
    phone_number = request.json['body']
    try:
        number = phonenumbers.parse(phone_number)
        if is_valid_number and not disposable(number):
            carrier_name = carrier.name_for_number(number, "en")
            return jsonify(carrier_name), 200
        else:
            return jsonify({"Invalid phone number"}), 200
    except:
        return jsonify('Unknown'), 200
        
def get_line_type():
    phone_number = request.json['body']
    try:
        parsed_number = phonenumbers.parse(phone_number)
        phone_type = phonenumbers.phonenumberutil.number_type(parsed_number)
        if phone_type is phonenumbers.PhoneNumberType.FIXED_LINE:
            return jsonify("Fixed Line"), 200
        elif phone_type is phonenumbers.PhoneNumberType.MOBILE:
            return jsonify("Mobile Line"), 200
        else:
            return jsonify({"Unknown Line Type"}), 200
    except phonenumbers.phonenumberutil.NumberParseException as e:
        return jsonify({"Error"}), 401

def disposable():
    phone_number = request.json['body']
    with open('./apis/disp-numbers.json', 'r') as file:
        data = json.load(file)
        if phone_number in data.keys():
            return jsonify(True), 200
        else:
            return jsonify(False), 200

def facebook_checker_phone():
        """Checks Facebook online presence by e-mail"""
        phone = request.json['body']
        browser = sync_playwright().start().chromium.launch(headless=True)
        
        page = browser.new_page()
        page.goto("https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0")
        page.fill('input#identify_email', phone)
        page.press('input#identify_email', 'Enter')
        time.sleep(2)
        
        try:
            test = page.query_selector('._9o4h').inner_text()
            if "Votre recherche ne donne aucun résultat" in test:
                return jsonify({"Facebook": "NO"})             
        except Exception:
            print("Facebook : YES")
            return jsonify({"Facebook": "YES"})
        finally:
            page.close()
    
def google_checker_phone():
    phone = request.json['body']
    try:
        browser = sync_playwright().start().firefox.launch(headless=True)
        
        page = browser.new_page()
        page.goto("https://accounts.google.com/ServiceLogin?hl=fr&passive=true&continue=https://www.google.com/&ec=GAZAmgQ")
        time.sleep(2)

        email_field = page.query_selector('.whsOnd.zHQkBf')
        email_field.fill(phone)
        email_field.press('Enter')            
        time.sleep(1)
        
        try:
            test = page.query_selector('div.Ekjuhf.Jj6Lae').inner_text()
            if "Couldn't find your Google Account" in test or "Impossible de trouver votre compte Google" in test:
                print("Google : NO")
                return jsonify({"Google": "NO"})
            else:
                return jsonify({"Google": "YES"})
        except Exception as e:
            return jsonify({"Google": "YES"})
            
    except Exception as e:
        pass

def microsoft_checker_phone():
    phone = request.json['body']
    try:
        browser = sync_playwright().start().chromium.launch(headless=True)
        
        page = browser.new_page()
        page.goto("https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=22&ct=1710952824&rver=7.3.6960.0&wp=MBI_SSL&wreply=https%3a%2f%2fwww.microsoft.com%2frpsauth%2fv1%2faccount%2fSignInCallback%3fstate%3deyJSdSI6Imh0dHBzOi8vd3d3Lm1pY3Jvc29mdC5jb20vZnItdG4iLCJMYyI6IjQwOTYiLCJIb3N0Ijoid3d3Lm1pY3Jvc29mdC5jb20ifQ&lc=1033&id=74335&aadredir=0")
        time.sleep(0.5)

        page.fill('input#i0116', phone)
        page.press('input#i0116', 'Enter')
        time.sleep(0.5)
        
        test = page.query_selector('div#i0116Error').inner_text()
        if "That Microsoft account doesn't exist." in test:
            print("Microsoft : NO")
            return jsonify({"Microsoft": "NO"})
    except Exception:
        print("Microsoft : YES")
        return jsonify({"Microsoft": "YES"})
    
    finally:
        page.close()

def twitter_checker_phone():
    phone = request.json['body']
    browser = sync_playwright().start().firefox.launch(headless=False)  
    page = browser.new_page() 
    page.goto("https://twitter.com/i/flow/login") 
    time.sleep(1)

    email_field = page.query_selector('.r-30o5oe.r-1dz5y72.r-13qz1uu.r-1niwhzg.r-17gur6a.r-1yadl64.r-deolkf.r-homxoj.r-poiln3.r-7cikom.r-1ny4l3l.r-t60dpp.r-fdjqy7')
    email_field.fill(phone)
    email_field.press("Enter")
    time.sleep(1)

    try:
        test = page.query_selector(".css-1qaijid.r-bcqeeo.r-qvutc0.r-poiln3").inner_text()
        if "Désolé" in test or "Sorry":
            print("Twitter: NO")
            return jsonify({"Twitter": "NO"})
        else:
            print("Twitter: YES")
            return jsonify({"Twitter": "YES"})
    except:
        print("Twitter: YES")
        return jsonify({"Twitter": "YES"})

def instagram_checker_phone():
    phone = request.json['body']
    try:
        browser = sync_playwright().start().chromium.launch(headless=True)
        
        page = browser.new_page()
        page.goto("https://www.instagram.com/accounts/password/reset/")
        time.sleep(1)

        elements = page.query_selector_all('input')
        email_field = elements[0]
        email_field.fill(phone)
        email_field.press('Enter')
        time.sleep(2)

        try:
            test = page.query_selector('._abmp')
            if "Aucun utilisateur trouvé" in test.inner_text() or "No users found":
                print("Instagram : NO")
                return jsonify({"Instagram": "NO"})
            else:
                print("Instagram : YES")
                return jsonify({"Instagram": "YES"})
        except Exception as e:
            print("Instagram : YES")
            return jsonify({"Instagram": "YES"})
            
    except Exception as e:
        pass
    
    finally:
        page.close()