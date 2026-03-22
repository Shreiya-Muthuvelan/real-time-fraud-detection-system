-- Create cleaned transactions table
CREATE TABLE transactions_clean AS
SELECT
    "index",
    step,
    type,
    amount,
    "nameOrig" AS sender,
    "oldbalanceOrg" AS old_balance_orig,
    "newbalanceOrig" AS new_balance_orig,
    "nameDest" AS receiver,
    "oldbalanceDest" AS old_balance_dest,
    "newbalanceDest" AS new_balance_dest,
    "isFraud" AS is_fraud,
    "isFlaggedFraud" AS is_flagged_fraud
FROM transactions;

-- Add primary key
ALTER TABLE transactions_clean
ADD COLUMN transaction_id SERIAL PRIMARY KEY;

-- Create indexes
CREATE INDEX idx_sender ON transactions_clean(sender);
CREATE INDEX idx_receiver ON transactions_clean(receiver);
CREATE INDEX idx_fraud ON transactions_clean(is_fraud);

-- Create fraud-only table
CREATE TABLE fraud_transactions AS
SELECT *
FROM transactions_clean
WHERE is_fraud = 1;