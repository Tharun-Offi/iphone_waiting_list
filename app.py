from flask import Flask, request, jsonify, send_file, render_template
import sqlite3
import random
import smtplib
import string
import os
import re
from email.message import EmailMessage
import ssl

app = Flask(__name__)

DATABASE = 'iphone_waitlist.db'

def create_customers_table():
    """Create the customers table if it doesn't exist."""
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            referral_code TEXT,
            referred_persons INTEGER DEFAULT 0
        )
    ''')
    connection.commit()
    connection.close()

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Check if the 'customers' table exists
        cursor.execute("PRAGMA table_info(customers)")
        columns = [column[1] for column in cursor.fetchall()]

        # If the 'referrals', 'referred_persons', 'phone', or 'position' columns are missing, migrate the table
        if 'referrals' not in columns or 'referred_persons' not in columns or 'phone' not in columns or 'position' not in columns:
            # Backup existing data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers_backup AS 
                SELECT id, name, email, referral_code FROM customers
            ''')
            cursor.execute('DROP TABLE customers')

            # Recreate the table with the correct schema
            cursor.execute('''
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT UNIQUE,
                    referral_code TEXT UNIQUE NOT NULL,
                    referrals INTEGER DEFAULT 0,
                    referred_persons INTEGER DEFAULT 0,
                    position INTEGER NOT NULL
                )
            ''')

            # Restore data and assign default values for new columns
            cursor.execute('''
                INSERT INTO customers (id, name, email, referral_code, referrals, referred_persons, position)
                SELECT id, name, email, referral_code, 0, 0, ROW_NUMBER() OVER (ORDER BY id)
                FROM customers_backup
            ''')
            cursor.execute('DROP TABLE customers_backup')

        conn.commit()

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def is_valid_phone(phone):
    return re.match(r'^\d{10}$', phone)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    referral_code = data.get('referralCode')

    # Validate input
    if not name or not email or not phone:
        return jsonify({'error': 'Name, email, and phone are required'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    if not is_valid_phone(phone):
        return jsonify({'error': 'Invalid phone number format'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Check for duplicate email
        cursor.execute('SELECT * FROM customers WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 400

        # Check for duplicate phone number
        cursor.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
        if cursor.fetchone():
            return jsonify({'error': 'Phone number already registered'}), 400

        if referral_code:
            cursor.execute('SELECT * FROM customers WHERE referral_code = ?', (referral_code,))
            referrer = cursor.fetchone()
            if not referrer:
                return jsonify({'error': 'Invalid referral code'}), 400
            
            # Increment referrals count for the referrer
            new_referrals = referrer[5] + 1
            cursor.execute('UPDATE customers SET referrals = ? WHERE referral_code = ?', (new_referrals, referral_code))

            # Increment referred_persons count for the referrer
            new_referred_persons = referrer[6] + 1
            cursor.execute('UPDATE customers SET referred_persons = ? WHERE referral_code = ?', (new_referred_persons, referral_code))

        # Determine the position for the new user
        cursor.execute('SELECT COUNT(*) FROM customers')
        count = cursor.fetchone()[0]
        position = count + 1  # Start position at 1 when the list is empty

        # Generate a new referral code for the new user
        new_referral_code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=9))
        cursor.execute('INSERT INTO customers (name, email, phone, referral_code, position) VALUES (?, ?, ?, ?, ?)', (name, email, phone, new_referral_code, position))
        conn.commit()

    return jsonify({'message': 'Signup successful', 'referralCode': new_referral_code, 'position': position})

@app.route('/rank')
def rank():
    return render_template('rank.html')

@app.route('/top10')
def top10():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, email, referrals FROM customers ORDER BY referrals DESC LIMIT 10')
        top10 = cursor.fetchall()
    result = [{'name': row[0], 'email': row[1], 'referrals': row[2]} for row in top10]
    return jsonify(result)

@app.route('/referral', methods=['POST'])
def referral():
    referral_code = request.json['referralCode']
    email = request.json['email']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE referral_code = ?', (referral_code,))
        referrer = cursor.fetchone()
        if referrer:
            new_position = referrer[3] - 1 if referrer[3] >= 1 else 1
            cursor.execute('UPDATE customers SET position = ? WHERE referral_code = ?', (new_position, referral_code))
            new_referral_code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=9))
            cursor.execute('INSERT INTO customers (email, position, referral_code) VALUES (?, ?, ?)', (email, new_position + 1, new_referral_code))
            conn.commit()
            if new_position < 99:
                send_email(email, 'Iphone 16 Pre-Order Coupon Code')
            return jsonify({'referrerPosition': new_position})
        else:
            return jsonify({'error': 'Invalid referral code'}), 400

@app.route('/rank-data')
def rank_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, email, position, referral_code, referred_persons FROM customers ORDER BY position ASC')
        customers = cursor.fetchall()
    result = [
        {
            'name': row[0],
            'email': row[1],
            'position': row[2],
            'referral_code': row[3],
            'referred_persons': row[4]  # Include referred_persons in the response
        }
        for row in customers
    ]
    return jsonify(result)  # Return rankings as JSON

def send_email(email, subject):
    send = 'tharunmctv@gmail.com'
    password = os.environ.get('EMAIL_PASSWORD')
    reciever = email

    subject = "testing"
    coupon_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    body = f"""
    Dear Customer,

    Congratulations on joining our waitlist for the iPhone 16 pre-order!

    As a token of our appreciation, here is your exclusive coupon code: {coupon_code}

    Use this coupon code to get a special discount on your purchase.

    Thank you for being with us.

    Best Regards,
    Apple Team
    """

    em = EmailMessage()
    em['From'] = send
    em['To'] = reciever
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(send, password)
            smtp.sendmail(send, reciever, em.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    create_customers_table()
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)