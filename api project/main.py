from flask import Flask, request, jsonify  
from flask_swagger import swagger  
from flasgger import Swagger  
import sqlite3  
from sqlite3 import Error  

app = Flask(__name__)  
swagger = Swagger(app)  

path = "products.db"  

shop = []  
categorie = [{}]  

# Database setup  
try:  
    con = sqlite3.connect(path)  
    cur = con.cursor()  
    cur.execute("""CREATE TABLE IF NOT EXISTS categorie(  
                    id INTEGER PRIMARY KEY AUTOINCREMENT, categorie TEXT)""")   
    cur.execute("""CREATE TABLE IF NOT EXISTS all_products  
                    (product TEXT, price INTEGER, categorie_id INTEGER,   
                    FOREIGN KEY(categorie_id) REFERENCES categorie(id)) """)  
    con.commit()   
except Error:  
    print(Error)   
finally:  
    con.close()   

@app.route('/category/get_all', methods=['GET'])  
def get_product():  
    """  
    Get all categories  
    ---  
    responses:  
      200:  
        description: A list of categories  
    """  
    try:  
        con = sqlite3.connect(path)  
        cur = con.cursor()  
        cur.execute("""SELECT id,categorie FROM categorie """)  
        categories = cur.fetchall()  
        categories_list = [{"id": category[0], "categorie": category[1]} for category in categories]   
        return jsonify(categories_list), 200  
    except Error:  
        return jsonify({"message": "Error occurred during fetching categories"}), 500  

@app.route('/category/create', methods=["POST"])  
def create_categorie():  
    """  
    Create a new category  
    ---  
    parameters:  
      - name: categorie  
        type: string  
        required: true  
        description: The name of the category  
    responses:  
      201:  
        description: The created category  
      400:  
        description: Invalid input  
    """  
    if not request.json or 'categorie' not in request.json:  
        return jsonify({"message": "invalid input"}), 400  

    new_categorie = {  
        "categorie": request.json['categorie']  
    }  
    try:  
        con = sqlite3.connect(path)  
        cur = con.cursor()  
        cur.execute("""INSERT INTO categorie(categorie)  
                    VALUES(?)""", (new_categorie['categorie'],))  
        con.commit()  
    except Error:  
        return jsonify({"message": "Error occurred during category creation"}), 500  
    finally:  
        con.close()  
        return jsonify(new_categorie), 201  

@app.route('/new/product', methods=['POST'])  
def create_product():  
    """  
    Create a new product  
    ---  
    parameters:  
      - name: product  
        type: string  
        required: true  
      - name: price  
        type: integer  
        required: true  
      - name: categorie  
        type: string  
        required: true  
    responses:  
      201:  
        description: Product created successfully  
      404:  
        description: Category not found  
    """  
    if not request.json or 'product' not in request.json or 'price' not in request.json or 'categorie' not in request.json:  
        return jsonify({"message": "Invalid input"}), 400  

    new_product = {  
        "product": request.json['product'],  
        "categorie": request.json["categorie"],  
        "price": request.json['price']  
    }  
    con = sqlite3.connect(path)  

    cur = con.cursor()  
    cur.execute("""SELECT id FROM categorie WHERE categorie=? """, (new_product['categorie'],))  
    category = cur.fetchone()  

    if category is None:  
        return jsonify({"message": "not found any"}), 404  

    category_id = category[0]   
    cur.execute("""INSERT INTO all_products(product, price, categorie_id)  
                   VALUES(?, ?, ?)""", (new_product['product'], new_product['price'], category_id))  
    
    con.commit()  
    con.close()  
    return jsonify({"message": "create successfully"}), 201  
    

@app.route('/get/product/<string:category>', methods=['GET'])  
def get_product_by_categorie(category):  
    """  
    Get products by category  
    ---  
    parameters:  
      - name: category  
        type: string  
        required: true  
    responses:  
      200:  
        description: A list of products  
    """  
    con = sqlite3.connect(path)  
    cur = con.cursor()  
    cur.execute("""SELECT product,price FROM all_products  
                WHERE categorie_id = (SELECT id FROM categorie WHERE categorie = ?) """, (category,))  
    products = cur.fetchall()  
    product_list = [{"product": product[0], "price": product[1]} for product in products]   
    con.close()  
    return jsonify(product_list), 200  

@app.route('/update/product', methods=['PUT'])  
def update_product():  
    """  
    Update an existing product  
    ---  
    parameters:  
      - name: product  
        type: string  
        required: true  
      - name: categorie  
        type: string  
        required: false  
      - name: price  
        type: integer  
        required: false  
    responses:  
      200:  
        description: Product updated successfully  
      404:  
        description: Product not found  
    """  
    if not request.json or 'product' not in request.json:  
        return jsonify({"message": "Invalid input"}), 400  
        
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
    app.run(debug=True)  
