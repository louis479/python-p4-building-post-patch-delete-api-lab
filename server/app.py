#!/usr/bin/env python3



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if bakery:
        bakery_serialized = bakery.to_dict()
        return make_response(bakery_serialized, 200)
    return make_response({"error": "Bakery not found"}, 404)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(baked_goods_by_price_serialized, 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if most_expensive:
        most_expensive_serialized = most_expensive.to_dict()
        return make_response(most_expensive_serialized, 200)
    return make_response({"error": "No baked goods found"}, 404)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    '''Creates a new baked good in the database and returns its data as JSON.'''
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    # Validate the form data
    if not name or not price or not bakery_id:
        return jsonify({"error": "Missing required fields"}), 400

    # Create a new baked good
    baked_good = BakedGood(name=name, price=float(price), bakery_id=int(bakery_id))
    db.session.add(baked_good)
    db.session.commit()

    return jsonify({
        "id": baked_good.id,
        "name": baked_good.name,
        "price": baked_good.price,
        "bakery_id": baked_good.bakery_id
    }), 201


@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    '''Updates the name of the bakery and returns its data as JSON.'''
    bakery = Bakery.query.get(id)
    
    if not bakery:
        return jsonify({"error": "Bakery not found"}), 404
    
    # Update the name if provided in the form data
    name = request.form.get('name')
    if name:
        bakery.name = name
        db.session.commit()

    return jsonify({
        "id": bakery.id,
        "name": bakery.name
    }), 200


@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    '''Deletes a baked good and returns a confirmation message.'''
    baked_good = BakedGood.query.get(id)

    if not baked_good:
        return jsonify({"error": "Baked good not found"}), 404
    
    db.session.delete(baked_good)
    db.session.commit()

    return jsonify({"message": "Baked good successfully deleted"}), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
