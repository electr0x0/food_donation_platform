# Introduction:

This project is a web application built using Flask, a lightweight web framework in Python. It serves as a platform for managing food donations, allowing users to register, create donation requests, and volunteer to pick up and distribute food donations.

# Features:

- User authentication and authorization
- User registration and profile management
- Donation request creation and management
- Volunteer sign-up and food pickup scheduling
- Admin dashboard for managing users and donations
- & Many More

# How to Run:

1. Clone the repository:

- `git clone https://github.com/electr0x0/food_donation_platform`

2. Install the required dependencies:

- `pip install -r requirements.txt`

3. Create a database in your MySQL named "food_donation".
- `CREATE DATABASE food_donation`

4. Run the application:

- `python app.py`

5. Access the application in your web browser at http://domain:5000.

6. Goto these urls http://domain:5000/update-groups & http://domain:5000/init-admin to create user groups and admin user (for first run).

## Note: Make sure to configure the database connection string and other environment variables as necessary found in .env .

# Contributing:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/xyz).
3. Make your changes and commit them (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/xyz).
5. Create a new Pull Request.

# License:

This project is licensed under the MIT License.