from functools import wraps
from app import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

def load_user(user_id):
    return User.query.get(int(user_id))

def get_all_users():
    users = User.query.all()
    return users

# returns True if login attempt succeeds, else False
def login(email, password):
    user = User.query.filter_by(email=email).first()

    # Verify user exists and password is correct
    if user and check_password_hash(user.password_hash, password):
        return login_user(user)
        
    return False

def logout():
    logout_user()


def signup(email, password, age, gender):
    # Check if the user already exists
    user = User.query.filter_by(email=email).first()
    if user: # user already exists
        return False
    
    # TODO: verify email
    # Hash the password and create a new user
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password, age=age, gender=gender)
    db.session.add(new_user)
    db.session.commit()
    return True

def delete_user(user_id, initiator='self'):
    if (initiator == 'self'):
        logout_user()
    # otherwise it means admin deleted him
    user = User.query.get(user_id)
    if user is not None and not user.is_admin:
        db.session.delete(user)
        db.session.commit()

# if admin deletes a user while the user is still logged in, that user will be able to see polls until his session expires
# however won't be able to create new polls or vote in polls





def add_admins(admins):
    for (admin_email, admin_pass) in admins.items():
        
        existing_user = User.query.filter_by(email=admin_email).first()
        if existing_user:
            print(f"User with email {admin_email} already exists. Skipping...")
            continue  # Skip adding this admin

        hashed_password = generate_password_hash(admin_pass)
        new_user = User(email=admin_email, password_hash=hashed_password, is_admin=True, age=23, gender="male")
        db.session.add(new_user)
        db.session.commit()



# append the @auth.admin_required decorator on any route now if you want it to be only accessed by an admin user
def admin_required(func):
    @login_required
    @wraps(func) # necessary, because otherwise decorator would change the name of every function it decorates to "wrapper". See https://stackoverflow.com/questions/308999/what-does-functools-wraps-do
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            return login_manager.unauthorized()
        return func(*args, **kwargs)
    return wrapper
