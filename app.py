from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify, Response, flash
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
import random
import csv


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'managemyrestraw@gmail.com'
app.config['MAIL_PASSWORD'] = 'ggag orpo xdda vmfa'
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
                msg.body = f""" 
                Hello {username},
                
                To reset your password, click the following link: {reset_link}
                If you did not request a password reset, please ignore this email.
                
                Best regards,
                ManageMyRestaurant
                
                Note: This is an automated email. Please do not reply to this email.
                """
                mail.send(msg)
                return "A password reset link has been sent to your email address.", 200
            return "Invalid username or email. Please try again."
        except Error as e:
            print(f"Error while querying database: {e}")
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
            print("Connection to database was successful")
            return connection
    except Error as e:
        print(f"Error while connecting to database: {e}")
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
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Hash the password
        restaurant_name = request.form['restaurant_name']
        restaurant_location = request.form['restaurant_location']
        restaurant_type = request.form['restaurant_type']
        
        # Generate OTP
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['registration_details'] = {
            'full_name': full_name,
            'email': email,
            'contact_number': contact_number,
            'username': username,
            'password': hashed_password,
            'plain_password': password,
            'restaurant_name': restaurant_name,
            'restaurant_location': restaurant_location,
            'restaurant_type': restaurant_type
        }

        # Send OTP to user's email
        msg = Message("Your OTP for ManageMyRestaurant registration", sender="your-email@gmail.com", recipients=[email])
        msg.body = f"""
        Hello {username},

        A warm welcome to ManageMyRestaurant! We're excited to have you on board!

        To complete your registration and ensure the security of your account, we've sent you a One-Time Password (OTP) to verify your email address.

        Your OTP is: {otp}

        Please enter this code on our verification page to verify your email and activate your account. This will enable you to access all the features and benefits of ManageMyRestaurant.

        Thank you for choosing ManageMyRestaurant! We look forward to helping you manage your restaurant efficiently and grow your business.

        Best regards,
        ManageMyRestaurant

        Note: This is an automated email. Please do not reply to this email.
        """
        mail.send(msg)
        return redirect(url_for('verify_otp'))
    
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if int(entered_otp) == session.get('otp'):
            details = session.get('registration_details')
            connection = create_db_connection()
            if connection is None:
                return "Failed to connect to the database. Please try again later.", 500

            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO users (full_name, email, contact_number, username, password, restaurant_name, restaurant_location, restaurant_type) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (details['full_name'], details['email'], details['contact_number'], details['username'], details['password'], details['restaurant_name'], details['restaurant_location'], details['restaurant_type']))
                connection.commit()
                cursor.close()
                connection.close()
                # Clear session data
                session.pop('otp', None)
                session.pop('registration_details', None)
                return f"Registration successful! Your username is {details['username']} and your password is {details['plain_password']}."
            except Error as e:
                print(f"Error while inserting into database: {e}")
                return "An error occurred while registering. Please try again.", 500
        else:
            return "Invalid OTP. Please try again."
    
    return render_template('verify_otp.html')


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
        print(f"Error while querying database: {e}")
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
                    'restaurant_name': user[6],
                    'restaurant_location': user[7],
                    'restaurant_type': user[8],
                    'profile_picture': base64.b64encode(user[9]).decode('utf-8') if user[9] else None
                }
                return render_template('edit_view.html', user=user_data)
        except Error as e:
            print(f"Error while querying database: {e}")
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
        password = generate_password_hash(request.form['password'])  # Hash the new password
        restaurant_name = request.form['restaurant_name']
        restaurant_location = request.form['restaurant_location']
        restaurant_type = request.form['restaurant_type']
        profile_picture = request.files['profile_picture'].read() if 'profile_picture' in request.files and request.files['profile_picture'].filename else None

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
            print(f"Error while updating database: {e}")
            return "An error occurred while updating the profile. Please try again.", 500
    return redirect(url_for('home'))


