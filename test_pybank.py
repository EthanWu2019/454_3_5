"""
============================================================
  PyBank Testing Exercise — Student Test File
============================================================

Your goal: find and document all bugs hidden in the pybank library.

Instructions:
  1. Write tests in the classes below using Python's `unittest` framework.
  2. A passing test means the library behaves correctly.
     A FAILING test means you've found (or confirmed) a bug.
  3. For every bug you find, add a comment above the test explaining:
       - What the bug is
       - Where it lives (file + line number if possible)
       - What the correct behaviour should be

Run your tests with:
    python -m pytest tests/test_pybank.py -v
  or:
    python -m unittest tests/test_pybank.py -v

There are 6 bugs total hidden across account.py and bank.py.
Good luck!
============================================================
"""

import unittest
from pybank import Account, Bank, Transaction, TransactionType


# ---------------------------------------------------------------------------
# Section 1 — Account tests
# ---------------------------------------------------------------------------

class TestAccountCreation(unittest.TestCase):
    """Tests for Account.__init__"""

    def test_valid_account_creation(self):
        """A properly constructed account should store owner, id, and balance."""
        acct = Account("Alice", "ACC001", 100.0)
        self.assertEqual(acct.owner, "Alice")
        self.assertEqual(acct.account_id, "ACC001")
        self.assertEqual(acct.balance, 100.0)

    # TODO: Write tests for invalid inputs (empty owner, empty id, negative balance)


class TestDeposit(unittest.TestCase):
    """Tests for Account.deposit"""

    def test_deposit_increases_balance(self):
        acct = Account("Alice", "ACC001", 0.0)
        acct.deposit(50.0)
        self.assertEqual(acct.balance, 50.0)

    # TODO: Write tests for:
    #   - Depositing zero
    #   - Depositing a negative amount
    #   - Multiple sequential deposits


class TestWithdrawal(unittest.TestCase):
    """Tests for Account.withdraw"""

    def test_withdrawal_decreases_balance(self):
        acct = Account("Alice", "ACC001", 100.0)
        acct.withdraw(40.0)
        self.assertEqual(acct.balance, 60.0)

    def test_withdrawal_exceeding_balance_raises(self):
        acct = Account("Alice", "ACC001", 50.0)
        with self.assertRaises(ValueError):
            acct.withdraw(100.0)

    # TODO: Write a test that withdraws the EXACT balance (e.g. balance=100, withdraw=100).
    #       Should this succeed or raise? What does the library actually do?


class TestTransactionHistory(unittest.TestCase):
    """Tests for Account.get_transaction_history"""

    def setUp(self):
        self.acct = Account("Bob", "ACC002", 0.0)
        self.acct.deposit(100.0)
        self.acct.deposit(200.0)
        self.acct.deposit(300.0)

    def test_history_returns_most_recent_first(self):
        history = self.acct.get_transaction_history()
        self.assertEqual(history[0].amount, 300.0)

    def test_history_length_matches_transactions(self):
        history = self.acct.get_transaction_history()
        self.assertEqual(len(history), 3)

    # TODO: Write a test requesting `limit=1`, `limit=2`, `limit=3`.
    #       Does the returned list length match the limit you requested?

    # TODO: Write a test for limit on an account with NO transactions.


class TestStatementSummary(unittest.TestCase):
    """Tests for Account.get_statement_summary"""

    # TODO: Write tests verifying total_deposits, total_withdrawals,
    #       net_change, and transaction_count.
    #       Include a test for an account with zero transactions.
    pass


# ---------------------------------------------------------------------------
# Section 2 — Bank tests
# ---------------------------------------------------------------------------

class TestBankAccountManagement(unittest.TestCase):
    """Tests for Bank.create_account and Bank.get_account"""

    def setUp(self):
        self.bank = Bank("TestBank")

    def test_create_and_retrieve_account(self):
        self.bank.create_account("Alice", "A1", 500.0)
        acct = self.bank.get_account("A1")
        self.assertEqual(acct.owner, "Alice")

    def test_duplicate_account_id_raises(self):
        self.bank.create_account("Alice", "A1")
        with self.assertRaises(ValueError):
            self.bank.create_account("Bob", "A1")

    # TODO: Write a test calling get_account(None).
    #       What error is raised? Is it the right kind of error?

    # TODO: Write a test calling get_account("") (empty string).


class TestTransfer(unittest.TestCase):
    """Tests for Bank.transfer"""

    def setUp(self):
        self.bank = Bank("TestBank")
        self.bank.create_account("Alice", "A1", 200.0)
        self.bank.create_account("Bob", "B1", 50.0)

    def test_transfer_moves_funds(self):
        self.bank.transfer("A1", "B1", 100.0)
        self.assertEqual(self.bank.get_account("A1").balance, 100.0)
        self.assertEqual(self.bank.get_account("B1").balance, 150.0)

    def test_transfer_to_same_account_raises(self):
        with self.assertRaises(ValueError):
            self.bank.transfer("A1", "A1", 50.0)

    # TODO: Write a test that transfers the EXACT balance of the source account.
    #       Does it succeed? Should it?


class TestTotalAssets(unittest.TestCase):
    """Tests for Bank.total_assets"""

    # TODO: Write a test for total_assets on a bank with multiple accounts.

    # TODO: Write a test for total_assets on a bank with NO accounts.
    #       Check the TYPE of the return value — is it a float?


class TestFindAccountsByOwner(unittest.TestCase):
    """Tests for Bank.find_accounts_by_owner"""

    def setUp(self):
        self.bank = Bank("TestBank")
        self.bank.create_account("Alice", "A1")
        self.bank.create_account("Alice", "A2")
        self.bank.create_account("Bob", "B1")

    def test_finds_multiple_accounts(self):
        results = self.bank.find_accounts_by_owner("Alice")
        self.assertEqual(len(results), 2)

    def test_case_insensitive_search(self):
        results = self.bank.find_accounts_by_owner("alice")
        self.assertEqual(len(results), 2)

    def test_no_match_returns_empty_list(self):
        results = self.bank.find_accounts_by_owner("Charlie")
        self.assertEqual(results, [])

    # TODO: Write a test passing None as the owner argument.
    #       What error is raised? Is it the right kind of error?

    # TODO: Write a test passing an empty string.


if __name__ == "__main__":
    unittest.main()
