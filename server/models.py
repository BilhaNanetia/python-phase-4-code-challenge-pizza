from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata with custom foreign key naming convention
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy instance with the metadata
db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    """
    Model representing a Restaurant with its attributes
    """
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan")

    # Creates an association proxy for pizzas using restaurant_pizzas relationship
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # add serialization rules
    serialize_rules = ("-pizzas",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    """
    Model representing a Pizza with its attributes
    """
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan")

    # Create an association proxy for restaurants using restaurant_pizzas relationship
    restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # add serialization rules
    serialize_rules = ("-restaurants",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"
class RestaurantPizza(db.Model, SerializerMixin):
    """
    Model representing the association between a Restaurant and a Pizza with price information
    """
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))

    # add relationships
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")

    # Add serialization rules
    serialize_rules = ("-pizza.restaurant_pizzas", "-restaurant.restaurant_pizzas")

    #validations
    @validates("price")
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"