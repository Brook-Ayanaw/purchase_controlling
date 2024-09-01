from flask import current_app as app
from flask import request, jsonify, url_for, send_file
from app.models import db, User, Order, Supplier, Entity, Role
from io import BytesIO
from datetime import datetime 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity 

@app.route('/')
def index():
    return "Welcome to the Flask App"


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    usernametbc = data['username']
    passwordtbc = data['password']
    #print(usernametbc + passwordtbc)

    # Find user by username
    user = User.query.filter_by(username=usernametbc).first()
    #print(user.email)
    # Validate user existence and password
    if not user or not (user.password == passwordtbc):
        return jsonify({'msg': 'Invalid username or password'}), 401

    # Generate JWT token
    access_token = create_access_token(identity={"id":user.id,"username": usernametbc, "role": user.role.name})
    print(access_token)

    return jsonify({'access_token': access_token}), 200


@app.route('/get_name', methods=['GET'])
@jwt_required()
def get_name():
    usernamessss = get_jwt_identity()
    user = User.query.filter_by(username=usernamessss).first()

    if user:
        return jsonify({'message': 'User found', 'name': user.username})
    else:
        return jsonify({'message': 'User not found'}), 404
@app.route('/get_role', methods=['GET'])
@jwt_required()
def get_role():
    usernamessss = get_jwt_identity()
    user = User.query.filter_by(username=usernamessss).first()

    if user:
        return jsonify({'message': 'User found', 'role': Role.query.filter_by(id=user.role_id).first().name})
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    if data:
        user = User(username=data["username"],name=data["name"], email=data["email"], password=data["password"],role_id=data["role_id"])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"user added"})
    else:
        return jsonify({"message": "no data"})

@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    data = []
    for u in users:
        user_data = {
            'id': u.id,
            'username': u.username,
            'name' : u.name,
            'email': u.email,
            'created_at': u.created_at,
            'password': u.password,
            'role' : u.role.name if u.role else "no role "
        }
        data.append(user_data)
    return jsonify(data)

@app.route('/delete_user/<int:id>', methods=['DELETE'])
@jwt_required
def delete_user(id):
    # Get the current user's identity from the JWT token
    current_user = get_jwt_identity()
    
    # Check if the user has the 'admin' role
    if current_user.get('role') != 'admin':
        return jsonify({"message": "Admin access required to delete orders"}), 403
    
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"user with ID {id} has been deleted."}), 200
    else:
        return jsonify({"message": "user not found."}), 404

