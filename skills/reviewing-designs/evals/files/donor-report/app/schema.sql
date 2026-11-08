-- inventory module
CREATE TABLE inventory_items (sku TEXT PRIMARY KEY, name TEXT NOT NULL,
    category TEXT NOT NULL, quantity INTEGER NOT NULL DEFAULT 0);
CREATE TABLE stock_moves (id INTEGER PRIMARY KEY, sku TEXT NOT NULL REFERENCES inventory_items(sku),
    kind TEXT NOT NULL CHECK (kind IN ('donation', 'pickup', 'adjustment')),
    donation_id INTEGER, quantity INTEGER NOT NULL, moved_at TEXT NOT NULL);

-- donors module
CREATE TABLE donors (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT);
CREATE TABLE donations (id INTEGER PRIMARY KEY, donor_id INTEGER NOT NULL REFERENCES donors(id),
    received_at TEXT NOT NULL);

-- households module
CREATE TABLE households (id INTEGER PRIMARY KEY, customer_ref TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL, email TEXT, size INTEGER NOT NULL);
CREATE TABLE pickups (id INTEGER PRIMARY KEY, household_id INTEGER NOT NULL REFERENCES households(id),
    slot_start TEXT NOT NULL,  -- ISO 8601 UTC, see app/households/pickups.py
    reminded_at TEXT);

-- volunteers (auth)
CREATE TABLE volunteers (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL);
