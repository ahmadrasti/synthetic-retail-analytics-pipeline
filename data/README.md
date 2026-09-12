# Data

The files in `synthetic/` are deterministic, fictional examples generated with a fixed random seed. They contain no names, phone numbers, emails, addresses, customer identifiers, or source records from a private system.

Input contracts:

- `transactions.csv`: `transaction_id`, `date`, `location_id`, `customer_segment`, `product_category`, `quantity`, `net_revenue`, `status`.
- `inventory.csv`: `date`, `location_id`, `product_category`, `received_qty`, `sold_qty`, `waste_qty`.
- `calendar.csv`: `date`, `weekday`, `is_weekend`, `is_holiday`.

Regenerate all files with:

```bash
python scripts/generate_synthetic_data.py
```