@app.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = create_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        if 'item_name' in request.form:
            item_name = request.form['item_name']
            item_description = request.form['item_description']
            item_price = request.form['item_price']
            item_section = request.form.get('item_section', '')  # Defaults to an empty string if not provided

            # Image validation (Optional but recommended)
            if 'item_image' in request.files:
                item_image = request.files['item_image']
                if item_image.mimetype not in ['image/jpeg', 'image/png', 'image/gif']:
                    flash("Invalid image format. Please upload a JPG, PNG, or GIF image.", "error")
                    return redirect(url_for('add_menu'))

                # Read image content
                item_image_data = item_image.read()
            else:
                item_image_data = None

            # Insert menu item
            cursor.execute(
                """
                INSERT INTO menu_items 
                (item_name, item_description, item_price, item_image, item_section, user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, 
                (item_name, item_description, item_price, item_image_data, item_section, session['user_id'])
            )
            connection.commit()

        elif 'section_name' in request.form:
            section_name = request.form['section_name']

            # Check for duplicate section
            cursor.execute(
                "SELECT COUNT(*) FROM item_section WHERE section_name = %s AND user_id = %s",
                (section_name, session['user_id'])
            )
            if cursor.fetchone()[0] > 0:
                flash("Section already exists.", "error")
            else:
                # Insert new section
                cursor.execute(
                    "INSERT INTO item_section (section_name, user_id) VALUES (%s, %s)",
                    (section_name, session['user_id'])
                )
                connection.commit()

    # Fetch menu items
    cursor.execute(
        """
        SELECT id, item_name, item_description, item_price, item_image, item_section 
        FROM menu_items 
        WHERE user_id = %s
        """, 
        (session['user_id'],)
    )
    menu_items = cursor.fetchall()

    # Fetch item sections
    cursor.execute(
        "SELECT id, section_name FROM item_section WHERE user_id = %s", 
        (session['user_id'],)
    )
    item_section = cursor.fetchall()

    cursor.close()
    connection.close()

    # Convert menu items to list with base64 image encoding
    menu_items = [{'id': item[0], 'name': item[1], 'description': item[2], 'price': item[3], 'image': base64.b64encode(item[4]).decode('utf-8') if item[4] else None, 'section': item[5]} for item in menu_items]
    item_section = [{'id': section[0], 'name': section[1]} for section in item_section]

    return render_template('add_menu.html', menu_items=menu_items, item_section=item_section)

@app.route('/add_section', methods=['POST'])
def add_section():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    section_name = request.form['section_name']

    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Check for duplicates before inserting
        cursor.execute("SELECT COUNT(*) FROM item_section WHERE section_name = %s AND user_id = %s", (section_name, session['user_id']))
        if cursor.fetchone()[0] > 0:
            flash("Section already exists.", "error")
        else:
            cursor.execute(
                "INSERT INTO item_section (section_name, user_id) VALUES (%s, %s)",
                (section_name, session['user_id'])
            )
            connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('add_menu'))

@app.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        # Set the section to NULL for items in this section
        cursor.execute(
            "UPDATE menu_items SET item_section = NULL WHERE item_section = (SELECT section_name FROM item_section WHERE id = %s AND user_id = %s)", 
            (section_id, session['user_id'])
        )

        # Delete the section
        cursor.execute("DELETE FROM item_section WHERE id = %s AND user_id = %s", (section_id, session['user_id']))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('add_menu'))




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
    section_filter = request.args.get('section', 'all')
    price_range_filter = request.args.get('price', 'all')
    
    connection = create_db_connection()
    cursor = connection.cursor()

    # Fetch unique sections
    cursor.execute("SELECT DISTINCT item_section FROM menu_items WHERE user_id = %s", (restaurant_id,))
    sections = cursor.fetchall()

    query = "SELECT item_name, item_description, item_price, item_image, item_section FROM menu_items WHERE user_id = %s"
    filters = [restaurant_id]

    if section_filter != 'all':
        query += " AND item_section = %s"
        filters.append(section_filter)

    if price_range_filter != 'all':
        min_price, max_price = map(float, price_range_filter.split('-'))
        query += " AND item_price BETWEEN %s AND %s"
        filters.extend([min_price, max_price])

    cursor.execute(query, tuple(filters))
    menu_items = cursor.fetchall()
    cursor.close()
    connection.close()

    menu_items = [{'name': item[0], 'description': item[1], 'price': item[2], 'image': base64.b64encode(item[3]).decode('utf-8'), 'section': item[4]} for item in menu_items]
    sections = [section[0] for section in sections]  # Extract section names from query results

    return render_template('view_menu.html', menu_items=menu_items, sections=sections)



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
        
        # Fetch pending orders
        cursor.execute("""
            SELECT o.id, o.table_number, GROUP_CONCAT(oi.item_name SEPARATOR ', ') as items, SUM(oi.item_price) as total_price, o.is_completed, o.completed_at
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.restaurant_id = %s AND o.is_completed = FALSE
            GROUP BY o.id, o.table_number, o.is_completed, o.completed_at
        """, (session['user_id'],))
        pending_orders = cursor.fetchall()
        
        # Fetch recently completed orders
        cursor.execute("""
            SELECT o.id, o.table_number, GROUP_CONCAT(oi.item_name SEPARATOR ', ') as items, SUM(oi.item_price) as total_price, o.is_completed, o.completed_at
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.restaurant_id = %s AND o.is_completed = TRUE
            GROUP BY o.id, o.table_number, o.is_completed, o.completed_at
            ORDER BY o.completed_at DESC
            LIMIT 5
        """, (session['user_id'],))
        recent_completed_orders = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('view_orders.html', pending_orders=pending_orders, recent_completed_orders=recent_completed_orders)
    
    return redirect(url_for('home'))



@app.route('/mark_order_completed/<int:order_id>', methods=['POST'])
def mark_order_completed(order_id):
    if 'username' in session:
        connection = create_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "UPDATE orders SET is_completed = TRUE, completed_at = NOW() WHERE id = %s AND restaurant_id = %s",
                (order_id, session['user_id'])
            )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('view_orders'))
        except Error as e:
            print(f"Error while updating database: {e}")
            return "An error occurred while updating the order status. Please try again.", 500
    return redirect(url_for('home'))


@app.route('/download_order_history', methods=['POST'])
def download_order_history():
    if 'username' in session:
        selected_date = request.form.get('history-date')
        connection = create_db_connection()
        cursor = connection.cursor()

        # Fetch orders only for the selected date
        cursor.execute("""
            SELECT o.id, o.table_number, GROUP_CONCAT(oi.item_name SEPARATOR ', ') as items, SUM(oi.item_price) as total_price, o.is_completed, o.completed_at
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.restaurant_id = %s AND DATE(o.completed_at) = %s
            GROUP BY o.id, o.table_number, o.is_completed, o.completed_at
        """, (session['user_id'], selected_date))
        
        orders = cursor.fetchall()
        cursor.close()
        connection.close()

        # Create CSV for download
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Order ID', 'Table Number', 'Items', 'Total Price', 'Status', 'Completed At'])
        
        for order in orders:
            writer.writerow([
                order[0],
                order[1],
                order[2],
                order[3],
                'Completed' if order[4] else 'Pending',
                order[5] if order[4] else ''
            ])
        
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=order_history_{selected_date}.csv"}
        )
    return redirect(url_for('home'))


@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if 'username' in session:
        # This function will not delete orders from the database, just clear them from the session
        session.pop('orders', None)  # Clearing the orders from session if stored there
        return redirect(url_for('view_orders'))
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
