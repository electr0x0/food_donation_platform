# models.py
from flask import Flask
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:6947@192.168.0.103/food_donation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class DonationFood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(50), nullable=False)
    pickup_time = db.Column(db.DateTime, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    status = db.Column(db.String(50), nullable=False)
    picked_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    user = relationship("User", foreign_keys=[user_id])

    # Define relationship with the User model
    picked_by_user = relationship("User", foreign_keys=[picked_by])

    def __repr__(self):
        return f"DonationFood(id={self.id}, user_id={self.user_id}, food_type={self.food_type}, " \
               f"pickup_time={self.pickup_time}, weight_kg={self.weight_kg}, expiry_date={self.expiry_date}, " \
               f"description={self.description}, image_path={self.image_path}, created_at={self.created_at}, status={self.status})"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) 
    first_name = db.Column(db.String(100), unique=False, nullable=False)
    last_name = db.Column(db.String(100), unique=False, nullable=False)
    
    email = db.Column(db.String(250), unique=True, nullable=False)
    
    address = db.Column(db.String(100), unique=False, nullable=False)
    
    organization = db.Column(db.String(100), unique=False, nullable=True)
    
    password_hash = db.Column(db.String(200), nullable=False)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_group.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    # Fields specific to Volunteers
    availability = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.String(500), nullable=True)
    
    
    # Common
    phone_number = db.Column(db.String(15), nullable=False)
    profile_picture = db.Column(db.String(250), nullable=True)
    
    # Define relationship with DonationFood model for user_id
    donated_foods = relationship("DonationFood", foreign_keys=[DonationFood.user_id])

    # Define relationship with DonationFood model for picked_by_id
    picked_foods = relationship("DonationFood", foreign_keys=[DonationFood.picked_by])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    
