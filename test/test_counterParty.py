from test.test_spendlog import TestSpendlog
from spendlog.counterParty import CounterParty, CounterPartyDataBase, NameMismatchError

class TestCounterParty(TestSpendlog):

    def testCounterParty(self):
        aliasA = "aliasA"
        counterPartyA = CounterParty(aliasA)
        # test default fields initialized correctly
        self.assertEqual(counterPartyA.name, aliasA)
        self.assertEqual(counterPartyA.tags, set())
        self.assertEqual(counterPartyA.category, None)

        aliasB = "aliasB"
        tagsB = set(["tag B"])
        categoryB = "category B"
        modifierB = lambda x : None
        counterPartyB = CounterParty(aliasB, tagsB, categoryB, modifierB)

        # test specified fields initialized correctly
        self.assertEqual(counterPartyB.name, aliasB)
        self.assertEqual(counterPartyB.tags, tagsB)
        self.assertEqual(counterPartyB.category, categoryB)
        self.assertEqual(counterPartyB.transactionModifier, modifierB)

        # == operator
        self.assertEqual(counterPartyB, counterPartyB)
        self.assertNotEqual(counterPartyA, counterPartyB)
        with self.assertRaises(NameMismatchError):
            counterPartyB == CounterParty(aliasB)

        # str()
        self.assertEqual(str(counterPartyB), aliasB)
        self.assertNotEqual(str(counterPartyB), aliasA)

class TestCounterPartyDataBase(TestSpendlog):

    def testInitializeCounterPartyDataBase(self):
        databaseA = CounterPartyDataBase()
        databaseB = CounterPartyDataBase()
        databaseC = databaseA
        self.assertIs(databaseA, databaseB)
        self.assertIs(databaseA, CounterPartyDataBase())
        self.assertIs(CounterPartyDataBase(), CounterPartyDataBase())
        self.assertIs(databaseA, databaseC)
        self.assertIs(databaseB, databaseC)
        self.assertIs(CounterPartyDataBase(), databaseC)

    def testAddGetAndReset(self):
        # get non existing counter party - it gets created
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 0)
        aliasA = "aliasA"
        counterPartyA = CounterPartyDataBase().getCounterParty(aliasA)
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 1)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), {"aliasA"})
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), {"aliasA"})

        # get party again - same party returned
        counterPartyASecond = CounterPartyDataBase().getCounterParty(aliasA)
        self.assertIs(counterPartyA, counterPartyASecond)
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 1)

        # get second non existing counter party - it gets created and is not the same as the first
        aliasB = "aliasB"
        counterPartyB = CounterPartyDataBase().getCounterParty(aliasB)
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 2)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), {"aliasA", "aliasB"})
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), {"aliasA", "aliasB"})

        self.assertIsNot(counterPartyA, counterPartyB)

        self.assertEqual(counterPartyA.name, aliasA)
        self.assertEqual(counterPartyB.name, aliasB)
        self.assertNotEqual(counterPartyA.name, counterPartyB.name)

        # create third counter party by using add counter party - we have one more counter party in database
        nameIndex = 0
        aliasIndex = 1
        aliasesC = ["aliasC", "tommy"]
        tagsC = set(["tag C"])
        categoryC = "category C"
        modifierC = lambda x : None
        CounterPartyDataBase().addCounterParty(aliasesC, tagsC, categoryC, modifierC)
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 3)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), {"aliasA", "aliasB", "aliasC"})
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), {"aliasA", "aliasB", "aliasC", "tommy"})

        # get the third counter party by name, it has the specified values (first alias is the name)
        counterPartyC = CounterPartyDataBase().getCounterParty(aliasesC[nameIndex])
        self.assertEqual(counterPartyC.name, aliasesC[nameIndex])
        self.assertEqual(counterPartyC.tags, tagsC)
        self.assertEqual(counterPartyC.category, categoryC)
        self.assertEqual(counterPartyC.transactionModifier, modifierC)
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 3)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), {"aliasA", "aliasB", "aliasC"})
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), {"aliasA", "aliasB", "aliasC", "tommy"})

        # get the third counter party by second alias, it has the specified values
        counterPartyCSecond = CounterPartyDataBase().getCounterParty(aliasesC[aliasIndex])
        self.assertEqual(counterPartyC.name, aliasesC[nameIndex])
        self.assertEqual(counterPartyC.tags, tagsC)
        self.assertEqual(counterPartyC.category, categoryC)
        self.assertEqual(counterPartyC.transactionModifier, modifierC)
        self.assertIs(counterPartyC, counterPartyCSecond)
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 3)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), {"aliasA", "aliasB", "aliasC"})
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), {"aliasA", "aliasB", "aliasC", "tommy"})

        # add new party that uses existing alias and test that it now doesn't point to the same counter party
        aliasesD = ["tommy"]
        CounterPartyDataBase().addCounterParty(aliasesD)
        counterPartyD = CounterPartyDataBase().getCounterParty(aliasesD[nameIndex])
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 4)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), {"aliasA", "aliasB", "aliasC", "tommy"})
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), {"aliasA", "aliasB", "aliasC", "tommy"})
        self.assertIsNot(counterPartyC, counterPartyD)
        self.assertNotEqual(counterPartyC, counterPartyD)

        # reset the database
        CounterPartyDataBase().reset()
        self.assertEqual(len(CounterPartyDataBase().getAllCounterParties()), 0)
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyNames(), set())
        self.assertEqual(CounterPartyDataBase().getAllCounterPartyAliases(), set())
        counterPartyASecond = CounterPartyDataBase().getCounterParty(aliasA)
        self.assertIsNot(counterPartyA, counterPartyASecond)
        with self.assertRaises(NameMismatchError):
            counterPartyASecond == counterPartyA
