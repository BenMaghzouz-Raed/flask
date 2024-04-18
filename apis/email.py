from flask import jsonify, request
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime
import smtplib
import dns.resolver
from disposable_email_domains import blocklist

def check_deliverable():
    """Check if an email is deliverable (can receive e-mails)"""
    email = request.json['body']
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    domain = email.split('@')[1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        with smtplib.SMTP(mx_records[0].exchange.to_text()) as server:
            server.verify(email)  # Trying to send a test email (simulation)
            return jsonify(True), 200
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
        return jsonify(False), 200
    except (dns.resolver.NoNameservers, dns.resolver.NoAnswer):
        return jsonify({'error': 'DNS resolution failed'}), 500

def check_disposable():
    """Checks whether an email is disposable or not"""
    email = request.json['body']
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    if email in blocklist:
        return jsonify(True), 200
    else:
        return jsonify(False), 200

def Check_breaches():
    """Extract Breach information from pcdcloud.com which uses Havinbeenpwned API"""
    email = request.json['body']
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.pcloud.com/fr/pass/free-personal-data-breach-checker.html")
        
        email_search = page.wait_for_selector(".StyledComponents__EmailInput-sc-1ds7hcq-3.tbQmL")
        email_search.fill(email)
        email_search.press("Enter")
        page.wait_for_timeout(2000)
        
        check_result = page.inner_text("#email-result-container")
        year_pattern = r'\b\d{4}\b'
        
        try:
            years_list = re.findall(year_pattern, check_result)
            years_list = [int(year) for year in years_list]
            oldest_year = min(years_list)
        except:
            pass
        
        if "Excellentes nouvelles ! Vos informations n'ont été trouvées dans aucune violation de données !" in check_result:
            print("Number of breaches : 0")
            return jsonify({'Number of breaches': 0}), 200
        elif "Nous avons trouvé des données que vous avez saisies dans les violations de données suivantes" in check_result:
            breaches = page.query_selector_all(".StyledComponents__DetailedBreachInfoBox-sc-1ds7hcq-28.kcJCEw")
            
            breach_titles = []
            
            for breach in breaches:
                title_element = breach.query_selector("div:nth-child(1)")
                title = title_element.inner_text()
                breach_titles.append(title) 
            
            for breach in breach_titles:
              print(breach)
          
            print("\nNumber of Breaches : ", len(breaches), "\nOldest Breach : ", oldest_year, "\nAccount min Age : ", datetime.now().year-oldest_year,"\n") 
            return jsonify({'Number of Breaches': len(breaches), 'Oldest Breach': oldest_year, 'Account min Age': datetime.now().year-oldest_year, 'Breaches': breach_titles}), 200
        browser.close()

def facebook_checker():
    """Checks Facebook online presence by e-mail"""
    email = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=True)
    
    page = browser.new_page()
    page.goto("https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0")
    page.fill('input#identify_email', email)
    page.press('input#identify_email', 'Enter')
    time.sleep(2)
    
    try:
        test = page.query_selector('._9o4h').inner_text()
        if "Votre recherche ne donne aucun résultat" in test:
            return jsonify({"result": "NO"})
    except Exception:
        return jsonify({"result": "YES"})
    finally:
        page.close()

def google_checker():
    email = request.json['body']
    browser = sync_playwright().start().firefox.launch(headless=True)

    page = browser.new_page()
    page.goto("https://accounts.google.com/ServiceLogin?hl=fr&passive=true&continue=https://www.google.com/&ec=GAZAmgQ")
    time.sleep(2)

    email_field = page.query_selector('.whsOnd.zHQkBf')
    email_field.fill(email)
    email_field.press('Enter')
    time.sleep(1)

    try:
        test = page.query_selector('div.Ekjuhf.Jj6Lae').inner_text()
        if "Couldn't find your Google Account" in test or "Impossible de trouver votre compte Google" in test:
            return jsonify({"result": "NO"})
    except Exception:
        return jsonify({"result": "YES"})
    finally:
        page.close()

def microsoft_checker():
    email = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=True)

    page = browser.new_page()
    page.goto("https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=22&ct=1710952824&rver=7.3.6960.0&wp=MBI_SSL&wreply=https%3a%2f%2fwww.microsoft.com%2frpsauth%2fv1%2faccount%2fSignInCallback%3fstate%3deyJSdSI6Imh0dHBzOi8vd3d3Lm1pY3Jvc29mdC5jb20vZnItdG4iLCJMYyI6IjQwOTYiLCJIb3N0Ijoid3d3Lm1pY3Jvc29mdC5jb20ifQ&lc=1033&id=74335&aadredir=0")
    time.sleep(0.5)

    page.fill('input#i0116', email)
    page.press('input#i0116', 'Enter')
    time.sleep(0.5)

    try:
        test = page.query_selector('div#i0116Error').inner_text()
        if "That Microsoft account doesn't exist." in test:
            return jsonify({"result": "NO"})
    except:
        return jsonify({"result": "YES"})
    finally:
        page.close()

