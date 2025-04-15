# db_handler.py
import mysql.connector
from mysql.connector import Error
import bcrypt # For password hashing

# --- Database Configuration ---
# !! IMPORTANT: Use environment variables or a config file in a real app !!
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # Replace with your MySQL username
    'password': 'manjucta123', # Replace with your MySQL password
    'database': 'bus_ticketing_system'
}

# --- Connection ---
def create_connection():
    """Create a database connection."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        # print("MySQL Database connection successful") # Optional: for debugging
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
    return connection

# --- Password Hashing ---
def hash_password(password):
    """Hashes the password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_password(stored_password_hash, provided_password):
    """Verifies a provided password against a stored hash."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash.encode('utf-8'))


# --- User Authentication ---
def register_user(username, password, email=None):
    """Registers a new user."""
    conn = create_connection()
    if not conn: return False, "Database connection error."

    hashed_pw = hash_password(password)
    sql = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (username, hashed_pw.decode('utf-8') , email)) # Store hash as string
        conn.commit()
        return True, "Registration successful!"
    except Error as e:
        conn.rollback()
        if e.errno == 1062: # Duplicate entry
             return False, f"Username '{username}' or Email '{email}' already exists."
        return False, f"Registration failed: {e}"
    finally:
        cursor.close()
        conn.close()

def validate_user(username, password):
    """Validates user credentials."""
    conn = create_connection()
    if not conn: return None, "Database connection error."

    sql = "SELECT user_id, password_hash FROM users WHERE username = %s"
    cursor = conn.cursor()
    user_id = None
    message = "Invalid username or password."
    try:
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        if result:
            stored_user_id, stored_hash = result
            # IMPORTANT: Retrieve hash as bytes if stored as BLOB, or string if stored as VARCHAR/TEXT
            # Adjust based on how you store the hash in register_user
            if check_password(stored_hash, password): # Pass hash string directly
                user_id = stored_user_id
                message = "Login successful!"
            else:
                 message = "Invalid username or password." # Keep message generic
        else:
             message = "Invalid username or password." # Keep message generic

    except Error as e:
        message = f"Login error: {e}"
    finally:
        cursor.close()
        conn.close()
    return user_id, message # Return user_id on success, None otherwise

# --- Routes ---
def get_all_routes():
    """Fetches all available routes."""
    conn = create_connection()
    if not conn: return [], "Database connection error."

    routes = []
    message = "Routes fetched successfully."
    sql = """SELECT route_id, origin, destination, fare,
                    TIME_FORMAT(departure_time, '%H:%i'),
                    TIME_FORMAT(arrival_time, '%H:%i'),
                    bus_details
             FROM routes ORDER BY origin, destination"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        routes = cursor.fetchall()
    except Error as e:
        message = f"Error fetching routes: {e}"
        routes = []
    finally:
        cursor.close()
        conn.close()
    return routes, message

# --- Booking ---
def add_booking(user_id, route_id, num_seats):
    """Adds a new booking."""
    conn = create_connection()
    if not conn: return None, "Database connection error."

    booking_id = None
    message = "Booking failed."
    cursor = conn.cursor()
    try:
        # 1. Get route fare
        cursor.execute("SELECT fare FROM routes WHERE route_id = %s", (route_id,))
        result = cursor.fetchone()
        if not result:
            return None, "Invalid Route ID."
        fare_per_seat = result[0]
        total_fare = fare_per_seat * num_seats

        # 2. Insert booking
        sql = """INSERT INTO bookings (user_id, route_id, num_seats, total_fare)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (user_id, route_id, num_seats, total_fare))
        conn.commit()
        booking_id = cursor.lastrowid # Get the ID of the inserted booking
        message = f"Booking successful! Your Booking ID is {booking_id}."

    except Error as e:
        conn.rollback()
        message = f"Booking failed: {e}"
    finally:
        cursor.close()
        conn.close()
    return booking_id, message

def get_user_bookings(user_id):
    """Fetches all bookings for a specific user."""
    conn = create_connection()
    if not conn: return [], "Database connection error."

    bookings = []
    message = "Bookings fetched successfully."
    sql = """
        SELECT b.booking_id, r.origin, r.destination,
               TIME_FORMAT(r.departure_time, '%H:%i'),
               b.num_seats, b.total_fare, b.status,
               DATE_FORMAT(b.booking_date, '%Y-%m-%d %H:%i')
        FROM bookings b
        JOIN routes r ON b.route_id = r.route_id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (user_id,))
        bookings = cursor.fetchall()
    except Error as e:
        message = f"Error fetching bookings: {e}"
        bookings = []
    finally:
        cursor.close()
        conn.close()
    return bookings, message

def get_booking_details(booking_id):
     """Fetches full details for a specific booking."""
     conn = create_connection()
     if not conn: return None, "Database connection error."

     details = None
     message = "Booking details fetched."
     sql = """
         SELECT
             b.booking_id, u.username,
             r.origin, r.destination, r.bus_details,
             TIME_FORMAT(r.departure_time, '%H:%i') AS dept_time,
             TIME_FORMAT(r.arrival_time, '%H:%i') AS arr_time,
             b.num_seats, b.total_fare, b.status,
             DATE_FORMAT(b.booking_date, '%Y-%m-%d %H:%i:%s') AS booked_on
         FROM bookings b
         JOIN users u ON b.user_id = u.user_id
         JOIN routes r ON b.route_id = r.route_id
         WHERE b.booking_id = %s
     """
     cursor = conn.cursor(dictionary=True) # Fetch as dictionary
     try:
         cursor.execute(sql, (booking_id,))
         details = cursor.fetchone()
         if not details:
             message = "Booking not found."
     except Error as e:
         message = f"Error fetching booking details: {e}"
     finally:
         cursor.close()
         conn.close()
     return details, message


# --- Complaints ---
def add_complaint(user_id, subject, description, booking_id=None):
    """Adds a new complaint."""
    conn = create_connection()
    if not conn: return False, "Database connection error."

    sql = """INSERT INTO complaints (user_id, booking_id, subject, description)
             VALUES (%s, %s, %s, %s)"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (user_id, booking_id, subject, description))
        conn.commit()
        return True, "Complaint submitted successfully!"
    except Error as e:
        conn.rollback()
        return False, f"Failed to submit complaint: {e}"
    finally:
        cursor.close()
        conn.close()

def get_user_complaints(user_id):
    """Fetches all complaints for a specific user."""
    conn = create_connection()
    if not conn: return [], "Database connection error."

    complaints = []
    message = "Complaints fetched successfully."
    sql = """
        SELECT complaint_id, booking_id, subject, description, status,
               DATE_FORMAT(submitted_at, '%Y-%m-%d %H:%i')
        FROM complaints
        WHERE user_id = %s
        ORDER BY submitted_at DESC
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (user_id,))
        complaints = cursor.fetchall()
    except Error as e:
        message = f"Error fetching complaints: {e}"
        complaints = []
    finally:
        cursor.close()
        conn.close()
    return complaints, message