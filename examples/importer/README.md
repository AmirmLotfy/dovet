# Synthetic importer fixture

Implement `parse_orders(csv_text: str) -> ImportResult` with Python standard CSV semantics. Preserve IDs as strings. Return accepted typed records and structured errors. Never execute CSV content and add no dependencies.

Required headers are `order_id`, `customer_name`, `quantity`, and `unit_price`. Ignore additional headers. Accept a leading UTF-8 BOM and blank lines. Quantity is a positive base-10 integer. Price is a finite, nonnegative `Decimal` with no locale guessing. The first valid occurrence of an ID wins; later duplicates are row errors. A bad row does not discard valid rows. For multiline CSV records, `source_line` is the first physical line of that record.

The protected acceptance suite is outside this directory and is not writable by managed workers.

