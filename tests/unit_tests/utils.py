import sys
from io import StringIO


def generate_test_data(test_data):
    for row in test_data:
        clean_row = {}
        for key, val in row.items():
            if key.strip() == 'amount':
                clean_row[key.strip()] = float(val.strip())
            elif key.strip() == 'tx' or key.strip() == 'client':
                clean_row[key.strip()] = int(val.strip())
            else:
                clean_row[key.strip()] = val.strip()
        yield clean_row


def capture_stdout():
    captured_output = StringIO()
    sys.stdout = captured_output
    return captured_output
