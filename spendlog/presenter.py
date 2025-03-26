from spendlog.ledger import Ledger, TimeRange
from spendlog.counterParty import CounterPartyDataBase

class Presenter:
    def __init__(self):
        pass

    def present(self):
        pass

class BasicPresenter(Presenter):
    def __init__(self, start, end):
        self.timeRange = TimeRange(start, end)
        self.fetchTags()
        self.fetchCategories()
        self.fetchCounterPartyAliases()

    def present(self, presentCapitalChange = False, presentAllTransactions = False):
        print(f"Summary of economy between {self.timeRange.start} and {self.timeRange.end}")
        print( "========================================================")

        if presentAllTransactions:
            print("All transactions:")
            transactions = list(Ledger().getTransactions(timeRange = self.timeRange))
            transactions.sort(key = lambda x : (x.date, x.liquidityChange, x. capitalChange, x.counterPartyAlias))
            for transaction in transactions:
                print("  " + str(transaction))
            print( "========================================================")

        print("Tags:")
        for tag in self.tags:
            print(f"  {tag}:")
            print(f"    liquidity: {Ledger().getTotalLiquidityChange(timeRange = self.timeRange, requiredTags = [tag])}")
            if presentCapitalChange:
                print(f"    capital change: {Ledger().getTotalCapitalChange(requiredTags = [tag])}")
        print( "========================================================")

        print("Categories:")
        self.categories = list(self.categories)
        self.categories.sort(key = lambda x : Ledger().getTotalLiquidityChange(timeRange = self.timeRange, requiredCategory = x))
        for category in self.categories:
            print(f"  {category}:")
            print(f"    liquidity: {Ledger().getTotalLiquidityChange(timeRange = self.timeRange, requiredCategory = category)}")
            if presentCapitalChange:
                print(f"    capital change: {Ledger().getTotalCapitalChange(timeRange = self.timeRange, requiredCategory = category)}")
        print( "========================================================")

        print("Counter Parties:")
        self.counterPartyAliases = list(self.counterPartyAliases)
        self.counterPartyAliases.sort(key = lambda x : Ledger().getTotalLiquidityChange(timeRange = self.timeRange, requiredCounterParty = x))
        for counterPartyAlias in self.counterPartyAliases:
            print(f"  {counterPartyAlias}:")
            print(f"    liquidity: {Ledger().getTotalLiquidityChange(timeRange = self.timeRange, requiredCounterParty = counterPartyAlias)}")
            if presentCapitalChange:
                print(f"    capital change: {Ledger().getTotalCapitalChange(timeRange = self.timeRange, requiredCounterParty = counterPartyAlias)}")
        print( "========================================================")

        print("Total:")
        print(f"  liquidity: {Ledger().getTotalLiquidityChange(timeRange = self.timeRange)}")
        print(f"  capital change: {Ledger().getTotalCapitalChange(timeRange = self.timeRange)}")
        print(f"  net change: {Ledger().getTotalNetChange(timeRange = self.timeRange)}")



    def fetchTags(self):
        transactions = Ledger().getTransactions(self.timeRange)
        self.tags = set()
        for transaction in transactions:
            self.tags |= set(transaction.getTags())

    def fetchCategories(self):
        transactions = Ledger().getTransactions(self.timeRange)
        self.categories = set()
        for transaction in transactions:
            self.categories.add(transaction.getCategory())

    def fetchCounterPartyAliases(self):
        transactions = Ledger().getTransactions(self.timeRange)
        self.counterPartyAliases = set()
        for transaction in transactions:
            self.counterPartyAliases.add(CounterPartyDataBase().getCounterParty(transaction.counterPartyAlias).name)
