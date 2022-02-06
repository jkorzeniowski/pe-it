import csv
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(pathname)s:%(lineno)d | %(levelname)s: %(message)s',
                    datefmt='%H:%M:%S')

logger = logging.getLogger(__name__)


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
                    clean_row[key.strip()] = float(val.strip())
                elif key.strip() == 'tx' or key.strip() == 'client':
                    clean_row[key.strip()] = int(val.strip())
                else:
                    clean_row[key.strip()] = val.strip()
            yield clean_row


@dataclass
class ClientAccount:
    available: float
    held: float
    total: float
    locked: bool

    def deposit(self, amount):
        if amount > 0.0:
            self.total += amount
            self.available += amount

    def withdraw(self, amount):
        if self.available > amount:
            self.total -= amount
            self.available -= amount

    def dispute(self, transaction):
        self.held += transaction.amount
        self.available -= transaction.amount

    def resolve_dispute(self, transaction):
        self.held -= transaction.amount
        self.available += transaction.amount

    def chargeback_dispute(self, transaction):
        self.held -= transaction.amount
        self.total -= transaction.amount
        self.locked = True


@dataclass
class TransactionHistory:
    type: str
    client: int
    amount: float


@dataclass
class DisputeHistory:
    client: int
    status: str
