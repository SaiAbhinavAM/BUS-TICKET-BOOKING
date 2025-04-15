-- database_setup.sql

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Store hashed passwords!
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    fare DECIMAL(10, 2) NOT NULL,
    departure_time TIME,
    arrival_time TIME,
    bus_details VARCHAR(100) -- e.g., 'Volvo AC Seater', 'Standard Non-AC'
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    route_id INT NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_seats INT NOT NULL,
    total_fare DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Confirmed', -- e.g., Confirmed, Cancelled
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT NULL, -- Optional: Link complaint to a specific booking
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Submitted', -- e.g., Submitted, In Progress, Resolved
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- Add some sample routes (Optional)
INSERT INTO routes (origin, destination, fare, departure_time, arrival_time, bus_details) VALUES
('City A', 'City B', 500.00, '08:00:00', '12:00:00', 'Volvo AC Seater'),
('City B', 'City C', 350.50, '14:00:00', '17:30:00', 'Standard Non-AC'),
('City A', 'City C', 800.00, '10:00:00', '17:00:00', 'Luxury Sleeper');