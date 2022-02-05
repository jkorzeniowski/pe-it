import csv
import sys
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


class WrongNumberOfArgumentsError(TypeError):
    pass


class UnsupportedTransactionTypeError(TypeError):
    pass


def load_and_prepare_data(filename: str):
    with open(filename, 'r') as csv_data:
        csv_data = csv.DictReader(csv_data)
        for row in csv_data:
            clean_row = {}
            for key, val in row.items():
                if key.strip() == 'amount':
                    clean_row[key.strip()] = Decimal(val.strip())
                elif key.strip() == 'tx' or key.strip() == 'client':
                    clean_row[key.strip()] = int(val.strip())
                else:
                    clean_row[key.strip()] = val.strip()
            yield clean_row


@dataclass
class ClientAccount:
    available: Decimal
    held: Decimal
    total: Decimal
    locked: Decimal

    def deposit(self, amount):
        self.total += amount
        self.available += amount


class PaymentEngine:
    def __init__(self, transactions_data: Iterable):
        self.__storage = {}
        self.__transactions_data = transactions_data
        self.transaction_types = ['deposit', 'withdrawal']

    def count_it(self):  # TODO: name to be changed
        for transaction in self.__transactions_data:
            if transaction['client'] in self.__storage:
                self.make_transaction(transaction)
            else:
                self.create_new_user(transaction['client'])
                self.make_transaction(transaction)

    def make_transaction(self, transaction: dict):
        if transaction['type'] not in self.transaction_types:
            raise UnsupportedTransactionTypeError("Unsupported transaction type found in csv file")
        if transaction['type'] == 'deposit':
            self.__storage[transaction['client']].deposit(transaction['amount'])
        if transaction['type'] == 'another_transaction':  # TODO: to be continued
            pass

    def create_new_user(self, client_id: int):
        self.__storage[client_id] = ClientAccount(**{'available': Decimal('0'), 'held': Decimal('0'),
                                                     'total': Decimal('0'), 'locked': Decimal('0')})

    def prepare_stdout(self):
        print("client,available,held,total,locked")
        for client, entry in self.__storage.items():
            print(f"{client},{entry.available},{entry.held},{entry.total},{entry.locked}")


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        raise WrongNumberOfArgumentsError(f"PaymentEngine app takes only 1 argument, "
                                          f"the csv file with transactions data. "
                                          f"Incorrect number of arguments passed of {len(sys.argv)}")

    transactions = load_and_prepare_data(sys.argv[1])
    engine = PaymentEngine(transactions)
    engine.count_it()
    engine.prepare_stdout()

    # payment_engine = PaymentEngine(transactions)
