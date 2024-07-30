# Restaurant Management System

This is a Flask-based web application for managing restaurant user registrations, logins, and profile updates, including profile picture uploads.

## Features

- User Registration
- User Login
- View and Edit User Profile
- Upload Profile Picture
- Generate and View QR Code for Restaurant
- Print QR Code
- Add Menu items
- Remove Menu items
- Scan QR code 
- Make Orders
- View Orders 

## Requirements

- Python 3.x
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

        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            contact_number VARCHAR(20),
            restaurant_name VARCHAR(100),
            restaurant_location VARCHAR(100),
            restaurant_type VARCHAR(50),
            profile_picture LONGBLOB
        );

        CREATE TABLE menu_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            item_description TEXT,
            item_image LONGBLOB,
            FOREIGN KEY (user_id) REFERENCES users(id),
            item_price DECIMAL(10, 2) NOT NULL
        );

        CREATE TABLE orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            table_number VARCHAR(255) NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            restaurant_id INT,
            is_completed BOOLEAN DEFAULT FALSE
        );
        

        CREATE TABLE order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            item_id INT,
            item_name VARCHAR(255),
            item_price DECIMAL(10, 2),
            FOREIGN KEY (order_id) REFERENCES orders(id)
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

This project is licensed under the MIT License.
