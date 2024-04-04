from models import UserGroup
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:6947@localhost/food_donation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def create_user_groups():
    existing_groups = UserGroup.query.all()
    
    if existing_groups:
        print("User groups already exist.")
        return
    
    donator_group = UserGroup(name='donator', description='User group for donator users')
    db.session.add(donator_group)
    
    # Create volunteer user group
    volunteer_group = UserGroup(name='volunteer', description='User group for volunteer users (delivery agents)')
    db.session.add(volunteer_group)
    
    try:
        db.session.commit()
        print("User groups created successfully.")
    except Exception as e:
        db.session.rollback()
        print("Failed to create user groups.")
        print(e)
        
create_user_groups()