from flask import Flask, request, jsonify
import sqlite3
path = "products.db"
app = Flask(__name__)

shop = [
    {
        "product": "gym closes",
        "categorie": "gym",
        "price": 2000
    },
    {
        "product": "mouse",
        "categorie": "programing",
        "price": 1500
    }
]

con = sqlite3.connect(path)

cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS all_products
            (product TEXT, price INTEGER,categorie TEXT) """)

cur.execute("""CREATE TABLE IF NOT EXISTS gym_products
            (product TEXT, price INTEGER) """)
for item in shop:

    cur.execute("""INSERT INTO all_products(product,price,categorie) VALUES(?,?,?)""",
                (item["product"], item["price"], item['categorie']))
    if item['categorie'] == "gym":
        cur.execute("""INSERT INTO gym_products(product,price) VALUES(?,?)""",
                    (item['product'], item['price']))
con.commit()
con.close()


@app.route('/shop', methods=['GET'])
def get_product():
    return jsonify(shop)


@app.route('/shop/new', methods=['POST'])
def create_product():
    new_product = {
        "product": request.json['product'],
        "categorie": request.json["categorie"],
        "price": request.json['price']
    }
    shop.append(new_product)
    con = sqlite3.connect(path)

    cur = con.cursor()
    cur.execute("""INSERT INTO all_products(products,price,categorie)
                VALUES(?,?,?) """, (new_product['product'], new_product['price'], new_product['categorie']))
    if new_product['categorie'] == "gym":
        cur.execute("""INSERT INTO gym_products(product.price)
                    VALUES(?,?) """, (new_product['product'], new_product['price']))
    con.commit()
    con.close()
    return jsonify(new_product), 201


@app.route('/shop/programing', methods=['GET'])
def get_programing_product():
    programing_product = [
        product for product in shop if product['categorie'] == 'programing']

    return jsonify(programing_product)


@app.route('/shop/gym', methods=['GET'])
def get_gym_product():
    gym_product = [
        product for product in shop if product['categorie'] == 'gym'
    ]
    return jsonify(gym_product)


@app.route('/shop/update', methods=['PUT'])
def update_product():
    product_name = request.json['product']
    product_to_update = next(
        (product for product in shop if product['product'] == product_name), None)

    if product_to_update:
        product_to_update['categorie'] = request.json.get(
            'categorie', product_to_update['categorie'])
        product_to_update['price'] = request.json.get(
            'price', product_to_update['price'])
        return jsonify({"message": "product updated ", "product": product_to_update}), 200
    else:
        return jsonify({"message": "product not found"}), 404


if __name__ == "__main__":
    app.run()
