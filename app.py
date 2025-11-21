from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory user storage (can be replaced with DB)
users = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Load jobs from CSV
jobs_df = pd.read_csv(r'C:\Users\hp\job_finder_app\jobs.csv')

# Home / Job Listing
@app.route('/')
def index():
    search = request.args.get('search', '').lower()
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    filtered_jobs = jobs_df.copy()
    
    if search:
        filtered_jobs = filtered_jobs[filtered_jobs['title'].str.lower().str.contains(search)]
    if job_type:
        filtered_jobs = filtered_jobs[filtered_jobs['job_type'] == job_type]
    if location:
        filtered_jobs = filtered_jobs[filtered_jobs['location'].str.lower().str.contains(location.lower())]

    return render_template('index.html', jobs=filtered_jobs.to_dict(orient='records'))

# Job Details Modal
@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = jobs_df[jobs_df['id'] == job_id].to_dict(orient='records')[0]
    return render_template('job_detail.html', job=job)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users.values():
            if user.username == username and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user_id = str(len(users) + 1)
        users[user_id] = User(user_id, username, password)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Saved Jobs (Simple in-memory for demo)
saved_jobs = {}

@app.route('/save_job/<int:job_id>')
@login_required
def save_job(job_id):
    saved_jobs.setdefault(current_user.id, set()).add(job_id)
    flash('Job saved successfully!')
    return redirect(url_for('index'))

@app.route('/saved_jobs')
@login_required
def view_saved_jobs():
    user_jobs = saved_jobs.get(current_user.id, set())
    filtered_jobs = jobs_df[jobs_df['id'].isin(user_jobs)]
    return render_template('saved_jobs.html', jobs=filtered_jobs.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