@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    if data:
        order = Order(
            amount=data["amount"],
            received_by=data["received_by"],
            supplier_id=data["supplier_id"],
            remark=data["remark"],
            invoiced=data["invoiced"],
            entity_id=data["entity_id"]
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({"message":"order has been added"})
    else:
        return jsonify({"message": "no data or missing data"})
@app.route('/add_attachemnt/<int:id>', methods = ['PUT'])
def add_attachemnt(id):
    invoice = Order.query.get(id)
    file = request.files.get('hopa')
    file2 = request.files.get('dopa')
    if invoice and file:
        invoice.receipt = file.read()
        invoice.file_name = file.filename
        db.session.commit()
        return({'message':'added'})
    elif invoice and file2:
        invoice.payment = file2.read()
        invoice.payment_file_name = file2.filename
        db.session.commit()
        return({'message':'payment added'})
    else:
        db.session.rollback()
        return({'message' : 'no order or file'})
        

@app.route('/orders', methods=['GET'])
def list_order():
    orders = Order.query.all()
    data = []
    for order in orders:
        order_data = {
            'id': order.id,
            'amount': order.amount,
            'received_by': order.store_keeper.name,  # Assuming store_keeper relationship
            'remark': order.remark,
            'supplier': order.supplier.name,  # Assuming supplier relationship
            'invoiced': order.invoiced,
            'entity': order.entity.name,  # Assuming entity relationship
            'receipt_url': url_for('download_receipt', order_id=order.id, _external=True),  # URL for downloading the receipt
            'payment_url' : url_for('download_payment_slip', order_id = order.id, _external = True)
        }
        data.append(order_data)
    return jsonify(data)

@app.route('/download_receipt/<int:order_id>', methods=['GET'])
def download_receipt(order_id):
    invoice = Order.query.get(order_id)
    if invoice is None or invoice.id is None or invoice.receipt is None:
        return jsonify({'message': 'Receipt not found'}), 404
    
    return send_file(
        BytesIO(invoice.receipt),
        download_name=invoice.file_name,  # Adjust the filename and extension as needed
        #mimetype='application/pdf'  # Adjust the MIME type based on your receipt format
    )
@app.route('/download_payment_slip/<int:order_id>', methods=['GET'])
def download_payment_slip(order_id):
    invoice = Order.query.get(order_id)
    if invoice is None or invoice.id is None or invoice.payment is None:
        return jsonify({'message': 'Receipt not found'}), 404
    
    return send_file(
        BytesIO(invoice.payment),
        download_name=invoice.payment_file_name,  # Adjust the filename and extension as needed
        #mimetype='application/pdf'  # Adjust the MIME type based on your receipt format
    )
# @app.route('/delete_order/<int:id>', methods=['DELETE'])
# @jwt_required
# def delete_order(id):
#     # Get the current user's identity from the JWT token
#     current_user = get_jwt_identity()
#     if current_user.role != 'admin':
#         return (jsonify({"message":"you need to contact your admin for this"}))
    
#     order = Order.query.get(id)
#     if order:
#         db.session.delete(order)
#         db.session.commit()
#         return jsonify({"message": f"order with ID {id} has been deleted."}), 200
#     else:
#         return jsonify({"message": "order not found."}), 404
@app.route('/delete_order/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_order(id):
    # Get the current user's identity from the JWT token
    current_user = get_jwt_identity()
    
    # Check if the user has the 'admin' role
    if current_user.get('role') != 'admin':
        return jsonify({"message": "Admin access required to delete orders"}), 403
    
    # Find the order by ID and delete if it exists
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": f"Order with ID {id} has been deleted."}), 200
    else:
        return jsonify({"message": "Order not found."}), 404

@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    data = request.get_json()
    if data:
        supplier = Supplier(
            name=data["name"],
            invoiced=data["invoiced"],
            primary_contact=data["primary_contact"],
            bank_account=data["bank_account"]
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify({"messgae":"added supplier"})
    else:
        return jsonify({"message": "no data or missing data"})

@app.route('/suppliers', methods=['GET'])
def list_suppliers():
    suppliers = Supplier.query.all()
    data = []
    for supplier in suppliers:
        supplier_data = {
            'id': supplier.id,
            'name': supplier.name,
            'invoiced': supplier.invoiced,
            'primary_contact': supplier.primary_contact,
            'bank_account': supplier.bank_account
        }
        data.append(supplier_data)
    return jsonify(data)

@app.route('/delete_supplier/<int:id>', methods=['DELETE'])
def delete_supplier(id):
    supplier = Supplier.query.get(id)
    if supplier:
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({"message": f"supplier with ID {id} has been deleted."}), 200
    else:
        return jsonify({"message": "supplier not found."}), 404

@app.route('/add_entity', methods=['POST'])
def add_entity():
    data = request.get_json()
    if data:
        entity = Entity(name=data["name"], location=data["location"])
        db.session.add(entity)
        db.session.commit()
        return f"Added entity"
    else:
        return jsonify({"message": "no data or missing data"})

@app.route('/entities', methods=['GET'])
def list_entities():
    entities = Entity.query.all()
    data = []
    for entity in entities:
        entity_data = {
            'id': entity.id,
            'name': entity.name,
            'location': entity.location
        }
        data.append(entity_data)
    return jsonify(data)

@app.route('/delete_entity/<int:id>', methods=['DELETE'])
def delete_entity(id):
    entity = Entity.query.get(id)
    if entity:
        db.session.delete(entity)
        db.session.commit()
        return jsonify({"message": f"entity with ID {id} has been deleted."}), 200
    else:
        return jsonify({"message": "entity not found."}), 404

@app.route('/add_role', methods=['POST'])
def add_role():
    data = request.get_json()
    if data:
        role = Role(name=data["name"])
        db.session.add(role)
        db.session.commit()
        return f"Added role"
    else:
        return jsonify({"message": "no data or missing data"})

@app.route('/roles', methods=['GET'])
def list_roles():
    roles = Role.query.all()
    data = []
    for role in roles:
        role_data = {
            'id': role.id,
            'name': role.name
        }
        data.append(role_data)
    return jsonify(data)

@app.route('/delete_role/<int:id>', methods=['DELETE'])
def delete_role(id):
    role = Role.query.get(id)
    if role:
        db.session.delete(role)
        db.session.commit()
        return jsonify({"message": f"Role with ID {id} has been deleted."}), 200
    else:
        return jsonify({"message": "Role not found."}), 404
@app.route('/search_by_entity', methods=['POST','GET'])
def search():
    data=request.get_json()
    result = []
    if data['entity']:
        entity = (Entity.query.filter_by(name = data['entity']).first())
        print(entity)
        if not entity:
            return {"message" : "invalid entry"}
        else:
            o = Order.query.filter_by(entity_id = entity.id).all()
            for order in o:
                result.append ({
                    "amount" : order.amount,
                    "id" : order.id
                })
            return jsonify(result)
    else:
        return {"message":"please enter data"}
@app.route('/search_by_supplier', methods=['POST','GET'])
def search_by_sup():
    data=request.get_json()
    result = []
    Total = 0
    if data['supplier']:
        supplier = (Supplier.query.filter_by(name = data['supplier']).first())
        print(supplier)
        if not supplier:
            return {"message" : "invalid entry"}
        else:
            o = Order.query.filter_by(supplier_id = supplier.id).all()
            for order in o:
                Total = Total+order.amount
                result.append ({
                    "amount" : order.amount,
                    "id" : order.id
                })
            result.append({"total_value":Total})
            return jsonify(result)
    else:
        return {"message":"please enter data"}
@app.route('/search_by_time', methods=['GET'])
def search_by_time():
    from_date_str = request.args.get('from')
    to_date_str = request.args.get('to')
    result = []
    Total = 0
    
    if not from_date_str or not to_date_str:
        return jsonify({"message": "Please provide 'from' and 'to' date parameters"}), 400

    try:
        # Convert the date strings to datetime objects
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

        # Filter orders based on the date range
        values = Order.query.filter(Order.recived_on.between(from_date, to_date)).all()

        if values:
            for v in values:
                result.append({
                    "id": v.id,
                    "amount": v.amount,
                    "entity": v.entity.name
                })
                Total += v.amount
            result.append({"total_value": Total})
            return jsonify(result)
        else:
            return jsonify({"message": "No records found for the given date range"}), 404

    except ValueError:
        return jsonify({"message": "Invalid date format. Please use YYYY-MM-DD."}), 400
