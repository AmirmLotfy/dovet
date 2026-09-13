"""Canonical protected checks for the public synthetic fixture."""

from decimal import Decimal

import pytest


@pytest.fixture(autouse=True)
def candidate_path(monkeypatch: pytest.MonkeyPatch) -> None:
    configured = __import__("os").environ.get("DOVET_CANDIDATE_ROOT")
    if configured:
        monkeypatch.syspath_prepend(f"{configured}/src")


def parse(text: str):
    from parcel_import import parse_orders

    return parse_orders(text)


def test_valid_record() -> None:
    result = parse("order_id,customer_name,quantity,unit_price\n001,Ada,2,3.25\n")
    assert result.accepted[0].order_id == "001"
    assert result.accepted[0].unit_price == Decimal("3.25")


def test_csv_quoting_bom_and_blank_lines() -> None:
    result = parse('\ufefforder_id,customer_name,quantity,unit_price\n\n7,"Doe, Jane",1,5.00\n')
    assert result.accepted[0].customer_name == "Doe, Jane"


def test_missing_header_is_file_error() -> None:
    result = parse("order_id,quantity\n1,2\n")
    assert not result.accepted
    assert result.errors[0].source_line == 1
    assert result.errors[0].code == "missing_header"


@pytest.mark.parametrize("value", ["0", "-1", "2.5", "x"])
def test_invalid_quantity(value: str) -> None:
    result = parse(f"order_id,customer_name,quantity,unit_price\na,A,{value},1.00\n")
    assert result.errors[0].field == "quantity"


@pytest.mark.parametrize("value", ["-1", "nan", "inf", "1,25"])
def test_invalid_price(value: str) -> None:
    result = parse(f'order_id,customer_name,quantity,unit_price\na,A,1,"{value}"\n')
    assert result.errors[0].field == "unit_price"


def test_first_valid_duplicate_wins_and_other_rows_survive() -> None:
    text = "order_id,customer_name,quantity,unit_price\n1,A,0,1\n1,B,2,1\n1,C,3,1\n2,D,1,2\n"
    result = parse(text)
    assert [row.customer_name for row in result.accepted] == ["B", "D"]
    assert any(error.code == "duplicate_id" for error in result.errors)


def test_formula_is_inert_and_extra_headers_are_ignored() -> None:
    result = parse("order_id,customer_name,quantity,unit_price,note\n1,=2+2,1,1,x\n")
    assert result.accepted[0].customer_name == "=2+2"
