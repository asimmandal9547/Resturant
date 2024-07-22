from flask import Flask, render_template, request, redirect, url_for, session, make_response
import mysql.connector
from mysql.connector import Error
import secrets
import qrcode
import io
import base64
from PIL import Image


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="user_auth_db",
            port=3306
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
            session['user_id'] = user[0]
            session['restaurant_name'] = user[6]
            session['qr_code'] = None
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

@app.route('/edit_view')
def edit_view():
    if 'username' in session:
        user_id = session['user_id']
        connection = create_db_connection()
        if connection is None:
            return "Failed to connect to the database. Please try again later.", 500

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            if user:
                user_data = {
                    'full_name': user[1],
                    'email': user[2],
                    'contact_number': user[3],
                    'username': user[4],
                    'password': user[5],
                    'restaurant_name': user[6],
                    'restaurant_location': user[7],
                    'restaurant_type': user[8],
                    'profile_picture': base64.b64encode(user[9]).decode('utf-8') if user[9] else None
                }
                return render_template('edit_view.html', user=user_data)
        except Error as e:
            print(f"Error while querying MySQL: {e}")
            return "An error occurred. Please try again.", 500
    return redirect(url_for('home'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session:
        user_id = session['user_id']
        full_name = request.form['full_name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        username = request.form['username']
        password = request.form['password']
        restaurant_name = request.form['restaurant_name']
        restaurant_location = request.form['restaurant_location']
        restaurant_type = request.form['restaurant_type']
        profile_picture = request.files['profile_picture'].read() if 'profile_picture' in request.files else None

        connection = create_db_connection()
        if connection is None:
            return "Failed to connect to the database. Please try again later.", 500

        try:
            cursor = connection.cursor()
            if profile_picture:
                cursor.execute("""
                    UPDATE users SET full_name = %s, email = %s, contact_number = %s, username = %s, password = %s, 
                    restaurant_name = %s, restaurant_location = %s, restaurant_type = %s, profile_picture = %s WHERE id = %s
                """, (full_name, email, contact_number, username, password, restaurant_name, restaurant_location, restaurant_type, profile_picture, user_id))
            else:
                cursor.execute("""
                    UPDATE users SET full_name = %s, email = %s, contact_number = %s, username = %s, password = %s, 
                    restaurant_name = %s, restaurant_location = %s, restaurant_type = %s WHERE id = %s
                """, (full_name, email, contact_number, username, password, restaurant_name, restaurant_location, restaurant_type, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('dashboard'))
        except Error as e:
            print(f"Error while updating MySQL: {e}")
            return "An error occurred while updating the profile. Please try again.", 500
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

@app.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = create_db_connection()
    cursor = connection.cursor()
    
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_description = request.form['item_description']
        item_price = request.form['item_price']
        item_image = request.files['item_image'].read()
        
        cursor.execute(
            "INSERT INTO menu_items (item_name, item_description, item_price, item_image, user_id) VALUES (%s, %s, %s, %s, %s)",
            (item_name, item_description, item_price, item_image, session['user_id'])
        )
        connection.commit()
    
    cursor.execute("SELECT id, item_name, item_description, item_price, item_image FROM menu_items WHERE user_id = %s", (session['user_id'],))
    menu_items = cursor.fetchall()
    cursor.close()
    connection.close()
    
    menu_items = [{'id': item[0], 'name': item[1], 'description': item[2], 'price': item[3], 'image': base64.b64encode(item[4]).decode('utf-8')} for item in menu_items]
    
    return render_template('add_menu.html', menu_items=menu_items)


@app.route('/remove_menu', methods=['GET', 'POST'])
def remove_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = create_db_connection()
    cursor = connection.cursor()
    
    if request.method == 'POST':
        item_id = request.form['item_id']
        cursor.execute("DELETE FROM menu_items WHERE id = %s AND user_id = %s", (item_id, session['user_id']))
        connection.commit()
    
    cursor.execute("SELECT id, item_name, item_description, item_image FROM menu_items WHERE user_id = %s", (session['user_id'],))
    menu_items = cursor.fetchall()
    cursor.close()
    connection.close()
    
    menu_items = [{'id': item[0], 'name': item[1], 'description': item[2], 'image': base64.b64encode(item[3]).decode('utf-8')} for item in menu_items]
    
    return render_template('remove_menu.html', menu_items=menu_items)

if __name__ == '__main__':
    app.run(debug=True)
