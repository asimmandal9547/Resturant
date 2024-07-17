from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database connection
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="user_auth_db",
            port=3306  # Ensure the port is specified
        )
        if connection.is_connected():
            print("Connection to MySQL database was successful")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    connection = create_db_connection()
    if connection is None:
        return "Failed to connect to the database. Please try again later.", 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            return f"Welcome {username}!"
        return "Invalid credentials, please try again."
    except Error as e:
        print(f"Error while querying MySQL: {e}")
        return "An error occurred while logging in. Please try again.", 500

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        username = request.form['username']
        password = request.form['password']
        restaurant_name = request.form['restaurant_name']
        restaurant_location = request.form['restaurant_location']
        restaurant_type = request.form['restaurant_type']
        
        connection = create_db_connection()
        if connection is None:
            return "Failed to connect to the database. Please try again later.", 500

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO users (full_name, email, contact_number, username, password, restaurant_name, restaurant_location, restaurant_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (full_name, email, contact_number, username, password, restaurant_name, restaurant_location, restaurant_type))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('home'))
        except Error as e:
            print(f"Error while inserting into MySQL: {e}")
            return "An error occurred while registering. Please try again.", 500
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
