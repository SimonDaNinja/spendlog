from spendlog.parser import InternetbankenParser
from spendlog.presenter import BasicPresenter

from os import path
import datetime
usingCounterPartyDatabaseTemplate = False
try:
    import specificCounterPartyDatabase
except ModuleNotFoundError:
    print("No specific counter party database found; using template.")
    usingCounterPartyDatabaseTemplate = True
    import counterPartyDatabaseTemplate as specificCounterPartyDatabase


DATE_FORMAT = "%Y-%m-%d"

def selectDateFromInput(prompt):
    while True:
        raw_input = input(prompt)
        date = convertToDate(raw_input)
        if date is None:
            print("invalid date!")
            print(f"you wrote: '{raw_input}'")
            print(f"date must follow: '{DATE_FORMAT}'")
        else:
            return date

def convertToDate(dateString):
    try:
        return datetime.datetime.strptime(dateString, DATE_FORMAT)
    except ValueError as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    filename = "transaction_input.txt"
    usingTransactionsTemplate = False

    if not path.exists(filename):
        usingTransactionsTemplate = True
        print("No transaction input file found; using template.")
        filename = "transactions_template.txt"

    isDemo = usingTransactionsTemplate and usingCounterPartyDatabaseTemplate

    presentCapitalChange = False
    presentAllTransactions = False
    if isDemo:
        # These are usually annoying unless you're specifically looking at these,
        # but for demo, let's include them to show they are there (the demo ledger
        # is pretty small anyway)
        presentCapitalChange = True
        presentAllTransactions = True

    specificCounterPartyDatabase.populateCounterPartyDatabase()
    parser = InternetbankenParser()
    parser.parseFromFilename(filename)
    start = datetime.datetime.strptime("2025-03-24", DATE_FORMAT)
    end = datetime.datetime.strptime("2025-03-25", DATE_FORMAT)

    # uncomment these if you want to select dates interactively
    # rather than specify them above:

    # start = selectDateFromInput("select start date: ")
    # end = selectDateFromInput("select end date: ")

    BasicPresenter(start, end).present(presentCapitalChange = presentCapitalChange,
                                       presentAllTransactions = presentAllTransactions)