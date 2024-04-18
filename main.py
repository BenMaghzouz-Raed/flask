from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from apis import email 
from apis import ipAddress
from apis import creditCard
from apis import phone
from apis import requestAdditionalInformation
from apis import customerLegalStatement
from subprocess import Popen, PIPE
import sys

p = Popen([sys.executable, "-m", "playwright", "install"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = p.communicate()
print(output)

app = Flask(__name__)

# API for email information retrieval
app.route('/v1/email/check_disposable', methods=['POST'])(email.check_disposable)
app.route('/v1/email/check_deliverable', methods=['POST'])(email.check_deliverable)
app.route('/v1/email/check_breaches', methods=['POST'])(email.Check_breaches)
app.route('/v1/email/facebook_checker', methods=['POST'])(email.facebook_checker)
app.route('/v1/email/google_checker', methods=['POST'])(email.google_checker)
app.route('/v1/email/instagram_checker', methods=['POST'])(email.instagram_checker)
app.route('/v1/email/twitter_checker', methods=['POST'])(email.twitter_checker)

# API for IP information retrieval
app.route('/v1/ip/proxy-threat', methods=['POST'])(ipAddress.GetProxyAndThreat)
app.route('/v1/ip/type', methods=['POST'])(ipAddress.ipType)
app.route('/v1/ip/is-blacklisted', methods=['POST'])(ipAddress.isBlackListed)
app.route('/v1/ip/open-ports', methods=['POST'])(ipAddress.OpenPortsScanner)

# API for Credit Card information retrieval
app.route('/v1/credit-card', methods=['POST'])(creditCard.CardBinValidator)

# API for phone information retrieval
app.route('/v1/phone/check-disposable', methods=['POST'])(phone.disposable)
app.route('/v1/phone/get-country', methods=['POST'])(phone.get_country)
app.route('/v1/phone/validate-phone-number', methods=['POST'])(phone.validate_phone_number)
app.route('/v1/phone/get-carrier-name', methods=['POST'])(phone.get_carrier_name)
app.route('/v1/phone/get-line-type', methods=['POST'])(phone.get_line_type)
app.route('/v1/phone/facebook-checker', methods=['POST'])(phone.facebook_checker_phone)
app.route('/v1/phone/instagram-checker', methods=['POST'])(phone.instagram_checker_phone)


# API for pdf parsing
app.route('/v1/pdf/request-additional-information', methods=['POST'])(requestAdditionalInformation.extract_additional_information)
app.route('/v1/pdf/customer-legal-statement', methods=['POST'])(customerLegalStatement.extract_customer_legal_statement)

@app.route('/')
def index():
  return jsonify({'Result': 'Server Running'}), 200

# Error handler for 404 Not Found error
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'API Not Found'}), 404

# Error handler for 400 Bad Request error
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad Request'}), 400

# Error handler for all other HTTP errors
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(port=5000)
