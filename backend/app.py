from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host="db",
        database="tourismdb",
        user="postgres",
        password="password"
    )

# --- User CRUDs ---
@app.route('/hotels', methods=['GET'])
def get_hotels():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM hotels ORDER BY id")
    hotels = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(hotels)

@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO bookings (user_id, hotel_id, start_date, end_date)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (data['user_id'], data['hotel_id'], data['start_date'], data['end_date']))
    
    booking_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'id': booking_id}), 201

@app.route('/bookings', methods=['GET'])
def get_bookings():
    user_id = request.args.get('user_id')
    
    if not user_id or user_id == 'undefined':
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT b.*, h.name as hotel_name 
            FROM bookings b 
            JOIN hotels h ON b.hotel_id = h.id 
            WHERE b.user_id = %s 
            ORDER BY b.start_date
        """, (user_id,))
        
        bookings = cur.fetchall()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'deleted'}), 204

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 409
    
    cur.execute("""
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        RETURNING id
    """, (username, password))
    
    user_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Registration successful', 'user_id': user_id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user:
        return jsonify({
            'status': 'success', 
            'message': 'Login successful',
            'user_id': user['id']
        }), 200
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Invalid credentials'
        }), 401
    

# --- Admin CRUDs ---
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data['username']
    password = data['password']
    
    if username == "admin" and password == "admin123":
        return jsonify({
            'status': 'success',
            'message': 'Admin login successful'
        }), 200
    return jsonify({
        'status': 'error',
        'message': 'Invalid admin credentials'
    }), 401

@app.route('/admin/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT users.*, COUNT(bookings.id) as booking_count 
        FROM users 
        LEFT JOIN bookings ON users.id = bookings.user_id 
        GROUP BY users.id
        ORDER BY users.id
    """)
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(users)

@app.route('/admin/users/<int:user_id>/bookings', methods=['GET'])
def get_user_bookings(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT b.*, h.name as hotel_name 
        FROM bookings b 
        JOIN hotels h ON b.hotel_id = h.id 
        WHERE b.user_id = %s
        ORDER BY b.start_date
    """, (user_id,))
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(bookings)

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM bookings WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'deleted'}), 204

@app.route('/admin/hotels', methods=['POST'])
def admin_create_hotel():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO hotels (name, rating)
        VALUES (%s, %s)
        RETURNING id
    """, (data['name'], data['rating']))
    
    hotel_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'id': hotel_id, 'status': 'created'}), 201

@app.route('/admin/hotels/<int:hotel_id>', methods=['DELETE'])
def admin_delete_hotel(hotel_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM hotels WHERE id = %s", (hotel_id,))
        if not cur.fetchone():
            return jsonify({'status': 'error', 'message': 'Hotel not found'}), 404
            
        cur.execute("DELETE FROM bookings WHERE hotel_id = %s", (hotel_id,))
        
        cur.execute("DELETE FROM hotels WHERE id = %s", (hotel_id,))
        
        conn.commit()
        return jsonify({'status': 'deleted'}), 204
        
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
    finally:
        cur.close()
        conn.close()

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            rating INTEGER NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            hotel_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            FOREIGN KEY (hotel_id) REFERENCES hotels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)