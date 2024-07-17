# Flask Login and Registration

This project is a simple web application for user registration and login, built using Flask and MySQL.

## Features

- User registration with detailed information
- User login
- Data stored in a MySQL database

## Prerequisites

- Python 3.x
- Flask
- MySQL server (e.g., XAMPP)
- MySQL connector for Python

## Setup

### 1. Clone the Repository
git clone git@github.com:asimmandal9547/Resturant_login.git
cd your-repo-name

2. Install Python Dependencies
Create a virtual environment and install the required Python packages.

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install flask mysql-connector-python

#3. Configure MySQL
Start your MySQL server (e.g., using XAMPP). Create a database named user_auth_db and a users table:

#sql

CREATE DATABASE user_auth_db;

USE user_auth_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    contact_number VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    restaurant_name VARCHAR(255) NOT NULL,
    restaurant_location VARCHAR(255) NOT NULL,
    restaurant_type VARCHAR(50) NOT NULL
);

#4. Update Database Credentials
Update the MySQL connection details in app.py with your MySQL username and password:

python
Copy code
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_mysql_username",
            password="your_mysql_password",
            database="user_auth_db",
            port=3306  # Ensure the port is specified
        )
        if connection.is_connected():
            print("Connection to MySQL database was successful")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None

# 5. Run the Application
Start the Flask application:

python app.py

The application will be accessible at http://127.0.0.1:5000.