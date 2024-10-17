# Python DApp Template for Loan Restructuring

This repository contains a template for a Python-based Locale Lending Decentralized Application (DApp) designed to run on the Cartesi platform. The DApp specializes in loan restructuring calculations based on various financial parameters.

## Overview

The main application logic is contained in the `dapp.py` file, which implements a loan restructuring algorithm. This DApp demonstrates how to:

- Interact with the Cartesi Rollup HTTP server
- Handle advance and inspect state requests
- Implement business logic for loan interest rate restructuring
- Utilize environment variables for configuration
- Implement error handling and logging

## Key Features

1. **Loan Restructuring Logic**: Calculates new interest rates based on:
   - Prime rate
   - Loan amount
   - Loan term
   - Borrower's income and expenses
   - Debt Service Coverage Ratio (DSCR)

2. **Rollup Integration**: Communicates with the Cartesi Rollup server to process requests and send notices/reports.

3. **Hexadecimal Conversion**: Efficiently converts between hexadecimal and string formats for payload handling.

4. **Error Handling**: Implements robust error handling and logging throughout the application.

## Setup and Configuration

1. Ensure Python 3.x is installed on your system.
2. Set the `ROLLUP_HTTP_SERVER_URL` environment variable to the appropriate Cartesi Rollup server URL.

## Usage

The DApp processes two types of requests:

1. `advance_state`: Handles loan restructuring calculations based on input data.
2. `inspect_state`: Logs inspection requests (currently returns "accept" without further processing).

Input data for loan restructuring should be provided in JSON format, including:
- `prime_rate`
- `loan_amount`
- `loan_term`
- `current_rate`
- `borrower_income`
- `borrower_expenses`

## Development and Extension

To extend or modify this DApp:

1. Update the `LoanRestructure` class in `dapp.py` to adjust the restructuring logic.
2. Modify the `handle_advance` and `handle_inspect` functions to change request processing behavior.
3. Add new handler functions and update the `handlers` dictionary for additional request types.

## Logging

The application uses Python's `logging` module to provide informative console output. Log level is set to `INFO` by default.
