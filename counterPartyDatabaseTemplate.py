from spendlog.counterParty import CounterPartyDataBase
from spendlog.ledger import Ledger
import datetime

def applyMortagePayoff(transaction):
    transaction.capitalChange = 1300

def applyPureSaving(transaction):
    transaction.capitalChange = transaction.liquidityChange

def populateCounterPartyDatabase():
    CounterPartyDataBase().addCounterParty(
        aliases = ["Systembolaget"],
        category = "alcohol")
    CounterPartyDataBase().addCounterParty(
        aliases = ["Ica", "ICA SUPERMARKET", "ICA NARA"],
        category = "groceries")
    CounterPartyDataBase().addCounterParty(
        aliases = ["Salary", "SALARY SYSTEM"],
        category = "salary")
