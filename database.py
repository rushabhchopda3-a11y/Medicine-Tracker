import mysql.connector
from mysql.connector import Error


# === DATABASE CONNECTION ===
def create_connection():
    """Create and return a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='medcare_db',   # ✅ Make sure this DB exists
            user='root',
            password='Rushabh05'     # ⚠️ Use your actual MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"❌ Database connection error: {e}")
    return None


# === ADD MEDICATION ===
def add_medication(med_details):
    """Insert a new medication record into the database."""
    query = """
    INSERT INTO medications 
    (medication_name, generic_name, medication_type, manufacturer, strength, 
     expiry_date, purchase_date, quantity_remaining, price, 
     prescription_required, storage_instructions, side_effects) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(query, med_details)
        connection.commit()
        print("✅ Medication added successfully.")
        return True
    except Error as e:
        print(f"❌ Error adding medication: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# === GET ALL MEDICATIONS ===
def get_all_medications():
    """Fetch and return all medications, ordered by expiry date."""
    query = "SELECT * FROM medications ORDER BY expiry_date ASC"
    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return []

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"❌ Error fetching medications: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# === DELETE MEDICATION ===
def delete_medication(med_id):
    """Delete a medication record by its ID."""
    query = "DELETE FROM medications WHERE medication_id = %s"
    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(query, (med_id,))
        connection.commit()
        print(f"✅ Medication with ID {med_id} deleted.")
        return True
    except Error as e:
        print(f"❌ Error deleting medication: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# === GET MEDICATION BY ID ===
def get_medication_by_id(med_id):
    """Fetch and return a single medication record by ID."""
    query = "SELECT * FROM medications WHERE medication_id = %s"
    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(query, (med_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"❌ Error fetching medication: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# === UPDATE MEDICATION ===
def update_medication(med_id, med_details):
    """Update an existing medication record by ID."""
    query = """
    UPDATE medications SET
        medication_name = %s,
        generic_name = %s,
        medication_type = %s,
        manufacturer = %s,
        strength = %s,
        expiry_date = %s,
        purchase_date = %s,
        quantity_remaining = %s,
        price = %s,
        prescription_required = %s,
        storage_instructions = %s,
        side_effects = %s
    WHERE medication_id = %s
    """

    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(query, med_details + (med_id,))
        connection.commit()
        print(f"✅ Medication with ID {med_id} updated.")
        return True
    except Error as e:
        print(f"❌ Error updating medication: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# === DASHBOARD STATS ===
def get_dashboard_stats():
    """Fetch total, expiring, and low-stock medicine counts."""
    query_total = "SELECT COUNT(*) FROM medications"
    query_expiring_month = """
        SELECT COUNT(*) FROM medications
        WHERE expiry_date BETWEEN CURDATE() AND LAST_DAY(CURDATE())
    """
    query_low_stock = "SELECT COUNT(*) FROM medications WHERE quantity_remaining < 10"

    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return None

    stats = {}
    try:
        cursor = connection.cursor()

        cursor.execute(query_total)
        stats["total"] = cursor.fetchone()[0]

        cursor.execute(query_expiring_month)
        stats["expiring_month"] = cursor.fetchone()[0]

        cursor.execute(query_low_stock)
        stats["low_stock"] = cursor.fetchone()[0]

        return stats
    except Error as e:
        print(f"❌ Error fetching dashboard stats: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# === ALERTS (EXPIRING & LOW STOCK) ===
def get_alerts():
    """Return lists of expiring and low-stock medicines."""
    query_expiring = """
    SELECT medication_id, medication_name, expiry_date, 
           DATEDIFF(expiry_date, CURDATE()) AS days_left
    FROM medications
    WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    ORDER BY expiry_date ASC
    """

    query_low_stock = """
    SELECT medication_id, medication_name, quantity_remaining
    FROM medications
    WHERE quantity_remaining < 10
    ORDER BY quantity_remaining ASC
    """

    connection = create_connection()
    if connection is None:
        print("Error: Could not connect to database.")
        return {'expiring': [], 'low_stock': []}

    alerts = {}
    try:
        cursor = connection.cursor()

        cursor.execute(query_expiring)
        alerts['expiring'] = cursor.fetchall()

        cursor.execute(query_low_stock)
        alerts['low_stock'] = cursor.fetchall()

        return alerts
    except Error as e:
        print(f"❌ Error fetching alerts: {e}")
        return {'expiring': [], 'low_stock': []}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
