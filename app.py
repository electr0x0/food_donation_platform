# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import app, db, User, UserGroup, DonationFood, WebsiteTraffic
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sign_in'

app.config['UPLOAD_FOLDER'] = "static/uploads/donorImages/food"


# Define user groups
user_groups = {'donator': None, 'volunteer': None, 'admin': 'Predefined'}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('home/index.html', )

#Dashboard Routes Start
@app.route('/dashboard')
@login_required
def dashboard():
    food_donations = DonationFood.query.filter_by(user_id=current_user.id).all()
    total_weight = sum(donation_request.weight_kg for donation_request in food_donations)
    indi_weight = [0,0,0,0,0]
    
    for food in food_donations:
        match food.food_type:
            case "Fruits":
                indi_weight[0] += food.weight_kg
            case "Vegetables":
                indi_weight[1] += food.weight_kg
            case "Grains":
                indi_weight[2] += food.weight_kg
            case "Dairy":
                indi_weight[3] += food.weight_kg
            case "Meat":
                indi_weight[4] += food.weight_kg
                
    return render_template('dashboard/home/index.html', segment= 'index', total_donation_req_count = len(food_donations), total_weight_of_food =total_weight, indi_donation_weight = indi_weight )

@app.route('/tables')
@login_required
def tables():
    return render_template('dashboard/home/tables.html', segment= 'tables')

@app.route('/notifications')
@login_required
def notifications():
    return render_template('dashboard/home/notifications.html', segment= 'notifications')

@app.route('/profile')
@login_required
def profile():
    food_donation = DonationFood.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/home/profile.html', segment= 'profile', donations = food_donation)

@app.route('/donate-food')
@login_required
def donate_food():
    return render_template('dashboard/home/donate-food.html', segment= 'donate-food')

@app.route('/billing')
@login_required
def billing():
    return render_template('dashboard/home/billing.html', segment='billing')

@app.route('/track-food')
@login_required
def track_food():
    food_donations = DonationFood.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/home/track-food.html',segment='track-food', food_donations=food_donations)

@app.route('/submit_donation', methods=['POST'])
@login_required
def submit_donation():
    if request.method == 'POST':
        food_type = request.form['foodType']
        pickup_time = request.form['pickupTime']
        weight_kg = request.form['weight']
        expiry_date = request.form['expiryDate']
        description = request.form['description']
        user_id = current_user.id
        status = 'pending'
        
        print(expiry_date)
        
        if 'file' in request.files:
            file = request.files['file']
            print(file)
            if file.filename != '':
                print(file.filename)
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
                os.makedirs(upload_dir, exist_ok=True)

                # Save file to upload directory
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

                # Save image path to database
                new_donation = DonationFood(user_id=user_id, food_type=food_type, pickup_time=pickup_time,
                                            weight_kg=weight_kg, expiry_date=expiry_date, description=description,
                                            image_path=file_path, status=status)
                db.session.add(new_donation)
                db.session.commit()

                flash('Your donation has been submitted successfully!', 'success')
                return redirect(url_for('track_food', successmsg ='Your donation has been submitted successfully!' ))
            else:
                flash('No file selected for upload.', 'danger')
        else:
            flash('File upload field is missing.', 'danger')

    # Handle form submission errors
    flash('Failed to submit donation. Please try again.', 'danger')
    return redirect(url_for('donate_food', errormsg ='Failed to submit donation. Please try again.' ))
