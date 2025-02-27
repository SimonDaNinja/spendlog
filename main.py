from presenter import BasicPresenter
from ledger import Ledger
from counterParty import CounterPartyDataBase
import datetime
import specificCounterPartyDatabase

from parser import Parser

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
    specificCounterPartyDatabase.populateCounterPartyDatabase()
    parser = Parser()
    parser.parse("raw_input.txt")
    format = "%Y-%m-%d"
    #start = datetime.datetime.strptime("2025-01-24", format)
    #end = datetime.datetime.strptime("2025-02-24", format)
    start = selectDateFromInput("select start date: ")
    end = selectDateFromInput("select end date: ")

    BasicPresenter(start, end).present()