-- Initialize the expense_tracker database
CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

-- Grant privileges to the expense_user
GRANT ALL PRIVILEGES ON expense_tracker.* TO 'expense_user'@'%';
FLUSH PRIVILEGES;
