from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task
from datetime import datetime, timedelta
import os

# ================== APP CONFIG ==================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ================== EXTENSIONS ==================
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """Load a user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# Create tables if not exist
with app.app_context():
    db.create_all()

# ================== ROUTES ==================

@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            msg = 'All fields are required'
            return jsonify({'error': msg}), 400 if request.is_json else flash(msg, 'error') or redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            msg = 'Username already exists'
            return jsonify({'error': msg}), 400 if request.is_json else flash(msg, 'error') or redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            msg = 'Email already registered'
            return jsonify({'error': msg}), 400 if request.is_json else flash(msg, 'error') or redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('dashboard')}), 201
        
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard')}), 200
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        msg = 'Invalid username or password'
        return jsonify({'error': msg}), 401 if request.is_json else flash(msg, 'error') or redirect(url_for('login'))

    return render_template('login.html')


# ---------- LOGOUT ----------
@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# ---------- DASHBOARD ----------
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    now = datetime.utcnow()
    upcoming_deadline = now + timedelta(days=1)

    # Tasks owned or assigned to user
    user_tasks = Task.query.filter(
        (Task.user_id == current_user.id) | (Task.assigned_to == current_user.id)
    ).order_by(Task.created_at.desc()).all()

    # Filter tasks due within next 24 hours
    approaching_tasks = [
        t for t in user_tasks
        if t.deadline and now < t.deadline <= upcoming_deadline and t.status != 'completed'
    ]

    return render_template(
        'dashboard.html',
        user=current_user,
        approaching_tasks=approaching_tasks,
        now=now
    )

# ================== API ROUTES ==================

# ---------- TASKS ----------
@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    """Get all tasks or create a new one"""
    if request.method == 'GET':
        user_tasks = Task.query.filter(
            (Task.user_id == current_user.id) | (Task.assigned_to == current_user.id)
        ).order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in user_tasks]), 200

    # POST - Create a task
    data = request.get_json(force=True, silent=True) or {}
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    # Parse deadline safely
    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.fromisoformat(data['deadline'])
        except Exception:
            try:
                deadline = datetime.strptime(data['deadline'], '%Y-%m-%dT%H:%M')
            except Exception:
                pass

    task = Task(
        title=title,
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'todo'),
        deadline=deadline,
        user_id=current_user.id,
        assigned_to=data.get('assigned_to')
    )

    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


# ---------- TASK DETAIL ----------
@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def task_detail(task_id):
    """Get, update, or delete a specific task"""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and task.assigned_to != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        return jsonify(task.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.priority = data.get('priority', task.priority)
        task.status = data.get('status', task.status)

        # Handle completion
        if data.get('status') == 'completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif data.get('status') != 'completed':
            task.completed_at = None

        # Handle deadline
        if 'deadline' in data:
            if data['deadline']:
                try:
                    task.deadline = datetime.fromisoformat(data['deadline'])
                except Exception:
                    try:
                        task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%dT%H:%M')
                    except Exception:
                        task.deadline = None
            else:
                task.deadline = None

        if 'assigned_to' in data:
            task.assigned_to = data['assigned_to']

        task.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(task.to_dict()), 200

    # DELETE
    if task.user_id != current_user.id:
        return jsonify({'error': 'Only task owner can delete'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True}), 200


# ---------- USERS ----------
@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    """Return all users for task assignment"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


# ---------- STATS ----------
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Return dashboard statistics"""
    all_tasks = Task.query.filter(
        (Task.user_id == current_user.id) | (Task.assigned_to == current_user.id)
    ).all()

    now = datetime.utcnow()
    return jsonify({
        'total': len(all_tasks),
        'completed': len([t for t in all_tasks if t.status == 'completed']),
        'in_progress': len([t for t in all_tasks if t.status == 'in_progress']),
        'todo': len([t for t in all_tasks if t.status == 'todo']),
        'overdue': len([t for t in all_tasks if t.deadline and t.deadline < now and t.status != 'completed']),
        'high_priority': len([t for t in all_tasks if t.priority == 'high' and t.status != 'completed']),
        'medium_priority': len([t for t in all_tasks if t.priority == 'medium' and t.status != 'completed']),
        'low_priority': len([t for t in all_tasks if t.priority == 'low' and t.status != 'completed'])
    }), 200


# ================== MAIN ==================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
