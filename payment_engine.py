import sys
from typing import Iterable

from utils import ClientAccount, DisputeHistory, TransactionHistory, UnsupportedTransactionTypeError, \
    WrongNumberOfArgumentsError, load_and_prepare_data


class PaymentEngine:
    """
    PaymentEngine - logic responsible for calculation of the clients bank accounts statuses
    given set of transactions data.

    :param transactions_data - raw data containing type, client, tx, amount data set
    """
    def __init__(self, transactions_data: Iterable):
        self.__storage = {}
        self.__transactions_history = {}
        self.__transactions_data = transactions_data
        self.__dispute_history = {}
        self.transaction_types = ['deposit', 'withdrawal', 'dispute', 'resolve', 'chargeback']

    def run_engine(self):
        for transaction in self.__transactions_data:
            if transaction['client'] not in self.__storage:
                self.create_new_user(transaction['client'])
            self.make_transaction(transaction)

    def make_transaction(self, transaction: dict):
        if transaction['type'] not in self.transaction_types:
            raise UnsupportedTransactionTypeError("Unsupported transaction type found in csv file")
        if transaction['type'] == 'deposit':
            if transaction['tx'] not in self.__transactions_history:
                if not self.__storage[transaction['client']].locked:
                    self.save_transaction_in_history(transaction)
                    self.__storage[transaction['client']].deposit(transaction['amount'])
        if transaction['type'] == 'withdrawal':
            if transaction['tx'] not in self.__transactions_history:
                if not self.__storage[transaction['client']].locked:
                    self.save_transaction_in_history(transaction)
                    self.__storage[transaction['client']].withdraw(transaction['amount'])
        if transaction['type'] == 'dispute':
            if transaction['tx'] in self.__transactions_history:
                transaction_disputed = self.get_transaction_by_tx(transaction['tx'])
                if transaction['client'] == transaction_disputed.client:
                    self.save_dispute_in_history(transaction)
                    self.__storage[transaction['client']].dispute(self.get_transaction_by_tx(transaction['tx']))
        if transaction['type'] == 'resolve':
            if transaction['tx'] in self.__transactions_history:
                transaction_disputed = self.get_transaction_by_tx(transaction['tx'])
                if transaction['client'] == transaction_disputed.client:
                    if transaction['tx'] in self.__dispute_history and \
                            self.__dispute_history[transaction['tx']].status == 'ongoing':
                        self.__storage[transaction['client']].resolve_dispute(
                            self.get_transaction_by_tx(transaction['tx']))
                        self.__dispute_history[transaction['tx']].status = 'resolve'
        if transaction['type'] == 'chargeback':
            if transaction['tx'] in self.__transactions_history:
                transaction_disputed = self.get_transaction_by_tx(transaction['tx'])
                if transaction['client'] == transaction_disputed.client:
                    if transaction['tx'] in self.__dispute_history and \
                            self.__dispute_history[transaction['tx']].status == 'ongoing':
                        self.__storage[transaction['client']].chargeback_dispute(
                            self.get_transaction_by_tx(transaction['tx']))
                        self.__dispute_history[transaction['tx']].status = 'chargeback'

    def create_new_user(self, client_id: int):
        self.__storage[client_id] = ClientAccount(**{'available': 0.0, 'held': 0.0,
                                                     'total': 0.0, 'locked': False})

    def save_transaction_in_history(self, transaction):
        if transaction['type'] == 'deposit' or transaction['type'] == 'withdrawal':
            self.__transactions_history[transaction['tx']] = \
                TransactionHistory(**{'type': transaction['type'], 'client': transaction['client'],
                                      'amount': transaction['amount']})
        else:
            self.__transactions_history[transaction['tx']] = \
                TransactionHistory(**{'type': transaction['type'], 'client': transaction['client'],
                                      'amount': 0.0})

    def save_dispute_in_history(self, transaction):
        self.__dispute_history[transaction['tx']] = DisputeHistory(**{'client': transaction['client'],
                                                                      'status': 'ongoing'})

    def get_transaction_by_tx(self, tx: int):
        if tx in self.__transactions_history:
            return self.__transactions_history[tx]

    def print_results(self):
        print("client,available,held,total,locked")
        for client, entry in self.__storage.items():
            print(f"{client},{round(entry.available, 4)},{round(entry.held, 4)},"
                  f"{round(entry.total, 4)},{str(entry.locked).lower()}")


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        raise WrongNumberOfArgumentsError(f"PaymentEngine app takes only 1 argument, "
                                          f"the csv file with transactions data. "
                                          f"Incorrect number of arguments passed of {len(sys.argv)}")
    transactions = load_and_prepare_data(sys.argv[1])
    engine = PaymentEngine(transactions)
    engine.run_engine()
    engine.print_results()
