from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    orders = db.relationship('Order', backref='store_keeper', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.created_at}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt = db.Column(db.LargeBinary, nullable=True)  # Storing the receipt image or document
    file_name = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    received_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    remark = db.Column(db.Text, nullable=True)
    invoiced = db.Column(db.Boolean, nullable=False, default=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False)
    payment = db.Column(db.LargeBinary, nullable=True)
    payment_file_name = db.Column(db.Text)
    recived_on = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"Order(id={self.id}, receipt=<BLOB>, amount={self.amount}, "
            f"received_by={self.received_by}, supplier_id={self.supplier_id}, "
            f"invoiced={self.invoiced}, entity_id={self.entity_id}, remark={self.remark})"
        )

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    invoiced = db.Column(db.Boolean, default=True)
    primary_contact = db.Column(db.String(20), nullable=True)
    bank_account = db.Column(db.String(30))
    orders = db.relationship('Order', backref='supplier', lazy=True)

    def __repr__(self):
        return f"Supplier(id='{self.id}', name='{self.name}', invoiced={self.invoiced})"

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    location = db.Column(db.String(30), nullable=False)
    orders = db.relationship('Order', backref='entity', lazy=True)

    def __repr__(self):
        return f"Entity(id='{self.id}', name='{self.name}', location='{self.location}')"

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Allowing for more descriptive role names
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"Role(id='{self.id}', name='{self.name}')"

# Uncomment and complete the Invoice model if needed in the future
# class Invoice(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.LargeBinary)
#     orders = db.relationship('Order', backref='invoice', lazy=True)
#     def __repr__(self):
#         return f"Invoice(id='{self.id}', data='<BLOB>')"
