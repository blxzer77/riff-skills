-- up
ALTER TABLE orders
  ADD COLUMN status TEXT NOT NULL DEFAULT 'pending';

UPDATE orders
SET status = 'paid'
WHERE paid_at IS NOT NULL;

-- down
ALTER TABLE orders DROP COLUMN status;

-- The deploy is run by the release job without an explicit transaction.
