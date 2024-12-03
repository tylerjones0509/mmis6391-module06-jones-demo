from flask import Flask, g
from .app_factory import create_app
from .db_connect import close_db, get_db

app = create_app()
app.secret_key = 'your-secret'  # Replace with an environment variable

# Register Blueprints
from app.blueprints.attendee_info import attendee_info
from app.blueprints.event_info import event_info
from app.blueprints.user_info import user_info

app.register_blueprint(attendee_info)
app.register_blueprint(event_info)
app.register_blueprint(user_info)



from . import routes

@app.before_request
def before_request():
    g.db = get_db()

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)

