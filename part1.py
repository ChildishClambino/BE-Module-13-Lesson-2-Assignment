from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///factory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Models
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {"id": self.id, "description": self.description}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price}

# Pagination for Orders
@app.route('/orders', methods=['GET'])
def get_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Order.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "orders": [order.to_dict() for order in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    })

# Pagination for Products
@app.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "products": [product.to_dict() for product in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Order.query.first():
            db.session.add_all([Order(description=f"Order {i}") for i in range(1, 51)])
        if not Product.query.first():
            db.session.add_all([Product(name=f"Product {i}", price=i * 10.0) for i in range(1, 51)])
        db.session.commit()

    app.run(debug=True)
