from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secretkey'

# Database Connection
def get_db_connection():
    conn = sqlite3.connect('./DB/DATABASE.db')
    cur = conn.cursor()
    return cur

# Function to calculate sleep time in hours
def calculate_sleep_time(start_time_str, wakeup_time_str):
    try:
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        wakeup_time = datetime.strptime(wakeup_time_str, '%H:%M').time()

        # Get today's date
        today = datetime.today().date()

        # Combine start time with today's date
        start_datetime = datetime.combine(today, start_time)

        # Combine wakeup time with today's date
        wakeup_datetime = datetime.combine(today, wakeup_time)

        # If wakeup time is earlier, add one day
        if wakeup_datetime <= start_datetime:
            wakeup_datetime += timedelta(days=1)

        time_difference = wakeup_datetime - start_datetime
        sleep_time_hours = time_difference.total_seconds() / 3600
        return round(sleep_time_hours, 2)

    except ValueError:
        return None




# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('./DB/DATABASE.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return redirect(url_for('sleep_data'))
    else:
        return render_template('index.html', error="Invalid username or password.")


@app.route('/register')
def let_register():
    return render_template('register.html')

@app.route('/registers', methods=['POST'])
def register():
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    try:
        conn = sqlite3.connect('./DB/DATABASE.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return redirect(url_for('index'))
    except sqlite3.IntegrityError:
        return render_template('register.html', error="Username already exists.")


@app.route('/sleep_data')
def sleep_data():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('./DB/DATABASE.db')
        cur = conn.cursor()
        data = cur.execute("SELECT * FROM sleep_data WHERE user_id = ?", (user_id,)).fetchall()
        return render_template('sleep_data.html', data=data)
    return redirect(url_for('index'))  # Redirect to login if not logged in

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if 'user_id' in session:
        if request.method == 'POST':
            user_id = session['user_id']
            sleep_start_time = request.form['sleep_start_time']
            wakeup_time = request.form['wakeup_time']
            sleep_date = request.form['sleep_date']
            sleep_time = calculate_sleep_time(sleep_start_time, wakeup_time)

            if sleep_time is not None:
                try:
                    conn = sqlite3.connect('./DB/DATABASE.db')
                    cur = conn.cursor()
                    cur.execute("INSERT INTO sleep_data (user_id, sleep_date, sleep_start_time, wakeup_time, sleep_time) VALUES (?, ?, ?, ?, ?)",
                    (user_id, sleep_date, sleep_start_time, wakeup_time, sleep_time))
                    conn.commit()
                    return redirect(url_for('sleep_data'))
                except Exception as e:
                    return render_template('new_entry.html', error=str(e)) # Display db error
            else:
                return render_template('new_entry.html', error="Invalid date/time format.")
        return render_template('new_entry.html')
    return redirect(url_for('index')) # Redirect to login if not logged in

@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'user_id' in session:
        conn = sqlite3.connect('./DB/DATABASE.db')
        cur = conn.cursor()
        data = cur.execute("SELECT * FROM sleep_data WHERE id = ? AND user_id = ?", (entry_id, session['user_id'])).fetchone()
        if request.method == 'POST':
            sleep_start_time = request.form['sleep_start_time']
            wakeup_time = request.form['wakeup_time']
            sleep_time = calculate_sleep_time(sleep_start_time, wakeup_time)
            if sleep_time is not None:
                cur.execute("UPDATE sleep_data SET sleep_start_time = ?, wakeup_time = ?, sleep_time = ? WHERE id = ?",
                                (sleep_start_time, wakeup_time, sleep_time, entry_id))
                conn.commit()
                return redirect(url_for('sleep_data'))
            else:
                return render_template('edit_entry.html', data=data, error="Invalid date/time format.")
        return render_template('edit_entry.html', data=data)
    return redirect(url_for('index')) # Redirect to login if not logged in

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    if 'user_id' in session:
        conn = sqlite3.connect('./DB/DATABASE.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM sleep_data WHERE id = ? AND user_id = ?", (entry_id, session['user_id']))
        conn.commit()
        return redirect('/sleep_data')
    return redirect(url_for('index')) # Redirect to login if not logged in

if __name__ == '__main__':
    app.run(debug=True,port=1234)
