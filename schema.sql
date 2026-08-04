-- Create e-commerce database
CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

-- Create admin table for login credentials
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Insert default admin account (username: admin, password: admin123)
INSERT IGNORE INTO admin (id, username, password) VALUES (1, 'admin', 'admin123');
