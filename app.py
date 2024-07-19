from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response
import mysql.connector
from mysql.connector import Error
import secrets
import qrcode
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

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

@app.route('/')
def home():
    return render_template('index.html')

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
            session['username'] = username
            session['restaurant_name'] = user[6]  # Assuming restaurant_name is in the 6th column
            session['profile_picture'] = user[9]  # Assuming profile_picture path is in the 9th column
            session['qr_code'] = None  # Reset QR code when user logs in
            return redirect(url_for('dashboard'))
        return "Invalid credentials, please try again."
    except Error as e:
        print(f"Error while querying MySQL: {e}")
        return "An error occurred while logging in. Please try again.", 500

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect(url_for('home'))

@app.route('/generate_qr')
def generate_qr():
    if 'username' in session:
        if session.get('qr_code') is None:
            qr = qrcode.make(f"QR Code for {session['restaurant_name']}")
            buf = io.BytesIO()
            qr.save(buf, format='PNG')
            buf.seek(0)
            session['qr_code'] = buf.getvalue()
        response = make_response(session['qr_code'])
        response.headers.set('Content-Type', 'image/png')
        return response
    return redirect(url_for('home'))

@app.route('/view_qr')
def view_qr():
    if 'username' in session:
        return render_template('view_qr.html', restaurant_name=session['restaurant_name'])
    return redirect(url_for('home'))

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

@app.route('/edit_view', methods=['GET', 'POST'])
def edit_view():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        restaurant_name = request.form['restaurant_name']
        restaurant_location = request.form['restaurant_location']
        restaurant_type = request.form['restaurant_type']
        
        profile_picture = request.files['profile_picture']
        profile_picture_path = session['profile_picture']
        
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(profile_picture_path)
            session['profile_picture'] = profile_picture_path

        connection = create_db_connection()
        if connection is None:
            return "Failed to connect to the database. Please try again later.", 500

        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name=%s, email=%s, contact_number=%s, restaurant_name=%s, restaurant_location=%s, restaurant_type=%s, profile_picture=%s
                WHERE username=%s
            """, (full_name, email, contact_number, restaurant_name, restaurant_location, restaurant_type, profile_picture_path, session['username']))
            connection.commit()
            cursor.close()
            connection.close()
            session['restaurant_name'] = restaurant_name
            return redirect(url_for('dashboard'))
        except Error as e:
            print(f"Error while updating MySQL: {e}")
            return "An error occurred while updating. Please try again.", 500
    
    connection = create_db_connection()
    if connection is None:
        return "Failed to connect to the database. Please try again later.", 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('edit_view.html', user=user)
    except Error as e:
        print(f"Error while querying MySQL: {e}")
        return "An error occurred while fetching data. Please try again.", 500

if __name__ == '__main__':
    app.run(debug=True)
