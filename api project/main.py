from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error
path = "products.db"
app = Flask(__name__)

shop = [
{

}
]
categorie=[{}]
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
    try:
        con = sqlite3.connect(path)

        cur = con.cursor()
        cur.execute("""SELECT id,categorie FROM categorie """)
        categories=cur.fetchall()
        categories_list = [{"id": category[0], "categorie": category[1]} for category in categories] 

        return jsonify(categories_list)
    except Error:
        print(Error)

@app.route('/category/create',methods=["POST"])
def create_categorie():
    new_categorie={
        "categorie":request.json['categorie']
    }
    categorie.append(new_categorie)
    try:
        con = sqlite3.connect(path)

        cur = con.cursor()
        cur.execute("""INSERT INTO categorie(categorie)
                    VALUES(?)""",(new_categorie['categorie'],))
        con.commit()
    except Error:
        print(Error)
    finally:
        con.close()
        return jsonify(new_categorie),201


@app.route('/new/product', methods=['POST'])  
def create_product():  
    new_product = {  
        "product": request.json['product'],  
        "categorie": request.json["categorie"],  
        "price": request.json['price']  
    }  
    shop.append(new_product)  
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
    return "create succesfully",201
    


@app.route('/get/product/<string:category>', methods = ['GET'])
def get_product_by_categorie(category):

    con = sqlite3.connect(path)

    cur = con.cursor()
    cur.execute("""SELECT product,price FROM all_products
                WHERE categorie_id = (SELECT id FROM categorie WHERE categorie = ?) """,(category,))
    products=cur.fetchall()
    product_list=[{"products" : product[0], "price" : product[1] } for product in products ] 
    con.close()
    return jsonify(product_list)
    


@app.route('/update/product', methods=['PUT'])
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
