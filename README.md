# Restaurant Management System

This is a Flask-based web application for managing restaurant user registrations, logins, and profile updates, including profile picture uploads.

## Features

- User Registration
- User Login
- View and Edit User Profile
- Upload Profile Picture
- Generate and View QR Code for Restaurant
- Print QR Code

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
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            contact_number VARCHAR(15) NOT NULL,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            restaurant_name VARCHAR(255) NOT NULL,
            restaurant_location VARCHAR(255) NOT NULL,
            restaurant_type VARCHAR(255) NOT NULL,
            profile_picture VARCHAR(255)
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

## Contributing

Feel free to contribute to this project by creating issues or submitting pull requests.

## License

This project is licensed under the MIT License.
