from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db

attendee_info = Blueprint('attendee_info', __name__)

@attendee_info.route('/attendees', methods=['GET', 'POST'])
def attendees():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new attendee
    if request.method == 'POST':
        user_id = request.form['user_id']
        event_id = request.form['event_id']
        rsvp_date = request.form['rsvp_date']
        status = request.form['status']

        # Insert the new attendee into the database
        cursor.execute(
            'INSERT INTO attendee_info (user_id, event_id, rsvp_date, status) VALUES (%s, %s, %s, %s)',
            (user_id, event_id, rsvp_date, status)
        )
        db.commit()

        flash('New attendee added successfully!', 'success')
        return redirect(url_for('attendee_info.attendees'))

    # Handle GET request to display all attendees
    cursor.execute('SELECT * FROM attendee_info')
    all_attendees = cursor.fetchall()
    return render_template('attendees.html', all_attendees=all_attendees)  # Ensure this matches your file name

@attendee_info.route('/update_attendee/<int:attendee_id>', methods=['GET', 'POST'])
def update_attendee(attendee_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Update the attendee's details
        user_id = request.form['user_id']
        event_id = request.form['event_id']
        rsvp_date = request.form['rsvp_date']
        status = request.form['status']

        cursor.execute(
            'UPDATE attendee_info SET user_id = %s, event_id = %s, rsvp_date = %s, status = %s WHERE attendee_id = %s',
            (user_id, event_id, rsvp_date, status, attendee_id))
        db.commit()

        flash('Attendee updated successfully!', 'success')
        return redirect(url_for('attendee_info.attendees'))

    # GET method: fetch attendee's current data for pre-populating the form
    cursor.execute('SELECT * FROM attendee_info WHERE attendee_id = %s', (attendee_id,))
    current_attendee_info = cursor.fetchone()
    return render_template('attendees_update.html', current_attendee_info=current_attendee_info)

@attendee_info.route('/delete_attendee/<int:attendee_id>', methods=['POST'])
def delete_attendee(attendee_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the attendee
    cursor.execute('DELETE FROM attendee_info WHERE attendee_id = %s', (attendee_id,))
    db.commit()

    flash('Attendee deleted successfully!', 'danger')
    return redirect(url_for('attendee_info.attendees'))
