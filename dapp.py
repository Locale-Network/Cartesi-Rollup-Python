from os import environ
import json
import requests

ROLLUP_SERVER_URL = "http://localhost:5004"

def hex2str(hex_value):
    return bytes.fromhex(hex_value[2:]).decode('utf-8')

def str2hex(string_value):
    return '0x' + string_value.encode('utf-8').hex()

def send_notice(payload):
    notice_url = f"{ROLLUP_SERVER_URL}/notice"
    response = requests.post(notice_url, json={'payload': str2hex(json.dumps(payload))})
    print(f"Notice sent, received status: {response.status_code}, body: {response.text}")

def send_report(message):
    report_url = f"{ROLLUP_SERVER_URL}/report"
    response = requests.post(report_url, json={'payload': str2hex(message)})
    print(f"Report sent, received status: {response.status_code}, body: {response.text}")

class LoanRestructure:
    def __init__(self, prime_rate, loan_amount, loan_term_years):
        self.prime_rate = prime_rate
        self.loan_amount = loan_amount
        self.loan_term_years = loan_term_years

    def get_max_interest_rate(self):
        if self.loan_amount > 50000 and self.loan_term_years < 7:
            return self.prime_rate + 2.25
        elif self.loan_amount > 50000 and self.loan_term_years >= 7:
            return self.prime_rate + 2.75
        else:
            return self.prime_rate + 4.75

    def restructure_interest_rate(self, current_rate, borrower_income, borrower_expenses):
        dscr = borrower_income / borrower_expenses
        new_rate = current_rate
        if dscr < 1.25:
            new_rate -= 0.5
            if dscr < 1.0:
                new_rate -= 1.0
            if dscr < 0.75:
                new_rate -= 2.0

            return min(new_rate, self.get_max_interest_rate())
        return current_rate
    
def handle_advance(data):
    print(f"Received advance request: {json.dumps(data)}")
    try:
        input_data = json.loads(hex2str(data['payload']))
        prime_rate = input_data['prime_rate']
        loan_amount = input_data['loan_amount']
        loan_term = input_data['loan_term']
        current_rate = input_data['current_rate']
        borrower_income = input_data['borrower_income']
        borrower_expenses = input_data['borrower_expenses']

        restructure = LoanRestructure(prime_rate, loan_amount, loan_term)
        new_interest_rate = restructure.restructure_interest_rate(current_rate, borrower_income, borrower_expenses)

        response_payload = {'new_interest_rate': new_interest_rate}
        send_notice(response_payload)
        return 'accept'

    except Exception as e:
        print(f"Error processing advance request: {e}")
        send_report(f"Error processing advance request: {str(e)}")
        return 'reject'

def handle_inspect(data):
    print(f"Received inspect request: {json.dumps(data)}")
    return 'accept'

def main():
    handlers = {
        "advance_state": handle_advance,
        "inspect_state": handle_inspect,
    }

    finish = {"status": "accept"}

    while True:
        finish_req = requests.post(f"{ROLLUP_SERVER_URL}/finish", json=finish)
        if finish_req.status_code == 202:
            print("No pending rollup request, retrying...")
        else:
            rollup_req = finish_req.json()
            handler = handlers.get(rollup_req["request_type"])
            finish["status"] = handler(rollup_req["data"])

if __name__ == "__main__":
    main()