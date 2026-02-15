from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class BankNotification:
    bank_account_balance: Optional[float] = None
    bank_account_currency: str = "UAH"
    bank_account_details: Optional[str] = None
    operation_amount: Optional[float] = None
    operation_currency: Optional[str] = None
    operation_type: str = "unknown"
    counterparty_details: Optional[str] = None

    def to_dict(self):
        return asdict(self)