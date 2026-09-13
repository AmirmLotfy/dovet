from decimal import Decimal

from parcel_import import parse_orders


def test_public_valid_and_quoted_rows() -> None:
    result = parse_orders(
        'order_id,customer_name,quantity,unit_price\n001,"Doe, Jane",2,3.25\n'
    )
    assert result.accepted[0].order_id == "001"
    assert result.accepted[0].customer_name == "Doe, Jane"
    assert result.accepted[0].unit_price == Decimal("3.25")


def test_public_invalid_quantity_is_structured() -> None:
    result = parse_orders("order_id,customer_name,quantity,unit_price\n1,A,0,1.00\n")
    assert result.errors[0].field == "quantity"
