import sys

import pytest

from payment_engine import PaymentEngine
from tests.unit_tests.utils import capture_stdout, generate_test_data


def test_deposit_positive():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1.0'},
         {'type': 'deposit', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'deposit', 'client': '2', 'tx': '3', 'amount': '234.0442'},
         {'type': 'deposit', 'client': '2', 'tx': '4', 'amount': '254.044772'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,2.0,0.0,2.0,false\n2,488.089,0.0,488.089,false\n"


def test_deposit_negative():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1.0'},
         {'type': 'deposit', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'deposit', 'client': '1', 'tx': '3', 'amount': '-23'},
         {'type': 'deposit', 'client': '1', 'tx': '4', 'amount': '0'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,2.0,0.0,2.0,false\n"


def test_withdraw_positive():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'deposit', 'client': '2', 'tx': '2', 'amount': '1.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '3', 'amount': '1420.0'},
         {'type': 'withdrawal', 'client': '2', 'tx': '4', 'amount': '1.0'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,1.0,0.0,1.0,false\n2,1.0,0.0,1.0,false\n"


def test_withdraw_negative():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '12.2'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '13.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '3', 'amount': '12.1'},
         {'type': 'deposit', 'client': '2', 'tx': '4', 'amount': '1'},
         {'type': 'withdrawal', 'client': '2', 'tx': '5', 'amount': '0.9999'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,0.1,0.0,0.1,false\n2,0.0001,0.0,0.0001,false\n"


@pytest.mark.parametrize(('tx', 'expected_outcome'), [
    (1, "TransactionHistory(type='deposit', client=1, amount=1421.0)"),
    (2, "TransactionHistory(type='deposit', client=2, amount=1.0)")])
def test_transaction_history(tx, expected_outcome):
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'deposit', 'client': '2', 'tx': '2', 'amount': '1.0'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    assert str(pe.get_transaction_by_tx(tx)) == expected_outcome


def test_dispute_after_deposit():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1419.0,1.0,1420.0,false\n"


def test_dispute_after_withdrawal():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'deposit', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1421.0,1.0,1422.0,false\n"


def test_dispute_by_another_client():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '2', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,1420.0,0.0,1420.0,false\n2,0.0,0.0,0.0,false\n"


def test_dispute_available_below_zero():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1000.0324'},
         {'type': 'dispute', 'client': '1', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,-579.0648,1000.0324,420.9676,false\n"


def test_resolve_dispute_positive():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'},
         {'type': 'resolve', 'client': '1', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1420.0,0.0,1420.0,false\n"


def test_resolve_dispute_by_another_client():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'},
         {'type': 'resolve', 'client': '2', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,1419.0,1.0,1420.0,false\n2,0.0,0.0,0.0,false\n"


def test_resolve_dispute_with_wrong_tx():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'},
         {'type': 'resolve', 'client': '1', 'tx': '1'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1419.0,1.0,1420.0,false\n"


def test_chargeback_dispute_by_another_client():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'},
         {'type': 'chargeback', 'client': '2', 'tx': '2'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n" \
                                         "1,1419.0,1.0,1420.0,false\n2,0.0,0.0,0.0,false\n"


def test_chargeback_dispute_with_wrong_tx():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'},
         {'type': 'chargeback', 'client': '1', 'tx': '1'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1419.0,1.0,1420.0,false\n"


def test_chargeback_dispute_client_cant_operate_as_locked():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'dispute', 'client': '1', 'tx': '2'},
         {'type': 'chargeback', 'client': '1', 'tx': '2'},
         {'type': 'deposit', 'client': '1', 'tx': '3', 'amount': '22.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '4', 'amount': '3.0'}])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1419.0,0.0,1419.0,true\n"


def test_transaction_id_not_unique():
    captured_output = capture_stdout()
    prepared_data = generate_test_data(
        [{'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1421.0'},
         {'type': 'withdrawal', 'client': '1', 'tx': '2', 'amount': '1.0'},
         {'type': 'deposit', 'client': '1', 'tx': '1', 'amount': '1.0'},
         ])
    pe = PaymentEngine(prepared_data)
    pe.run_engine()
    pe.print_results()
    assert captured_output.getvalue() == "client,available,held,total,locked\n1,1420.0,0.0,1420.0,false\n"
