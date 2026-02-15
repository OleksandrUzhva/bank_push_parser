import re
import logging
from typing import Optional, Dict, Type
from models import BankNotification


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseBankParser:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content
        self.data = BankNotification()

    def _extract_by_pattern(self, pattern: str, text: str, group: int = 1) -> Optional[str]:
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
            return match.group(group).strip() if match else None
        except Exception as e:
            logger.error(f"Regex error: {e}")
            return None

    def _parse_amount(self, value: Optional[str]) -> Optional[float]:
        if not value: return None
        try:
            cleaned = value.replace(',', '.').replace('\xa0', '').replace(' ', '')
            cleaned = re.sub(r'[^\d.-]', '', cleaned)
            return float(cleaned)
        except ValueError:
            return None

class UkrsibParser(BaseBankParser):
    def parse(self) -> BankNotification:
        self.data.bank_account_balance = abs(self._parse_amount(self._extract_by_pattern(r"Dostupno\s?([\d\s\.,]+)", self.content)) or 0)
        self.data.bank_account_details = self._extract_by_pattern(r"(?:kartku|Kartka)\s?([\d\*]+)", self.content)
        self.data.operation_amount = abs(self._parse_amount(self._extract_by_pattern(r"(?:sumu|Suma)\s?([\d\s\.,]+)", self.content)) or 0)
        self.data.operation_type = "in" if "Perekaz" in self.content else "reject"
        self.data.operation_currency = "UAH" 
        self.data.counterparty_details = self._extract_by_pattern(r"(?:Perekaz|Blokuvannia):\s?(.*?)\s\d{2}", self.content)
        return self.data

class PumbParser(BaseBankParser):
    def parse(self) -> BankNotification:
        lines = [line.strip() for line in self.content.split('\n') if line.strip()]
        self.data.operation_amount = abs(self._parse_amount(lines[0]) if lines else 0)
        self.data.operation_currency = "UAH"
        self.data.counterparty_details = lines[1] if len(lines) > 1 else None
        self.data.bank_account_details = self._extract_by_pattern(r"Картка:\s?([\*\d]+)", self.content)
        self.data.bank_account_balance = abs(self._parse_amount(self._extract_by_pattern(r"Доступно:\s?([\d\s\.,]+)", self.content)) or 0)
        self.data.operation_type = "in" if "Надходження" in self.title else "out"
        return self.data

class CAPlusParser(BaseBankParser):
    def parse(self) -> BankNotification:
        self.data.bank_account_balance = abs(self._parse_amount(self._extract_by_pattern(r"Баланс:\s?([\d,\s\.]+)", self.content)) or 0)
        self.data.bank_account_details = self._extract_by_pattern(r"Картка:\s?([\*\d]+)", self.content)
        self.data.operation_type = "balance_info"
        self.data.operation_amount = None
        self.data.operation_currency = None
        return self.data

class Tas2uParser(BaseBankParser):
    def parse(self) -> BankNotification:
        amount_raw = self._extract_by_pattern(r"(-?[\d\s\.]+)\sUAH", self.title)
        self.data.operation_amount = abs(self._parse_amount(amount_raw) or 0)
        self.data.operation_type = "out" if amount_raw and "-" in amount_raw else "in"
        self.data.operation_currency = "UAH"
        self.data.bank_account_balance = abs(self._parse_amount(self._extract_by_pattern(r"доступно\s([\d\s\.]+)", self.title)) or 0)
        self.data.bank_account_details = self._extract_by_pattern(r"(\*\d+)", self.title)
        return self.data

class ParserFactory:
    _parsers: Dict[str, Type[BaseBankParser]] = {
        "UKRSIB": UkrsibParser,
        "PUMB": PumbParser,
        "CA+": CAPlusParser, 
        "TAS2U": Tas2uParser
        # Можемо додавати інші банки  
    }

    @classmethod
    def get_parser(cls, app_name: str, title: str, content: str) -> BankNotification:
        parser_cls = cls._parsers.get(app_name)
        if not parser_cls:
            raise ValueError(f"Unsupported app: {app_name}")
        return parser_cls(title, content).parse()

def parse_notification(app_name: str, title: str, content: str) -> dict:
    return ParserFactory.get_parser(app_name, title, content).to_dict()