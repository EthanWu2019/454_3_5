import unittest
from pybank import Account, Bank, Transaction, TransactionType

# ---------------------------------------------------------------------------
# Section 1 - Account tests
# ---------------------------------------------------------------------------

class TestAccountCreation(unittest.TestCase):
    """Tests for Account.__init__"""

    def test_valid_account_creation(self):
        """A properly constructed account should store owner, id, and balance."""
        acct = Account("Alice", "ACC001", 100.0)
        self.assertEqual(acct.owner, "Alice")
        self.assertEqual(acct.account_id, "ACC001")
        self.assertEqual(acct.balance, 100.0)

    def test_invalid_account_creation_empty_strings(self):
        """Account creation should fail with empty owner or id."""
        with self.assertRaises(ValueError):
            Account("", "ACC001")
        with self.assertRaises(ValueError):
            Account("Alice", "")

    def test_invalid_account_creation_negative_balance(self):
        """Account creation should fail with negative initial balance."""
        with self.assertRaises(ValueError):
            Account("Alice", "ACC001", -50.0)


class TestDeposit(unittest.TestCase):
    """Tests for Account.deposit"""

    def test_deposit_increases_balance(self):
        acct = Account("Alice", "ACC001", 0.0)
        acct.deposit(50.0)
        self.assertEqual(acct.balance, 50.0)

    def test_deposit_zero_or_negative_raises(self):
        """Deposit must be strictly positive."""
        acct = Account("Alice", "ACC001", 0.0)
        with self.assertRaises(ValueError):
            acct.deposit(0.0)
        with self.assertRaises(ValueError):
            acct.deposit(-10.0)

    def test_multiple_sequential_deposits(self):
        acct = Account("Alice", "ACC001", 0.0)
        acct.deposit(10.0)
        acct.deposit(20.0)
        self.assertEqual(acct.balance, 30.0)


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

    def test_withdraw_exact_balance(self):
        """
        Suspected Bug: Wrong logic / incorrect operator
        Testing boundary condition: withdrawing exactly the total balance.
        """
        acct = Account("Alice", "ACC001", 100.0)
        acct.withdraw(100.0) 
        self.assertEqual(acct.balance, 0.0)


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

    def test_history_with_limit(self):
        """
        Suspected Bug: Off-by-one error
        Testing if limit returns exactly the requested quantity.
        """
        self.assertEqual(len(self.acct.get_transaction_history(limit=1)), 1)
        self.assertEqual(len(self.acct.get_transaction_history(limit=2)), 2)
        self.assertEqual(len(self.acct.get_transaction_history(limit=3)), 3)

    def test_history_limit_no_transactions(self):
        empty_acct = Account("Empty", "ACC003", 0.0)
        self.assertEqual(len(empty_acct.get_transaction_history(limit=5)), 0)


class TestStatementSummary(unittest.TestCase):
    """Tests for Account.get_statement_summary"""

    def test_statement_summary_values(self):
        acct = Account("Charlie", "ACC003", 50.0)
        acct.deposit(100.0)
        acct.withdraw(20.0)
        summary = acct.get_statement_summary()
        
        self.assertEqual(summary["total_deposits"], 100.0)
        self.assertEqual(summary["total_withdrawals"], 20.0)
        self.assertEqual(summary["net_change"], 80.0)
        self.assertEqual(summary["transaction_count"], 2)

    def test_statement_summary_zero_transactions(self):
        acct = Account("Charlie", "ACC003", 50.0)
        summary = acct.get_statement_summary()
        self.assertEqual(summary["total_deposits"], 0.0)
        self.assertEqual(summary["total_withdrawals"], 0.0)
        self.assertEqual(summary["net_change"], 0.0)
        self.assertEqual(summary["transaction_count"], 0)


# ---------------------------------------------------------------------------
# Section 2 - Bank tests
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

    def test_get_account_with_none(self):
        """
        Suspected Bug: Edge case - None input
        """
        with self.assertRaises(KeyError):
            self.bank.get_account(None)

    def test_get_account_with_empty_string(self):
        """
        Suspected Bug: Edge case - empty input
        """
        with self.assertRaises(KeyError):
            self.bank.get_account("")


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

    def test_transfer_exact_balance(self):
        """
        Suspected Bug: Wrong logic / incorrect operator
        Testing boundary condition for transfer logic.
        """
        self.bank.transfer("A1", "B1", 200.0)
        self.assertEqual(self.bank.get_account("A1").balance, 0.0)
        self.assertEqual(self.bank.get_account("B1").balance, 250.0)


class TestTotalAssets(unittest.TestCase):
    """Tests for Bank.total_assets"""

    def test_total_assets_multiple_accounts(self):
        bank = Bank("TestBank")
        bank.create_account("Alice", "A1", 100.50)
        bank.create_account("Bob", "B1", 200.25)
        self.assertEqual(bank.total_assets(), 300.75)

    def test_total_assets_no_accounts(self):
        bank = Bank("TestBank")
        assets = bank.total_assets()
        self.assertEqual(assets, 0.0)
        self.assertIsInstance(assets, float)


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

    def test_find_accounts_none_owner(self):
        """
        Suspected Bug: Edge case - None input
        """
        with self.assertRaises(ValueError):
            self.bank.find_accounts_by_owner(None)

    def test_find_accounts_empty_owner(self):
        """
        Suspected Bug: Edge case - empty string input
        """
        with self.assertRaises(ValueError):
            self.bank.find_accounts_by_owner("")


if __name__ == "__main__":
    unittest.main()