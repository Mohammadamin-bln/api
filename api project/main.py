from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql, Error
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# PostgreSQL connection parameters
DATABASE_URL = "postgresql://root:KlOqbfpQFZIPh1wkniMbGvGk@grande-casse.liara.cloud:33563/postgres"

# Initialize the database
def init_db():
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS categorie(  
                    id SERIAL PRIMARY KEY, categorie TEXT)""")

        cur.execute("""CREATE TABLE IF NOT EXISTS all_products  
                    (product TEXT, price INTEGER, categorie_id INTEGER,   
                    FOREIGN KEY(categorie_id) REFERENCES categorie(id)) """)
        
        con.commit()
    except Error as e:
        print(e)
    finally:
        if con:
            cur.close()
            con.close()

init_db()

@app.route('/category/get_all', methods=['GET'])
def get_product():
    """  
    Get all categories  
    ---  
    responses:  
      200:  
        description: A list of categories  
        schema:  
          type: array  
          items:  
            type: object  
            properties:  
              id:  
                type: integer  
              categorie:  
                type: string  
    """
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        cur.execute("SELECT id, categorie FROM categorie")
        categories = cur.fetchall()
        categories_list = [{"id": category[0], "categorie": category[1]} for category in categories]

        return jsonify(categories_list)
    except Error as e:
        print(e)
    finally:
        if con:
            cur.close()
            con.close()

@app.route('/category/create', methods=["POST"])
def create_categorie():
    """  
    Create a new category  
    ---  
    parameters:  
      - name: categorie  
        in: body  
        required: true  
        schema:  
          type: object  
          properties:  
            categorie:  
              type: string  
    responses:  
      201:  
        description: The created category  
        schema:  
          type: object  
          properties:  
            id:  
              type: integer  
            categorie:  
              type: string  
    """
    new_categorie = {
        "categorie": request.json['categorie']
    }
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        cur.execute("INSERT INTO categorie(categorie) VALUES(%s) RETURNING id", (new_categorie['categorie'],))
        new_categorie['id'] = cur.fetchone()[0]
        con.commit()
    except Error as e:
        print(e)
    finally:
        if con:
            cur.close()
            con.close()
        return jsonify(new_categorie), 201

@app.route('/product/add', methods=['POST'])
def create_product():
    """  
    Create a new product  
    ---  
    parameters:  
      - name: product  
        in: body  
        required: true  
        schema:  
          type: object  
          properties:  
            product:  
              type: string  
            categorie:  
              type: string  
            price:  
              type: integer  
    responses:  
      201:  
        description: Product created successfully  
    """
    new_product = {
        "product": request.json['product'],
        "categorie": request.json["categorie"],
        "price": request.json['price']
    }
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        cur.execute("SELECT id FROM categorie WHERE categorie=%s", (new_product['categorie'],))
        category = cur.fetchone()

        if category is None:
            return jsonify({"message": "Category not found"}), 404

        category_id = category[0]
        cur.execute("INSERT INTO all_products(product, price, categorie_id) VALUES(%s, %s, %s)", 
                    (new_product['product'], new_product['price'], category_id))
        con.commit()
    except Error as e:
        print(e)
    finally:
        if con:
            cur.close()
            con.close()
    return jsonify({"message": "Product created successfully"}), 201

@app.route('/get/product/<string:category>', methods=['GET'])
def get_product_by_categorie(category):
    """  
    Get products by category  
    ---  
    parameters:  
      - name: category  
        in: path  
        type: string  
        required: true  
    responses:  
      200:  
        description: A list of products in the specified category  
        schema:  
          type: array  
          items:  
            type: object  
            properties:  
              product:  
                type: string  
              price:  
                type: integer  
      404:  
        description: Category not found  
    """
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        cur.execute("""SELECT product, price FROM all_products  
                    WHERE categorie_id = (SELECT id FROM categorie WHERE categorie = %s)""", (category,))
        products = cur.fetchall()
        product_list = [{"product": product[0], "price": product[1]} for product in products]
        return jsonify(product_list)
    except Error as e:
        print(e)
    finally:
        if con:
            cur.close()
            con.close()

@app.route('/update/product', methods=['PUT'])
def update_product():
    """  
    Update an existing product  
    ---  
    parameters:  
      - name: product  
        in: body  
        required: true  
        schema:  
          type: object  
          properties:  
            product:  
              type: string  
            categorie:  
              type: string  
            price:  
              type: integer  
    responses:  
      200:  
        description: Product updated successfully  
      404:  
        description: Product not found  
    """
    product_name = request.json['product']
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        cur.execute("SELECT * FROM all_products WHERE product=%s", (product_name,))
        product = cur.fetchone()

        if product:
            updated_categorie = request.json.get('categorie', product[2])
            updated_price = request.json.get('price', product[1])

            cur.execute("UPDATE all_products SET categorie_id=(SELECT id FROM categorie WHERE categorie=%s), price=%s WHERE product=%s",
                        (updated_categorie, updated_price, product_name))
            con.commit()
            return jsonify({"message": "Product updated"}), 200
        else:
            return jsonify({"message": "Product not found"}), 404
    except Error as e:
        print(e)
    finally:
        if con:
            cur.close()
            con.close()

@app.route('/product/delete', methods=['DELETE'])
def product_delete():
    """  
    Delete an existing product  
    ---  
    parameters:  
      - name: product  
        in: body  
        required: true  
        schema:  
          type: object  
          properties:  
            product:  
              type: string  

    responses:  
      200:  
        description: Product deleted successfully  
      404:  
        description: Product not found  
    """
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        product_name = request.json['product']
        cur.execute("SELECT id FROM all_products WHERE product=%s", (product_name,))
        product = cur.fetchone()

        if product is None:
            return jsonify({"message": "Product not found"}), 404

        cur.execute("DELETE FROM all_products WHERE product=%s", (product_name,))
        con.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Error as e:
        print(e)
        return jsonify({"message": "Something went wrong"}), 500
    finally:
        if con:
            cur.close()
            con.close()

@app.route('/category/delete', methods=['DELETE'])
def categorie_delete():
    """  
    Delete an existing category  
    ---  
    parameters:  
      - name: category 
        in: body  
        required: true  
        schema:  
          type: object  
          properties:  
            category:  
              type: string  

    responses:  
      200:  
        description: Category deleted successfully  
      404:  
        description: Category not found  
    """
    try:
        con = psycopg2.connect(DATABASE_URL)
        cur = con.cursor()
        categorie_name = request.json['categorie']
        cur.execute("SELECT id FROM categorie WHERE categorie=%s", (categorie_name,))
        category = cur.fetchone()

        if category is None:
            return jsonify({"message": "This category does not exist"}), 404

        cur.execute("DELETE FROM categorie WHERE categorie=%s", (categorie_name,))
        con.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Error as e:
        print(e)
        return jsonify({"message": "Something went wrong"}), 500
    finally:
        if con:
            cur.close()
            con.close()

if __name__ == "__main__":
    app.run()