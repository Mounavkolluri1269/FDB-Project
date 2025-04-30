-- Create the database
CREATE DATABASE IF NOT EXISTS EventBookingPlatform;
USE EventBookingPlatform;

-- Create Users table
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(100),
    Role ENUM('user', 'admin') DEFAULT 'user'
);

-- Create Events table
CREATE TABLE Events (
    EventID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(100),
    Description TEXT,
    Location VARCHAR(100),
    Date DATE,
    Price DECIMAL(10, 2)
);

-- Create Checkins table
CREATE TABLE Checkins (
    CheckinID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    EventID INT,
    Guests INT,
    CheckinTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID)
);

-- Create Payments table
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    CheckinID INT,
    Amount DECIMAL(10,2),
    Method ENUM('credit_card', 'paypal', 'upi', 'cash'),
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CheckinID) REFERENCES Checkins(CheckinID)
);

-- Insert sample users
INSERT INTO Users (Name, Email, Password, Role) VALUES
('Admin User', 'admin@example.com', 'admin123', 'admin'),
('John Doe', 'john@example.com', 'john123', 'user');

-- Insert sample events
INSERT INTO Events (Title, Description, Location, Date, Price) VALUES
('Tech Conference 2025', 'Annual tech gathering with speakers, demos, and networking.', 'Dallas', '2025-06-20', 99.99),
('Startup Pitch Night', 'Showcase your ideas to potential investors.', 'Austin', '2025-07-05', 49.50),
('Wedding Expo', 'Explore wedding services, planners, and deals.', 'Houston', '2025-08-10', 75.00),
('Live Music Fest', 'A night of fun with live performances.', 'San Antonio', '2025-09-01', 120.00);
INSERT INTO Events (Title, Description, Location, Date, Price) VALUES
('Weddings', 'Celebrate love with flawless planning, from intimate gatherings to grand ceremonies. We ensure every detail is handled with care and elegance.', 'Dallas', '2025-06-01', 2500.00),
('Corporate Events', 'Host professional seminars, product launches, or team-building retreats. We align every element to reflect your brand and goals.', 'Austin', '2025-06-15', 1800.00),
('Birthday Parties', 'Make birthdays unforgettable with custom themes, décor, and entertainment. We cater to all age groups, from kids to adults.', 'Houston', '2025-07-01', 800.00),
('Concerts & Live Shows', 'From artist coordination to crowd management, we bring energy to the stage. Experience seamless execution for unforgettable performances.', 'San Antonio', '2025-07-20', 1500.00),
('Festivals', 'We manage large-scale cultural or seasonal festivals with full logistical support. Focus on the fun while we handle the complex setup.', 'Fort Worth', '2025-08-05', 3000.00),
('Exhibitions & Trade Shows', 'Showcase your products or services with impactful setups and efficient flow. We provide end-to-end management from stalls to visitor experience.', 'Dallas', '2025-08-22', 2200.00),
('Private Parties', 'Whether it\'s a housewarming or anniversary bash, we design exclusive private gatherings. Enjoy personalized themes and flawless service.', 'Plano', '2025-09-10', 1000.00),
('Charity & Fundraisers', 'Create inspiring events that support meaningful causes. We manage donors, venues, and campaigns to maximize impact.', 'Austin', '2025-09-25', 500.00),
('Workshops & Seminars', 'Plan educational or training sessions with organized schedules and materials. We ensure productive environments and smooth coordination.', 'Frisco', '2025-10-10', 350.00),
('Fashion Shows', 'From runway setup to backstage coordination, we bring your style vision to life. Expect glitz, glamour, and perfect timing.', 'Houston', '2025-11-01', 2000.00);


ALTER TABLE Checkins
ADD COLUMN PreferredLocation VARCHAR(255),
ADD COLUMN PreferredDate DATE;

