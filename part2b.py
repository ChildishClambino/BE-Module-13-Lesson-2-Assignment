import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import func, and_
from datetime import datetime, date
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'factory_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database Models
class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    department = db.Column(db.String(50))
    
    productions = db.relationship('Production', back_populates='employee')

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    
    productions = db.relationship('Production', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')

class Production(db.Model):
    __tablename__ = 'productions'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    
    employee = db.relationship('Employee', back_populates='productions')
    product = db.relationship('Product', back_populates='productions')

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    
    orders = db.relationship('Order', back_populates='customer')

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    order_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    customer = db.relationship('Customer', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

# Schemas
class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

class ProductionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Production
        load_instance = True
    
    employee = ma.Nested(EmployeeSchema)
    product = ma.Nested(ProductSchema)

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
    
    customer = ma.Nested(CustomerSchema)

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
production_schema = ProductionSchema()
productions_schema = ProductionSchema(many=True)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

def create_database():
    with app.app_context():
        db.create_all()
        print("Database created successfully!")

# Sample Data Population
def populate_sample_data():
    with app.app_context():
        # Clear existing data
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.query(Production).delete()
        db.session.query(Employee).delete()
        db.session.query(Product).delete()
        db.session.query(Customer).delete()
        
        # Create Employees
        employees = [
            Employee(name='John Doe', email='john@example.com', department='Production'),
            Employee(name='Jane Smith', email='jane@example.com', department='Quality Control')
        ]
        db.session.add_all(employees)
        
        # Create Products
        products = [
            Product(name='Laptop', category='Electronics', price=1000),
            Product(name='Smartphone', category='Electronics', price=500),
            Product(name='Tablet', category='Electronics', price=300)
        ]
        db.session.add_all(products)
        
        # Create Customers
        customers = [
            Customer(name='Alice Brown', email='alice@example.com', phone='123-456-7890'),
            Customer(name='Bob Wilson', email='bob@example.com', phone='987-654-3210')
        ]
        db.session.add_all(customers)
        
        # Create Productions
        productions = [
            Production(employee=employees[0], product=products[0], quantity=50, production_date=date(2024, 1, 15)),
            Production(employee=employees[1], product=products[1], quantity=75, production_date=date(2024, 1, 16))
        ]
        db.session.add_all(productions)
        
        # Create Orders
        orders = [
            Order(customer=customers[0], order_date=date(2024, 1, 20), total_amount=3000),
            Order(customer=customers[1], order_date=date(2024, 1, 21), total_amount=1500)
        ]
        db.session.add_all(orders)
        
        # Create Order Items
        order_items = [
            OrderItem(order=orders[0], product=products[0], quantity=3, price=1000),
            OrderItem(order=orders[1], product=products[1], quantity=3, price=500)
        ]
        db.session.add_all(order_items)
        
        db.session.commit()
        print("Sample data populated successfully!")

# API Endpoints to be used wiff postman
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify(employees_schema.dump(employees))

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify(products_schema.dump(products))

@app.route('/employee-performance', methods=['GET'])
def employee_performance():
    """
    Calculate total quantity of products each employee has produced
    """
    performance_data = (
        db.session.query(
            Employee.name, 
            func.sum(Production.quantity).label('total_quantity')
        )
        .join(Production, Employee.id == Production.employee_id)
        .group_by(Employee.name)
        .all()
    )
    
    result = [
        {
            'employee_name': name,
            'total_quantity': total_quantity
        } for name, total_quantity in performance_data
    ]
    
    return jsonify(result)

@app.route('/top-selling-products', methods=['GET'])
def top_selling_products():
    """
    Find top-selling products based on total quantity ordered
    """
    top_n = request.args.get('top_n', default=5, type=int)
    
    top_products = (
        db.session.query(
            Product.name, 
            func.sum(OrderItem.quantity).label('total_ordered')
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(top_n)
        .all()
    )
    
    result = [
        {
            'product_name': name,
            'total_ordered': total_ordered
        } for name, total_ordered in top_products
    ]
    
    return jsonify(result)

@app.route('/customer-lifetime-value', methods=['GET'])
def customer_lifetime_value():
    """
    Calculate total order value for each customer
    """
    threshold = request.args.get('threshold', default=1000, type=float)
    
    customer_value = (
        db.session.query(
            Customer.name, 
            func.sum(Order.total_amount).label('total_value')
        )
        .join(Order, Customer.id == Order.customer_id)
        .group_by(Customer.name)
        .having(func.sum(Order.total_amount) > threshold)
        .all()
    )
    
    result = [
        {
            'customer_name': name,
            'total_value': float(total_value)
        } for name, total_value in customer_value
    ]
    
    return jsonify(result)

@app.route('/production-efficiency', methods=['GET'])
def production_efficiency():
    """
    Calculate total quantity produced for each product on a specific date
    """
    date_str = request.args.get('production_date', default=datetime.now().date().isoformat())
    
    try:
        production_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    product_production = (
        db.session.query(
            Product.name, 
            func.sum(Production.quantity).label('total_quantity')
        )
        .join(Production, Product.id == Production.product_id)
        .filter(Production.production_date == production_date)
        .group_by(Product.name)
        .all()
    )
    
    result = [
        {
            'product_name': name,
            'total_quantity': total_quantity
        } for name, total_quantity in product_production
    ]
    
    return jsonify(result)


if __name__ == '__main__':
    create_database()
    populate_sample_data()
    
    app.run(debug=True)

# pip install requirements.txt
# type "pip install -r requirements.txt" in the terminal