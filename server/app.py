#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

# Configure base directory path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Set database URI from environment variable or default to local SQLite database
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask application
app = Flask(__name__)

# Configure Flask application settings
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize SQLAlchemy with the Flask application
db.init_app(app)

# Initialize Flask-RESTful API
api = Api(app)


@app.route("/")
def index():
    """
    Basic route for the root path.
    """
    return "<h1>Code challenge</h1>"

class RestaurantsResource(Resource):
    """
    API Resource for managing a collection of Restaurants.
    """
    def get(self):
        # Convert restaurants to dictionary format with specified keys
        response = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in Restaurant.query.all()]
        return make_response(jsonify(response), 200)
    
class RestaurantResource(Resource):
    """
    API Resource for managing a single Restaurant.
    """
    def get(self, id):
        """
        Get a restaurant by its ID.
        """
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            response = restaurant.to_dict()
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        """
        Delete a restaurant by its ID.
        """
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response(jsonify({"message": "Restaurant deleted"}), 204)
        else:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)
            
        return response

class PizzasResource(Resource):
    """
    API Resource for managing a collection of Pizzas.
    """
    def get(self):
        response = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in Pizza.query.all()]
        return make_response(jsonify(response), 200)

class RestaurantPizzasResource(Resource):
    """
    API Resource for managing associations between Restaurants and Pizzas.
    """
    def post(self):
        """
        Create a new association between a restaurant and a pizza.
        """
        data = request.get_json()

        try:
            restaurant_id = data['restaurant_id']
            pizza_id = data['pizza_id']
            price = data['price']

            if price < 1 or price > 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)

            
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            response = new_restaurant_pizza.to_dict()
            return make_response(jsonify(response), 201)

        # Handle errors
        except KeyError as e:
            return make_response(jsonify({"errors": [f"Missing key: {str(e)}"]}), 400)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        finally:
            db.session.close()

api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")



if __name__ == "__main__":
    app.run(port=5555, debug=True)
