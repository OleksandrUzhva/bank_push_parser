import pytest
from parser import parse_notification



@pytest.mark.parametrize("app_name, title, content, expected", [
    ("UKRSIB", "UKRSIB", 
     "Perekaz: CLIENT001 00.00.0000 00:00:00 na kartku 000000****0000 na sumu 1000.00UAH. Dostupno 1154.16UAH. EXAMPLE.COM",
     {"bank_account_balance": 1154.16, "bank_account_currency": "UAH", "bank_account_details": "000000****0000", "operation_amount": 1000.0, "operation_currency": "UAH", "operation_type": "in", "counterparty_details": "CLIENT001"}),
    
    ("PUMB", "Надходження", 
     "2000.0UAH\nCLIENT NAME\n00-00-0000 00:00\nКартка: *0000\nДоступно: 2000.0UAH",
     {"bank_account_balance": 2000.0, "bank_account_currency": "UAH", "bank_account_details": "*0000", "operation_amount": 2000.0, "operation_currency": "UAH", "operation_type": "in", "counterparty_details": "CLIENT NAME"}),
    
    ("CA+", "CA+", "Баланс: 5853,79 UAH\nКартка: *0000",
     {"bank_account_balance": 5853.79, "bank_account_currency": "UAH", "bank_account_details": "*0000", "operation_amount": None, "operation_currency": None, "operation_type": "balance_info", "counterparty_details": None}),

    ("UKRSIB", "UKRSIB", 
     "Blokuvannia: ORDER001 PAYMENT*MERCHANT 00.00.0000 00:00:00. Kartka 000000****0000. Suma 2540.43UAH. Dostupno 78126.18UAH. EXAMPLE.COM",
     {"bank_account_balance": 78126.18, "bank_account_currency": "UAH", "bank_account_details": "000000****0000", "operation_amount": 2540.43, "operation_currency": "UAH", "operation_type": "reject", "counterparty_details": "ORDER001 PAYMENT*MERCHANT"}),

    ("TAS2U", "-1 000.00 UAH доступно 505.01 UAH *0000", 
     "переказ з картки на картку, 00.00.0000 00:00:00, власні кошти 505.01 UAH комісія 15.00 UAH,",
     {"bank_account_balance": 505.01, "bank_account_currency": "UAH", "bank_account_details": "*0000", "operation_amount": 1000.0, "operation_currency": "UAH", "operation_type": "out", "counterparty_details": None}),
])
def test_parsers(app_name, title, content, expected):
    assert parse_notification(app_name, title, content) == expected