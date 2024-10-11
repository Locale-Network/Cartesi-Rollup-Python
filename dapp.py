from os import environ
import logging
import json
import requests
from functools import partial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a constant for the base URL
ROLLUP_SERVER = environ.get("ROLLUP_HTTP_SERVER_URL")
if not ROLLUP_SERVER:
    logger.error("ROLLUP_HTTP_SERVER_URL environment variable is not set.")
    exit(1)

logger.info(f"HTTP rollup server URL is {ROLLUP_SERVER}")

# More efficient hex to string conversion
hex2str = lambda h: bytes.fromhex(h[2:]).decode('utf-8')
str2hex = lambda s: '0x' + s.encode('utf-8').hex()

# Combine send_notice and send_report into a single function
def send_server_request(endpoint, payload):
    url = f"{ROLLUP_SERVER}/{endpoint}"
    try:
        response = requests.post(url, json={'payload': str2hex(json.dumps(payload) if endpoint == 'notice' else payload)})
        response.raise_for_status()
        logger.info(f"{endpoint.capitalize()} sent successfully, status: {response.status_code}, body: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Failed to send {endpoint}: {e}")

# Create partial functions for notice and report
send_notice = partial(send_server_request, 'notice')
send_report = partial(send_server_request, 'report')

class LoanRestructure:
    def __init__(self, prime_rate, loan_amount, loan_term_years):
        self.prime_rate = prime_rate
        self.loan_amount = loan_amount
        self.loan_term_years = loan_term_years

    def get_max_interest_rate(self):
        if self.loan_amount > 50000:
            return self.prime_rate + (2.75 if self.loan_term_years >= 7 else 2.25)
        return self.prime_rate + 4.75

    def restructure_interest_rate(self, current_rate, borrower_income, borrower_expenses):
        dscr = borrower_income / borrower_expenses
        if dscr >= 1.25:
            return current_rate
        
        new_rate = current_rate - 0.5
        if dscr < 1.0:
            new_rate -= 1.0
        if dscr < 0.75:
            new_rate -= 2.0
        
        return min(new_rate, self.get_max_interest_rate())

def handle_advance(data):
    logger.info(f"Received advance request: {json.dumps(data)}")
    try:
        input_data = json.loads(hex2str(data['payload']))
        restructure = LoanRestructure(input_data['prime_rate'], input_data['loan_amount'], input_data['loan_term'])
        new_interest_rate = restructure.restructure_interest_rate(
            input_data['current_rate'], input_data['borrower_income'], input_data['borrower_expenses']
        )
        logger.info(f"New Interest Rate: {new_interest_rate}")
        send_notice({'new_interest_rate': new_interest_rate})
        return 'accept'
    except Exception as e:
        logger.error(f"Error processing advance request: {e}")
        send_report(f"Error processing advance request: {str(e)}")
        return 'reject'

def handle_inspect(data):
    logger.info(f"Received inspect request data: {json.dumps(data)}")
    return "accept"

handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    try:
        logger.info("Sending finish request to rollup server")
        response = requests.post(f"{ROLLUP_SERVER}/finish", json=finish)
        response.raise_for_status()

        if response.status_code == 202:
            logger.info("No pending rollup request, retrying...")
        else:
            rollup_request = response.json()
            handler = handlers.get(rollup_request["request_type"])
            finish["status"] = handler(rollup_request["data"]) if handler else "reject"
    except requests.RequestException as e:
        logger.error(f"Error communicating with rollup server: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")