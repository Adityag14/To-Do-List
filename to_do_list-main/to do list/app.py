from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '5bd5e18b29522a8ee43b08d0841c5d97' 
# Set up the LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dreams@2024',
    'database': 'flask_auth_demo',
    'raise_on_warnings': True
}

# Create a MySQL connection
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# User class
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

# User loader function
@login_manager.user_loader
def load_user(user_id):
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return User(user_data[0], user_data[1])
    return None
@app.route('/')
def home():
    return render_template('home.html')
# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

       
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')


        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
            db_conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            message="Your are registerd successfully please login to continue"
            return render_template('home.html', message=message)
        except mysql.connector.Error as err:
            flash(f'Registration failed: {err}', 'error')
        
        

    return render_template('home.html', message=message)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query user details from the database
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cursor.fetchone()

        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'error')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
