from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Keep this secret in production!

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',          # Assuming your MySQL username is 'root'
    'password': 'littu',     # Updated to your new password
    'database': 'job_portal'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    # Renders your main job portal page
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            # Verify user and password
            if user and check_password_hash(user['password'], password):
                session['loggedin'] = True
                session['id'] = user['id']
                session['name'] = user['name']
                return redirect(url_for('home'))
            else:
                flash('Incorrect email or password!')
                
        except mysql.connector.Error as err:
            flash('Database connection failed. Please try again.')
            print(f"Error: {err}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password for security before storing it in the database
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check if account already exists
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()
            
            if account:
                flash('Account already exists! Please log in.')
            else:
                cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_password))
                conn.commit()
                flash('You have successfully registered! Please log in.')
                return redirect(url_for('login'))
                
        except mysql.connector.Error as err:
            flash('Database error during signup. Please try again.')
            print(f"Error: {err}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)