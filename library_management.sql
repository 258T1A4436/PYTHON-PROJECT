-- ==========================================================
-- Database Script for Library Management System
-- Suitable for 2nd Year B.Tech CSE Project & Viva
-- ==========================================================

-- 1. Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS library_management;

-- 2. Switch to the library_management database
USE library_management;

-- 3. Create the 'books' table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1
);

-- 4. Create the 'users' table for Login & Registration
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL, -- SHA-256 Produces a 64-character hexadecimal hash
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Insert starter sample records for testing and demonstration
INSERT INTO books (title, author, category, quantity) VALUES
('Introduction to Algorithms', 'Thomas H. Cormen', 'Computer Science', 5),
('Clean Code', 'Robert C. Martin', 'Software Engineering', 3),
('Operating System Concepts', 'Abraham Silberschatz', 'Computer Science', 4),
('Database System Concepts', 'Abraham Silberschatz', 'Database Systems', 6),
('Computer Networks', 'Andrew S. Tanenbaum', 'Networking', 2);

-- 6. Insert default demo user (Username: admin, Password: admin123)
-- SHA-256 of 'admin123' is: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
INSERT IGNORE INTO users (username, password) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