#Dashboard Routes End

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('home/sign-in.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('sign_in'))

@app.route('/show-current-users')
@login_required
def show_current_users():
    users = User.query.all()
    return render_template('/home/show-users.html', users= users)

@app.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.address = request.form['address']
        user.organization = request.form['organization']
        user.user_group_id = request.form['user_group_id']
        db.session.commit()
        flash('User information updated successfully', 'success')
        return redirect(url_for('show_current_users'))
    return render_template('edit-user.html', user=user)

@app.route('/contact-us' ,methods=['POST', 'GET'])
def contact_us():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phonenumber']
        email = request.form['email']
        message = request.form['message']
        return (str([firstname,lastname,phone,email,message]))
    
    return render_template('home/contact-us.html')


@app.route('/about-us')
def about_us():
    return render_template('home/about-us.html')
    

@app.route('/sign-up/<user_group>', methods=['GET', 'POST'])
def register(user_group):
    if user_group not in user_groups:
        flash('Invalid user group', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        organization = request.form['organization']
        password = request.form['password']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        
        user_group_name = user_group
        user_group = UserGroup.query.filter_by(name=user_group_name).first()

        if not user_group:
            return('Invalid user group', 'error')

        finduser = User.query.filter_by(username=username).first()
        findemail = User.query.filter_by(email=email).first()

        if finduser:
            flash('Username already exists', 'error')
            return redirect(url_for('register', user_group=user_group_name, errmessage='Username already exists'))
        if findemail:
            flash('Email already exists', 'error')
            return redirect(url_for('register', user_group=user_group_name, errmessage='Email already exists'))

        new_user = User(username=username, first_name=first_name, email=email, last_name=last_name, address=address, organization=organization, password_hash=generate_password_hash(password), user_group_id=user_group.id, phone_number=phonenumber)

        if user_group_name == 'volunteer':
            new_user.availability = request.form.get('availability')
            new_user.skills = request.form['selected_skills']

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('sign_in', successmsg = "Registration successful. Please log in."))

    return render_template('home/sign-up.html', user_group=user_group)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('home/page-404.html'), 404

#Utility Funcs
@app.route('/show_dark_status',methods=['GET'])
def show_status_dark():
    return session['dark_mode']

@app.route('/update_dark_mode_state', methods=['POST'])
def update_dark_mode_state():
    state = request.json.get('state')
    session['dark_mode'] = state
    print(session['dark_mode'])
    return jsonify({'success': True})
#Utility Funcs End


# Volunteer Routes
@app.route('/pickup-food', methods = ['GET','POST'])
def pickup_food(food_id = None):
    if request.method == 'POST':
        food_donation = DonationFood.query.get(request.form.get('id'))
        if food_donation:
            food_donation.status = request.form.get('status')
            food_donation.picked_by = current_user.id
            print(food_donation.status)
            db.session.commit()
            
            flash('Food picked successfully!', 'success')
            return redirect(url_for('pickup_food', statusmsg='success'))
        else:
            return redirect(url_for('pickup_food', statusmsg='error'))
        
    # Query the database for pending food donations
    pending_food_donations = DonationFood.query.filter_by(status='pending').all()
    
    return render_template('dashboard/home/pickup-food.html', food_donations=pending_food_donations, segmet='pickup-food')

@app.route('/pending-deliveries', methods = ['GET', 'POST'])
@login_required
def pending_deliveries():
    if request.method == 'POST':
        food_donation = DonationFood.query.get(request.form.get('id'))
        if food_donation:
            food_donation.status = request.form.get('status')
            food_donation.picked_by = None
            db.session.commit()

    food_donations_deliveries = DonationFood.query.filter_by(picked_by=current_user.id).all()
    return render_template('dashboard/home/pending-deliveries.html', deliveries = food_donations_deliveries)

# Volunteer Routes End


#Admin Routes Start
def admin_required(func):
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_group_id == 3:
            return func(*args, **kwargs)
        else:
            return 'Unauthorized', 401
    # Set a unique endpoint name based on the original function name
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/manage-users')
@login_required
@admin_required
def manage_users():
    # Query users with group ID 1 (donors)
    donors = User.query.filter_by(user_group_id=1).all()
    
    # Query users with group ID 2 (volunteers)
    volunteers = User.query.filter_by(user_group_id=2).all()
    
    return render_template('dashboard/home/manage-users.html', donors = donors, volunteers = volunteers)

@app.route('/get_user/<int:user_id>')
@login_required
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'address': user.address,
        'phone_number': user.phone_number,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })
    
# Route to delete a volunteer
@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return 'User deleted successfully', 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500

# Route to handle updating volunteer information
@app.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    # Get data from the request form
    data = request.json
    user = User.query.get_or_404(user_id)
    try:
        # Update volunteer information
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.email = data.get('email')
        user.address = data.get('address')
        user.phone_number = data.get('phone_number')
        # Save changes to the database
        db.session.commit()
        return 'User information updated successfully', 200
    except Exception as e:
        db.session.rollback()
        return str(e)
    
@app.route('/traffic-data')
@login_required
@admin_required
def get_traffic_data():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    traffic_data = WebsiteTraffic.query.filter(WebsiteTraffic.date.between(start_date, end_date)).all()

    
    traffic_data_dict = {
        "labels": [data.date.strftime('%a') for data in traffic_data],
        "data": [data.views for data in traffic_data]
    }

    return jsonify(traffic_data_dict)

@app.before_request
def update_traffic():
    STATIC_PATHS = ['/static/', '/assets/']
    is_static_asset = any(request.path.startswith(path) for path in STATIC_PATHS)

    # If it's a static asset, return without updating traffic
    if is_static_asset:
        return

    # Get the current date
    current_date = datetime.now().date()

    # Check if there's a record for the current date
    traffic_data = WebsiteTraffic.query.filter_by(date=current_date).first()

    if traffic_data:
        # If a record exists, increment the view count
        traffic_data.views += 1
    else:
        # If no record exists, create a new one with a view count of 1
        new_traffic_data = WebsiteTraffic(date=current_date, views=1)
        db.session.add(new_traffic_data)

    # Commit the changes to the database
    db.session.commit()

@app.route('/update-groups')
def create_user_groups():
    existing_groups = UserGroup.query.all()
    
    if existing_groups:
        return "User groups already exist."
    
    donator_group = UserGroup(name='donator', description='User group for donator users')
    db.session.add(donator_group)
    
    # Create volunteer user group
    volunteer_group = UserGroup(name='volunteer', description='User group for volunteer users (delivery agents)')
    db.session.add(volunteer_group)
    
    admin_group = UserGroup(name='admin', description='User group for admin')
    db.session.add(admin_group)
    
    admin_user = User(username=os.getenv('ADMIN_USERNAME'), first_name='Admin', email='admin@fooddonation.org', last_name='Admin', address='None', organization='Food Donation', password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD')), user_group_id=3, phone_number=os.getenv('ADMIN_PHONE'))
    
    db.session.add(admin_user)
    try:
        db.session.commit()
        return "User groups created successfully."
    except Exception as e:
        db.session.rollback()
        return f"Failed to create user groups. {e}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')