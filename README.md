# payment-engine

### Introduction
Dummy payment engine that reads a series of transactions from a CSV file,
handles disputes and chargebacks and then outputs the state of clients' accounts.
Data is being streamed to the engine via a generator rather than loading billions of records to memory.
### Python version
The application was written using Python 3.9, probably it will work with older versions of Python 3.
### How to run
```python3 payment_engine.py transactions.csv```  

The app takes only one argument - the CSV file with transactions data.
Output is written to stdout in CSV-like format and can be redirected in your shell.


### Unit tests

I've added a couple of unit tests that are checking positive and also negative scenarios
that popped up during implementation. Framework used: `pyTest`.
Simply install `pyTest` using ```pip install -r tests/unit_tests/requirements.txt```
and run tests by running ```pytest```.

### Details
Although data is being streamed to the engine via a generator to achieve high memory efficiency,
all the transactions' history is stored in `dataclass` to support operations
like `dispute`, `chargeback`, and `resolve`.  

If I had more time, then I would choose to store transaction history in a database
like `SQLite` rather than keeping a thousand records in memory,
so I fully expect the app to blow up when fed with GBs of data.
Since I have limited time to only 2 days then I chose not to flirt with databases,
and I don't have much experience with writing apps that are using databases.
Nevertheless, I've chosen `dataclass` to store the info since it's rather good when
it comes to memory efficiency.

### Things to thought through
Things that came out during implementation:
- can we deposit by a negative value? I've blocked that possibility.
- dispute operation - it wasn't specified what happens when the client doesn't have
enough `available` resources,
are we decreasing `available` below zero? I left that possibility.
- can other users dispute another client's transactions? I've blocked that possibility.
- what does `lock` user mean after `chargeback` operation? I assumed that client can't either make
a deposit or withdraw the resources, and I implemented it in that manner.
