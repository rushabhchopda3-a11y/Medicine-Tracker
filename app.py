from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from database import (
    create_connection,
    add_medication,
    get_all_medications,
    delete_medication,
    get_medication_by_id,
    update_medication,
    get_dashboard_stats,
    get_alerts,
)

app = Flask(__name__)

# === GLOBAL CONTEXT PROCESSOR (fixes 'now is undefined') ===
@app.context_processor
def inject_now():
    """Make current datetime globally available to all templates."""
    return {'now': datetime.utcnow}

# === DATABASE CONNECTION TEST ===
db_conn = create_connection()
if db_conn is not None:
    print("✅ Database connection test successful.")
    db_conn.close()
else:
    print("❌ Database connection test failed!")

# === HOME ROUTE ===
@app.route('/')
def home():
    """Display dashboard statistics."""
    stats = get_dashboard_stats() or {'total': 'N/A', 'expiring_month': 'N/A', 'low_stock': 'N/A'}
    return render_template('dashboard.html', stats=stats)

# === ADD MEDICINE ROUTE ===
@app.route('/add', methods=['GET', 'POST'])
def add_medicine_route():
    """Add a new medicine record."""
    if request.method == 'POST':
        try:
            form = request.form
            med_details = (
                form['med_name'],
                form.get('gen_name', ''),
                form['med_type'],
                form.get('manufacturer', ''),
                form.get('strength', ''),
                form['expiry_date'],
                form.get('purchase_date') or None,
                form['quantity'],
                form.get('price') or None,
                form['presc_req'],
                form.get('storage', ''),
                form.get('side_effects', '')
            )

            if not form['med_name'] or not form['expiry_date'] or int(form['quantity']) < 0:
                return "⚠️ Error: Missing required fields or invalid quantity.", 400

            if add_medication(med_details):
                return redirect(url_for('view_medicines'))
            return "❌ Failed to add medication to database.", 500

        except Exception as e:
            return f"❌ Internal error: {e}", 500

    return render_template('add_medication.html')

# === VIEW MEDICINES ROUTE ===
@app.route('/view')
def view_medicines():
    """Display all medicines."""
    meds_list = get_all_medications() or []
    return render_template('view_medicines.html', meds=meds_list)

# === DELETE MEDICINE ROUTE ===
@app.route('/delete/<int:med_id>')
def delete_medicine_route(med_id):
    """Delete a medicine by its ID."""
    if delete_medication(med_id):
        return redirect(url_for('view_medicines'))
    return "❌ Failed to delete medication.", 500

# === EDIT MEDICINE ROUTE ===
@app.route('/edit/<int:med_id>', methods=['GET', 'POST'])
def edit_medicine_route(med_id):
    """Edit details of an existing medicine."""
    if request.method == 'POST':
        try:
            form = request.form
            med_details = (
                form['med_name'],
                form.get('gen_name', ''),
                form['med_type'],
                form.get('manufacturer', ''),
                form.get('strength', ''),
                form['expiry_date'],
                form.get('purchase_date') or None,
                form['quantity'],
                form.get('price') or None,
                form['presc_req'],
                form.get('storage', ''),
                form.get('side_effects', '')
            )

            if not form['med_name'] or not form['expiry_date'] or int(form['quantity']) < 0:
                return "⚠️ Error: Missing required fields or invalid quantity.", 400

            if update_medication(med_id, med_details):
                return redirect(url_for('view_medicines'))
            return "❌ Failed to update medication.", 500

        except Exception as e:
            return f"❌ Internal error: {e}", 500

    med_data = get_medication_by_id(med_id)
    if med_data is None:
        return "❌ Medication not found.", 404
    return render_template('edit_medication.html', med=med_data)

# === ALERTS PAGE ROUTE ===
@app.route('/alerts')
def alerts_page():
    """Display expiring and low stock medicine alerts."""
    alert_data = get_alerts() or []
    return render_template('alerts.html', alerts=alert_data)

# === MAIN ENTRY POINT ===
if __name__ == '__main__':
    app.run(debug=True)
 