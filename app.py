from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    approved = db.Column(db.Boolean, default=False)

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class UserProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('problems', lazy=True))

class ProblemReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response = db.Column(db.Text)
    problem_id = db.Column(db.Integer, db.ForeignKey('user_problem.id'), nullable=False)
    problem = db.relationship('UserProblem', backref=db.backref('reviews', lazy=True))

# Routes
@app.route('/companies/awaiting_approval', methods=['GET'])
def get_companies_awaiting_approval():
    companies = Company.query.filter_by(approved=False).all()
    return jsonify([company.name for company in companies])

@app.route('/companies/approve', methods=['POST'])
def approve_company():
    company_id = request.json.get('company_id')
    company = Company.query.get(company_id)
    if company:
        company.approved = True
        db.session.commit()
        return jsonify({'message': 'Company approved successfully'})
    else:
        return jsonify({'message': 'Company not found'})

@app.route('/companies/reject', methods=['POST'])
def reject_company():
    company_id = request.json.get('company_id')
    company = Company.query.get(company_id)
    if company:
        db.session.delete(company)
        db.session.commit()
        return jsonify({'message': 'Company rejected successfully'})
    else:
        return jsonify({'message': 'Company not found'})

@app.route('/admin/create', methods=['POST'])
def create_admin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    hashed_password = generate_password_hash(password)
    new_admin = AdminUser(username=username, password_hash=hashed_password)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': 'Admin created successfully'})

@app.route('/admin', methods=['GET'])
def get_admin_users():
    admins = AdminUser.query.all()
    return jsonify([admin.username for admin in admins])

# Other routes remain the same...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
