# storage.py
# Простейшее in-memory хранилище для BeRich

from typing import Dict

# user_id -> total_spent (USDT)
users_spent: Dict[int, float] = {}

# invoice_id -> user_id
pending_invoices: Dict[str, int] = {}
