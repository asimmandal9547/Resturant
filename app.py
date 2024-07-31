from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import mysql.connector
from mysql.connector import Error
import secrets
import qrcode
import io
import base64
import hashlib
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'asimmandal9547@gmail.com'
app.config['MAIL_PASSWORD'] = 'xtql hyoz vjqg tvar'
mail = Mail(app)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        connection = create_db_connection()
        if connection is None:
            return "Failed to connect to the database. Please try again later.", 500

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s AND email = %s", (username, email))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                # Generate a unique token
                user_id = user[0]
                token = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()

                # Save the token to the database with an expiration time
                connection = create_db_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO password_reset_tokens (user_id, token, expiration) VALUES (%s, %s, %s)",
                               (user_id, token, int(time.time()) + 3600))  # Token valid for 1 hour
                connection.commit()
                cursor.close()
                connection.close()

                # Send email with reset link
                reset_link = url_for('reset_password', token=token, _external=True)
                msg = Message("Password Reset Request", sender="your-email@example.com", recipients=[email])
                msg.body = f"To reset your password, click the following link: {reset_link}\n\nIf you did not request a password reset, please ignore this email."
                mail.send(msg)
                return "A password reset link has been sent to your email address.", 200
            return "Invalid username or email. Please try again."
        except Error as e:
            print(f"Error while querying MySQL: {e}")
            return "An error occurred. Please try again.", 500
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['new_password']

        # Verify token and get user_id
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM password_reset_tokens WHERE token = %s AND expiration > %s", (token, int(time.time())))
        token_info = cursor.fetchone()

        if token_info:
            user_id = token_info[0]
            hashed_password = generate_password_hash(new_password)

            # Update password
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
            connection.commit()
            
            # Remove used token
            cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
            connection.commit()
            cursor.close()
            connection.close()

            return "Your password has been reset successfully. You can now log in with your new password."
        return "Invalid or expired token. Please request a new password reset.", 400

    return render_template('reset_password.html', token=token)


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # Hash the password
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

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    connection = create_db_connection()
    if connection is None:
        return "Failed to connect to the database. Please try again later.", 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user and check_password_hash(user[2], password):  # Check hashed password
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
        restaurant_url = url_for('view_menu', restaurant_id=session['user_id'], _external=True)
        if session.get('qr_code') is None:
            qr = qrcode.make(restaurant_url)
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
                    'full_name': user[3],
                    'email': user[4],
                    'contact_number': user[5],
                    'username': user[1],
                    'password': user[2],
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

@app.route('/menu/<int:restaurant_id>')
def view_menu(restaurant_id):
    connection = create_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT item_name, item_description, item_price, item_image FROM menu_items WHERE user_id = %s", (restaurant_id,))
    menu_items = cursor.fetchall()
    cursor.close()
    connection.close()

    menu_items = [{'name': item[0], 'description': item[1], 'price': item[2], 'image': base64.b64encode(item[3]).decode('utf-8')} for item in menu_items]
    return render_template('view_menu.html', menu_items=menu_items)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        item_id = request.json['item_id']
        item_name = request.json['item_name']
        item_price = request.json['item_price']
        
        cart = session.get('cart', [])
        cart.append({'id': item_id, 'name': item_name, 'price': item_price})
        session['cart'] = cart
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        item_id = request.json['item_id']
        
        cart = session.get('cart', [])
        cart = [item for item in cart if item['id'] != item_id]
        session['cart'] = cart
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        table_number = request.json['table_number']
        cart = session.get('cart', [])
        
        if not cart:
            return jsonify({'error': 'Cart is empty'}), 400
        
        connection = create_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("INSERT INTO orders (table_number, restaurant_id) VALUES (%s, %s)", (table_number, session['user_id']))
        order_id = cursor.lastrowid
        
        for item in cart:
            cursor.execute("INSERT INTO order_items (order_id, item_id, item_name, item_price) VALUES (%s, %s, %s, %s)",
                           (order_id, item['id'], item['name'], item['price']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        session['cart'] = []
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/orders')
def view_orders():
    if 'username' in session:
        connection = create_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT o.id, o.table_number, GROUP_CONCAT(oi.item_name SEPARATOR ', ') as items, SUM(oi.item_price) as total_price, o.is_completed
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.restaurant_id = %s
            GROUP BY o.id, o.table_number, o.is_completed
        """, (session['user_id'],))
        orders = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template('view_orders.html', orders=orders)
    return redirect(url_for('home'))

@app.route('/mark_order_completed/<int:order_id>', methods=['POST'])
def mark_order_completed(order_id):
    if 'username' in session:
        connection = create_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("UPDATE orders SET is_completed = TRUE WHERE id = %s AND restaurant_id = %s", (order_id, session['user_id']))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('view_orders'))
        except Error as e:
            print(f"Error while updating MySQL: {e}")
            return "An error occurred while updating the order status. Please try again.", 500
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
