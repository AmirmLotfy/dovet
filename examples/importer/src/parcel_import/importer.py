"""Intentionally incomplete fixture used to demonstrate a real recovery."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_name: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class RowError:
    source_line: int
    code: str
    field: str


@dataclass(frozen=True)
class ImportResult:
    accepted: tuple[Order, ...]
    errors: tuple[RowError, ...]


def parse_orders(csv_text: str) -> ImportResult:
    """Parse orders. The starting implementation deliberately lacks required behavior."""

    raise NotImplementedError("recovery worker must implement the accepted contract")

