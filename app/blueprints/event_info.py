from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db_connect import get_db

# Create the events blueprint
event_info = Blueprint('event_info', __name__)

# Route for displaying all events (this will be used in 'events.html')
@event_info.route('/events', methods=['GET', 'POST'])
def events():
    db = get_db()
    cursor = db.cursor()  # Always define the cursor at the start

    if request.method == 'POST':
        event_name = request.form['event_name']
        category = request.form['category']
        description = request.form['description']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        location = request.form['location']
        max_attendees = request.form['max_attendees']
        current_attendees = 0  # Initializing current_attendees as 0

        # Insert event into the event_info table
        cursor.execute(
            'INSERT INTO event_info (event_name, category, description, date, time, location, max_attendees, current_attendees) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            (event_name, category, description, event_date, event_time, location, max_attendees, current_attendees)
        )
        db.commit()
        return redirect(url_for('event_info.events'))  # Redirect to the event listing page

    # Filtering logic
    location_filter = request.args.get('location', '').strip()
    if location_filter:
        # Use LIKE for partial matching
        query = 'SELECT * FROM event_info WHERE location LIKE %s'
        cursor.execute(query, (f'%{location_filter}%',))
    else:
        # Fetch all events if no filter is provided
        cursor.execute('SELECT * FROM event_info')

    all_events = cursor.fetchall()
    return render_template('events.html', all_events=all_events)

# Route for signing up for an event (this will be used to increase current_attendees)
@event_info.route('/signup_event/<int:event_id>', methods=['POST'])
def signup_event(event_id):
    db = get_db()
    cursor = db.cursor()

    # Assuming the user is logged in, get their user_id (e.g., from session or authentication)
    user_id = session.get('user_id')  # Replace with actual user_id retrieval method

    if not user_id:
        flash('You need to be logged in to sign up for an event!', 'danger')
        return redirect(url_for('users.login'))  # Redirect to login page if not logged in

    # First, check if the user is already signed up for the event
    cursor.execute('SELECT * FROM attendees WHERE user_id = %s AND event_id = %s', (user_id, event_id))
    existing_signup = cursor.fetchone()

    if existing_signup:
        flash('You are already signed up for this event!', 'warning')
        return redirect(url_for('event_info.events'))

    # Check if the event has reached its maximum number of attendees
    cursor.execute('SELECT current_attendees, max_attendees FROM event_info WHERE event_id = %s', (event_id,))
    event = cursor.fetchone()

    if event['current_attendees'] >= event['max_attendees']:
        flash('This event has reached its maximum number of attendees!', 'danger')
        return redirect(url_for('event_info.events'))

    # Insert the new sign-up record into the attendees table
    cursor.execute('INSERT INTO attendees (user_id, event_id) VALUES (%s, %s)', (user_id, event_id))
    db.commit()

    # Increment the current_attendees for the event
    cursor.execute('UPDATE event_info SET current_attendees = current_attendees + 1 WHERE event_id = %s', (event_id,))
    db.commit()

    flash('You have successfully signed up for the event!', 'success')
    return redirect(url_for('event_info.events'))

# Route for updating an event (this will be used in 'events_update.html')
@event_info.route('/update_event/<int:event_id>/update', methods=['GET', 'POST'])
def update_event(event_id):
    db = get_db()
    cursor = db.cursor()  # Use a cursor for executing queries

    if request.method == 'POST':
        # Retrieve form data
        event_name = request.form.get('event_name')
        category = request.form.get('category')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        location = request.form.get('location')
        max_attendees = request.form.get('max_attendees')

        # Update the event details in the database
        cursor.execute(
            '''
            UPDATE event_info
            SET event_name = %s, category = %s, description = %s, date = %s, time = %s, location = %s, max_attendees = %s
            WHERE event_id = %s
            ''',
            (event_name, category, description, event_date, event_time, location, max_attendees, event_id)
        )
        db.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('event_info.events'))

    # Fetch the current event details for pre-filling the form
    cursor.execute('SELECT * FROM event_info WHERE event_id = %s', (event_id,))
    current_event_info = cursor.fetchone()

    if not current_event_info:
        flash('Event not found.', 'danger')
        return redirect(url_for('event_info.events'))

    return render_template('events_update.html', current_event_info=current_event_info)

# Route for deleting an event
@event_info.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the event
    cursor.execute('DELETE FROM event_info WHERE event_id = %s', (event_id,))
    db.commit()

    flash('Event deleted successfully!', 'danger')
    return redirect(url_for('event_info.events'))
