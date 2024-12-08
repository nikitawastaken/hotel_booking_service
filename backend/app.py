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

# --- CRUD для отелей ---
@app.route('/hotels', methods=['POST'])
def create_hotel():
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
    
    return jsonify({'id': hotel_id}), 201

@app.route('/hotels', methods=['GET'])
def get_hotels():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM hotels ORDER BY id")
    hotels = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(hotels)

@app.route('/hotels/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM hotels WHERE id = %s", (hotel_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'deleted'}), 204

# --- CRUD для брони ---
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
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM bookings ORDER BY start_date")
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(bookings)

@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'deleted'}), 204

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
        return jsonify({'status': 'success', 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Таблица отелей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            rating INTEGER NOT NULL
        )
    """)
    
    # Таблица бронирований
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            hotel_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            FOREIGN KEY (hotel_id) REFERENCES hotels (id)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)