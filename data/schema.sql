-- E-commerce demo schema (SQLite)

CREATE TABLE customers (
    customer_id      INTEGER PRIMARY KEY,
    name              TEXT NOT NULL,
    email             TEXT NOT NULL,
    city              TEXT NOT NULL,
    signup_date       TEXT NOT NULL     -- ISO date
);

CREATE TABLE products (
    product_id       INTEGER PRIMARY KEY,
    name              TEXT NOT NULL,
    category          TEXT NOT NULL,
    unit_price        REAL NOT NULL
);

CREATE TABLE orders (
    order_id         INTEGER PRIMARY KEY,
    customer_id       INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date        TEXT NOT NULL,    -- ISO date
    status            TEXT NOT NULL     -- 'pending', 'shipped', 'delivered', 'cancelled'
);

CREATE TABLE order_items (
    order_item_id    INTEGER PRIMARY KEY,
    order_id          INTEGER NOT NULL REFERENCES orders(order_id),
    product_id        INTEGER NOT NULL REFERENCES products(product_id),
    quantity          INTEGER NOT NULL,
    unit_price        REAL NOT NULL     -- price at time of order
);
