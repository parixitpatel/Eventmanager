# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Event
from datetime import datetime
from flask_lambda import FlaskLambda    

app = FlaskLambda(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

# Create database tables before the first request
# @app.before_first_request
@app.before_request
def create_tables():
    db.create_all()

# User Authentication (Simple Example)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Replace with your own authentication logic
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('view_events'))
        else:
            flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Decorator to enforce authentication
def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Route to display all events
@app.route('/events')
@login_required
def view_events():
    events = Event.query.all()
    return render_template('events.html', events=events)

# Route to add a new event
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        time_str = request.form['time']
        location = request.form['location']

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()

        new_event = Event(title=title, description=description, date=date_obj, time=time_obj, location=location)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('view_events'))
    return render_template('add_event.html')

# Route to edit an existing event
@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        
        time_str = request.form['time']
        time_str = time_str.split(':')[0] + ':' + time_str.split(':')[1]  # Remove any seconds if present
        event.time = datetime.strptime(time_str, '%H:%M').time()

        event.location = request.form['location']
        db.session.commit()
        return redirect(url_for('view_events'))
    return render_template('edit_event.html', event=event)

# Route to delete an event
@app.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('view_events'))

# Netlify Lambda function entry point
from flask_lambda import function
@function
def handler(event, context):
    return app(event, context)


if __name__ == '__main__':
    app.run()
