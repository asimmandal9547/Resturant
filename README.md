# Restaurant Management System

This is a Flask-based web application for managing restaurant user registrations, logins, profile updates, Add Orders, Remove Orders, View QR code, View Menu page, Order Managing.

## Features

- User Registration
- User Login
- Forgot Password
- View and Edit User Profile
- Generate and View QR Code for Restaurant
- Print QR Code
- Add Menu items
- Remove Menu items
- Scan QR code 
- Make Orders
- View Orders 

## Requirements

- Python
- Flask
- MySQL
- XAMPP (for local MySQL server)
- Required Python packages listed in `requirements.txt`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/restaurant-management-system.git
    cd restaurant-management-system
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the MySQL database:
    - Create a database named `user_auth_db`.
    - Use the following SQL command to create the `users` table:
        ```sql
        CREATE DATABASE user_auth_db;

        USE user_auth_db;

        -- Create users table
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            contact_number VARCHAR(20),
            restaurant_name VARCHAR(100),
            restaurant_location VARCHAR(100),
            restaurant_type VARCHAR(50),
            profile_picture LONGBLOB
        );

        -- Create menu_items table
        CREATE TABLE menu_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            item_description TEXT,
            item_image LONGBLOB,
            item_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Create orders table
        CREATE TABLE orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            table_number VARCHAR(255) NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            restaurant_id INT,
            is_completed BOOLEAN DEFAULT FALSE,
            completed_at DATETIME,
            FOREIGN KEY (restaurant_id) REFERENCES users(id)  -- Add foreign key for restaurant_id
        );

        -- Create order_items table with cascading delete
        CREATE TABLE order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            item_id INT,
            item_name VARCHAR(255),
            item_price DECIMAL(10, 2),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,  -- Add ON DELETE CASCADE
            FOREIGN KEY (item_id) REFERENCES menu_items(id)  -- Add foreign key for item_id
        );

        -- Create password_reset_tokens table
        CREATE TABLE password_reset_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            token VARCHAR(255) NOT NULL,
            expiration INT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        ```

5. Update the database connection details in `app.py`:
    ```python
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="user_auth_db",
    port=3306
    ```

6. Run the application:
    ```bash
    python app.py
    ```

7. Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Usage

- **Home Page**: Login to access the dashboard.
- **Dashboard**: Access various functionalities like viewing/editing profile, adding/removing menu items, viewing orders, and generating QR codes.
- **Profile Management**: View and update user profile details, including uploading a profile picture.
- **Menu**: Customers can scan the QR code to view the menu and place orders.

## Contributing

Feel free to contribute to this project by creating issues or submitting pull requests.

## License

Copyright in 2024 by ManageMyRestaurant.
