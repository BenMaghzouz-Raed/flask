from flask import request, jsonify
from playwright.sync_api import sync_playwright
import re
from bs4 import BeautifulSoup
import socket


def GetProxyAndThreat():
    """Retrieves Proxy infos about the IP and determines whether it's harmful or not"""
    ip_address = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"https://scamalytics.com/ip/{ip_address}")
    
    risk_level = page.inner_text('.panel_title.high_risk')
    proxy_data = page.query_selector_all("//tr[th[contains(text(), 'Anonymizing VPN') or contains(text(), 'Tor Exit Node') or contains(text(), 'Server') or contains(text(), 'Public Proxy') or contains(text(), 'Web Proxy') or contains(text(), 'Search Engine Robot')]]")
    country_raw =page.query_selector("//tr[th[contains(text(), 'Country Name')]]").inner_text()
    country = country_raw.split('Country Name')[1].strip()
    
    result = {
        'country': country,
        'harmful': True if "Low Risk" not in risk_level else False,
        'proxy_data': {}
    }
    
    for data in proxy_data:
        key_element = data.query_selector('th')
        value_element = data.query_selector('td > div')
        if key_element and value_element:
            key = key_element.inner_text()
            value = value_element.inner_text()
            result['proxy_data'][key] = value
    
    return jsonify(result), 200

def ipType():
    """Retrieves IP Type of the IP Address, can be: COM|ORG|GOV|MIL|EDU|LIB|CDN|ISP|MOB|DCH|SES|RSV"""
    ip_address = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=True)
    page = browser.new_page()

    if "." in ip_address:
        page.goto(f"https://en.ipshu.com/ipv4/{ip_address}")
    elif ":" in ip_address:
        page.goto(f"https://en.ipshu.com/ipv6/{ip_address}")
    
    html_content = page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    main_entities = soup.find_all('div', itemprop='mainEntity')
    
    if len(main_entities) >= 10:
        target_div = main_entities[9]
        paragraphs = target_div.find_all("p")

        if len(paragraphs) >= 2:
            second_paragraph = paragraphs[1]
            text = second_paragraph.get_text()
            
            pattern = r'\b(COM|ORG|GOV|MIL|EDU|LIB|CDN|ISP|MOB|DCH|SES|RSV)\b'
            match = re.search(pattern, text)
            if match:
                usage_type = match.group(0)
                return jsonify({'result': usage_type}), 200
            else:
                return jsonify({'Unknown'}), 400
        else:
            return jsonify({'Unknown'}), 400
    
def isBlackListed():
    """Checks whether an IP is blacklisted or not and lists the blacklists"""
    ip_address = request.json['body']
    browser = sync_playwright().start().chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(f"https://www.blacklistmaster.com/check?t={ip_address}")
    page.click('.inputbox')
    page.keyboard.press('Enter')
    page.wait_for_timeout(5000)  # Wait for 5 seconds for the page to load
    
    html_content = page.content()
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all("tr")
    blacklist_list = []
    
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 3:
            status = cells[2].text.strip()
            if status == "Listed":
                blacklist = cells[0].text.strip()
                blacklist_list.append(blacklist)
    
    if len(blacklist_list) > 0:
        return jsonify({"is_blacklisted": "Yes", "blacklists": blacklist_list}), 200
    else:
        return jsonify({"is_blacklisted": "No"}), 200
        
def OpenPortsScanner():
    ip_address = request.json['body']
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389]
    open_ports = []
    for port in common_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip_address, port))
            if result == 0:
                open_ports.append(port)
            s.close()
        except KeyboardInterrupt:
            print("\nExiting...")
            exit()
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting...")
            exit()
        except socket.error:
            print("Couldn't connect to server")
            exit()
    return jsonify({"open_ports": open_ports}), 200
        
