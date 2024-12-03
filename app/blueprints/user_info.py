from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
from pymysql.cursors import DictCursor  # Import DictCursor

user_info = Blueprint('user_info', __name__)

# Route to display and filter users
@user_info.route('/users', methods=['GET', 'POST'])
def users():
    db = get_db()
    cursor = db.cursor(cursor=DictCursor)  # Use DictCursor for dictionary results

    # Handle POST request to add a new user
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_hash = request.form['password_hash']
        preferred_categories = request.form['preferred_categories']

        # Insert the new user into the database
        cursor.execute(
            'INSERT INTO user_info (username, email, password_hash, preferred_categories) VALUES (%s, %s, %s, %s)',
            (username, email, password_hash, preferred_categories)
        )
        db.commit()

        flash('New user added successfully!', 'success')
        return redirect(url_for('user_info.users'))

    # Handle GET request for filtering
    username_filter = request.args.get('username')
    email_filter = request.args.get('email')
    preferred_categories_filter = request.args.get('preferred_categories')

    # Construct SQL query for filtering
    query = 'SELECT * FROM user_info WHERE TRUE'
    params = []

    if username_filter:
        query += ' AND username LIKE %s'
        params.append(f'%{username_filter}%')

    if email_filter:
        query += ' AND email LIKE %s'
        params.append(f'%{email_filter}%')

    if preferred_categories_filter:
        query += ' AND preferred_categories LIKE %s'
        params.append(f'%{preferred_categories_filter}%')

    cursor.execute(query, params)
    all_users = cursor.fetchall()

    # Debugging: Print results for verification
    print(all_users)

    return render_template('users.html', all_users=all_users)

# Route to update a user's details
@user_info.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    db = get_db()
    cursor = db.cursor(cursor=DictCursor)  # Use DictCursor for dictionary results

    if request.method == 'POST':
        # Update the user's details
        username = request.form['username']
        email = request.form['email']
        password_hash = request.form['password_hash']
        preferred_categories = request.form['preferred_categories']

        cursor.execute(
            'UPDATE user_info SET username = %s, email = %s, password_hash = %s, preferred_categories = %s WHERE user_id = %s',
            (username, email, password_hash, preferred_categories, user_id)
        )
        db.commit()

        flash('User updated successfully!', 'success')
        return redirect(url_for('user_info.users'))

    # GET method: fetch the user's current data for pre-populating the form
    cursor.execute('SELECT * FROM user_info WHERE user_id = %s', (user_id,))
    current_user_data = cursor.fetchone()
    return render_template('users_update.html', current_user_data=current_user_data)

# Route to delete a user
@user_info.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor(cursor=DictCursor)  # Use DictCursor for dictionary results

    # Delete the user
    cursor.execute('DELETE FROM user_info WHERE user_id = %s', (user_id,))
    db.commit()

    flash('User deleted successfully!', 'danger')
    return redirect(url_for('user_info.users'))

