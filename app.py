from flask import Flask, render_template, request, redirect
import sqlite3
import statistics

app = Flask(__name__)
DB = "database.db"

# Initialize the database table
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS survey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                date TEXT NOT NULL,
                contact TEXT NOT NULL,
                foods TEXT,
                rating_eat_out INTEGER,
                rating_watch_movies INTEGER,
                rating_radio INTEGER,
                rating_tv INTEGER
            )
        ''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    contact = request.form['contact']
    age = calculate_age_from_dob(date)

    foods = ', '.join(request.form.getlist('foods'))

    rating_watch_movies = request.form.get('watch_movies')
    rating_radio = request.form.get('radio')
    rating_eat_out = request.form.get('eat_out')
    rating_tv = request.form.get('tv')

    # Basic validation
    if not all([name, email, date, contact, rating_watch_movies, rating_radio, rating_eat_out, rating_tv]):
        return "Please complete all fields", 400

    if not (5 <= age <= 120):
        return "Age must be between 5 and 120", 400

    # Save to DB
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            INSERT INTO survey (
                name, email, age, date, contact, foods,
                rating_eat_out, rating_watch_movies, rating_radio, rating_tv
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, email, age, date, contact, foods,
            int(rating_eat_out), int(rating_watch_movies),
            int(rating_radio), int(rating_tv)
        ))

    return redirect('/results')

@app.route('/results')
def results():
    with sqlite3.connect(DB) as conn:
        rows = conn.execute('SELECT * FROM survey').fetchall()
        if not rows:
            return render_template('results.html', data=None)

        ages = [row[3] for row in rows]
        pizza_lovers = [row for row in rows if 'Pizza' in row[6]]

        data = {
            'total_surveys': len(rows),
            'average_age': round(statistics.mean(ages), 1),
            'youngest': min(ages),
            'oldest': max(ages),
            'pizza_percentage': round(len(pizza_lovers) / len(rows) * 100, 1),
            'average_eat_out': round(statistics.mean([row[7] for row in rows]), 1),
            'average_watch_movies': round(statistics.mean([row[8] for row in rows]), 1),
            'average_radio': round(statistics.mean([row[9] for row in rows]), 1),
            'average_tv': round(statistics.mean([row[10] for row in rows]), 1)
        }

        return render_template('results.html', data=data)

# Helper function to calculate age from date of birth
from datetime import datetime, date
def calculate_age_from_dob(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return 0  # fallback in case of format issues

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
