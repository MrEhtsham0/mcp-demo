-- Initialize expense_tracker database
CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) DEFAULT '',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO expenses (date, amount, category, subcategory, note) VALUES
('2024-01-15', 25.50, 'Food & Dining', 'Lunch', 'Lunch at restaurant'),
('2024-01-16', 15.00, 'Transportation', 'Bus', 'Daily commute'),
('2024-01-17', 100.00, 'Shopping', 'Clothing', 'New shirt');

-- Create indexes for better performance
CREATE INDEX idx_date ON expenses(date);
CREATE INDEX idx_category ON expenses(category);
CREATE INDEX idx_amount ON expenses(amount);
