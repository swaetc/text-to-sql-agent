"""Builds data/store.db from schema.sql and fills it with sample e-commerce data.

Run: python scripts/seed_db.py
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "store.db"
SCHEMA_PATH = ROOT / "data" / "schema.sql"

random.seed(42)

CITIES = ["Cape Town", "Johannesburg", "Durban", "Pretoria", "Gqeberha", "Bloemfontein"]
CATEGORIES = {
    "Electronics": ["Wireless mouse", "Mechanical keyboard", "USB-C hub", "Webcam", "Monitor stand"],
    "Home": ["Coffee plunger", "Desk lamp", "Throw blanket", "Ceramic mug set", "Candle set"],
    "Books": ["Python crash course", "SQL for data analysis", "The pragmatic programmer", "Clean code", "System design guide"],
    "Sports": ["Yoga mat", "Resistance bands", "Water bottle", "Running cap", "Foam roller"],
}
STATUSES = ["pending", "shipped", "delivered", "cancelled"]
STATUS_WEIGHTS = [0.1, 0.2, 0.6, 0.1]

FIRST_NAMES = ["Thabo", "Aisha", "Liam", "Naledi", "Sipho", "Emma", "Zanele", "Ryan", "Lerato", "Michael",
               "Amahle", "Daniel", "Nomvula", "James", "Precious", "David", "Karabo", "Sarah", "Tumi", "John"]
LAST_NAMES = ["Nkosi", "Van der Merwe", "Dlamini", "Smith", "Mokoena", "Botha", "Zulu", "Naidoo",
              "Khumalo", "Pretorius", "Moyo", "Adams", "Mahlangu", "Reddy", "Fischer"]


def random_date(start: date, end: date) -> str:
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def build_db():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    # Customers
    customers = []
    for i in range(1, 61):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = name.lower().replace(" ", ".") + f"{i}@example.com"
        city = random.choice(CITIES)
        signup = random_date(date(2023, 1, 1), date(2025, 12, 31))
        customers.append((i, name, email, city, signup))
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    # Products
    products = []
    pid = 1
    for category, names in CATEGORIES.items():
        for name in names:
            price = round(random.uniform(50, 2500), 2)
            products.append((pid, name, category, price))
            pid += 1
    conn.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

    # Orders + order_items
    orders = []
    order_items = []
    oid = 1
    item_id = 1
    for customer_id, *_ in customers:
        n_orders = random.randint(0, 6)
        for _ in range(n_orders):
            order_date = random_date(date(2024, 1, 1), date(2026, 7, 1))
            status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
            orders.append((oid, customer_id, order_date, status))

            n_items = random.randint(1, 4)
            chosen = random.sample(products, n_items)
            for prod in chosen:
                qty = random.randint(1, 5)
                order_items.append((item_id, oid, prod[0], qty, prod[3]))
                item_id += 1
            oid += 1

    conn.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
    conn.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", order_items)

    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH} with {len(customers)} customers, {len(products)} products, "
          f"{len(orders)} orders, {len(order_items)} order items.")


if __name__ == "__main__":
    build_db()
