from decimal import Decimal

from payment_engine import PaymentEngine
# import StringIO


def test_deposits(caplog):
    # capturedOutput = StringIO.StringIO()
    # sys.stdout = capturedOutput
    transaction_data = [{'type': 'deposit', 'client': 1, 'tx': 1, 'amount': Decimal(1.0)},
                        {'type': 'deposit', 'client': 1, 'tx': 1, 'amount': Decimal(1.0)},
                        {'type': 'deposit', 'client': 2, 'tx': 1, 'amount': Decimal(234.0442)}]
    pe = PaymentEngine(transaction_data)
    pe.count_it()