def instagram_checker():
    """Checks Instagram online presence by e-mail"""
    try:
        email = str(request.json['body'])
        print(email)
    except KeyError:
        return jsonify({'error': 'Email is required'}), 400

    browser = sync_playwright().start().chromium.launch(headless=True)

    def _check_instagram():
        start_time = time.time()
        page = browser.new_page()
        page.goto("https://www.instagram.com/accounts/password/reset/")
        time.sleep(1)

        elements = page.query_selector_all('input')
        email_field = elements[0]
        email_field.fill(email)
        email_field.press('Enter')
        time.sleep(2)

        try:
            test = page.query_selector('._abmp')
            if "Aucun utilisateur trouvé" in test.inner_text() or "No users found" in test.inner_text():
                return {"result": "NO"}
        except Exception:
            return {"result": "YES"}
        finally:
            page.close()

        elapsed_time = time.time() - start_time
        if elapsed_time > 10:  # Adjust the timeout duration as needed
            raise TimeoutError("Function execution exceeded timeout duration")

    try:
        result = _check_instagram()
    except TimeoutError:
        result = {"result": "Timeout"}
    except Exception as e:
        result = {"result": "Error", "message": str(e)}
    finally:
        browser.close()

    return jsonify(result)

def twitter_checker():
    email = request.json['body']
    browser = sync_playwright().start().firefox.launch(headless=True)

    page = browser.new_page()
    page.goto("https://twitter.com/i/flow/signup")
    time.sleep(2)
    page.click('.css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r-lrvibr.r-ywje51.r-usiww2.r-13qz1uu.r-2yi16.r-1qi8awa.r-ymttw5.r-1loqt21.r-o7ynqc.r-6416eg.r-1ny4l3l')
    time.sleep(1)

    elements = page.query_selector_all('.r-30o5oe.r-1dz5y72.r-13qz1uu.r-1niwhzg.r-17gur6a.r-1yadl64.r-deolkf.r-homxoj.r-poiln3.r-7cikom.r-1ny4l3l.r-t60dpp.r-fdjqy7')

    email_field = elements[1]
    email_field.fill(email)
    time.sleep(1)

    try:
        tests = page.query_selector_all('.css-1qaijid.r-bcqeeo.r-qvutc0.r-poiln3')
        test = tests[5].inner_text()
        if "déjà utilisé" in test or "Email has already been taken." in test:
            return jsonify({"result": "YES"})
        else:
            return jsonify({"result": "NO"})
    except Exception:
        return jsonify({"result": "NO"})
    finally:
        page.close()

def netflix_checker():
    email = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=True)

    page = browser.new_page()
    page.goto("https://www.netflix.com/tn-fr/LoginHelp")

    email_field =  page.query_selector("#forgot_password_input")
    email_field.fill(email)
    page.query_selector("button").click()

    time.sleep(2)

    try:
        test = page.query_selector("div.ui-message-contents").inner_text()
        if "Aucun compte" in test or "account" in test:
            return jsonify({"result": "NO"})
    except Exception:
        return jsonify({"result": "YES"})
    finally:
        page.close()

def snapchat_checker():
    email = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://accounts.snapchat.com/accounts/v2/login?continue=%2Faccounts%2Fsso%3Freferrer%3Dhttps%253A%252F%252Fweb.snapchat.com%252F%253Fref%253Dsnapchat_dot_com_login_cta%26tiv_request_info%3DCmsKaQpnCkEEhUtYJiu5iQpNo0oXNiZv0njCchmhwTgpmzdrrNBul%252B5TB1ywaLUTH5qDcmF2xmaHWh%252BRkxW02h9uQzmOvTGdnRIgXHBoJHvJigh%252FLZyw6deXFE6xVtPUejlIIaslgwHpADgYCQ%253D%253D%26client_id%3Dweb-calling-corp--prod&tiv_request_info=CmsKaQpnCkEEhUtYJiu5iQpNo0oXNiZv0njCchmhwTgpmzdrrNBul%2B5TB1ywaLUTH5qDcmF2xmaHWh%2BRkxW02h9uQzmOvTGdnRIgXHBoJHvJigh%2FLZyw6deXFE6xVtPUejlIIaslgwHpADgYCQ%3D%3D")

    email_field = page.query_selector("#accountIdentifier")
    email_field.fill(email)
    page.query_selector("button").click()

    try:
        test = page.wait_for_selector("#error_message", timeout=4000)
        if test:
            if "Nous ne trouvons pas de compte" in test.inner_text() or "We cannot find an account for this email address." in test.inner_text():
                return jsonify({"result": "NO"})
    except Exception:
        try:
            test2 = page.query_selector(".login-challenge-title").inner_text()
            if "Saisir le mot de passe" in test2 or "pass" in test2:
                return jsonify({"result": "YES"})
        except Exception:
            return jsonify({"result": "NO"})
    finally:
        page.close()