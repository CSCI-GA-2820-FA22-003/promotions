"""
Models for Promotion

All of the models are stored in this module

Models
------
Promotion - A Promotion used in the Shopping Cart
Attributes:
-----------
name (string) - the name of the promotion
type (enumeration) - the type of the promotion: ABS_DISCOUNT, PERCENT_DISCOUNT
description (string) - the description of the promotion
promotion_value (number) - the value of the promotion like 2000 off
promotion_percent: the percent of the promotion like 50% off
status (boolean) - True for active promotions
expiry (date) - Date when the promotion expires
created_at (date) - Date when the promotion was created
last_updated_at (date) - Date when the promotion was last updated

"""
import logging
from enum import Enum
from datetime import date, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Promotion.init_db(app)


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class DataValidationError(Exception):
    """Custom Exception with data validation fails"""


class PromotionType(Enum):
    """Enumeration of valid Promotion Types"""

    ABS_DISCOUNT = 0
    PERCENT_DISCOUNT = 1
    UNKNOWN = 2


class Promotion(db.Model):  # pylint: disable=too-many-instance-attributes
    """
    Class that represents a Promotion

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    type = db.Column(
        db.Enum(PromotionType),
        nullable=False,
        server_default=(PromotionType.ABS_DISCOUNT.name)
    )
    description = db.Column(db.String(63), nullable=False)
    promotion_value = db.Column(db.Integer)
    promotion_percent = db.Column(db.Float)
    status = db.Column(db.Boolean(), nullable=False, default=True)
    expiry = db.Column(db.Date(), nullable=False,
                       default=date.today() + timedelta(days=7))
    created_at = db.Column(db.Date(), nullable=False, default=date.today())
    last_updated_at = db.Column(
        db.Date(), nullable=False, default=date.today())

    # Instance Methods

    def __repr__(self):
        return f"<Promotion {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Promotion to the database
        """
        logger.info("Saving %s", self.name)
        self.last_updated_at = date.today()
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Promotion from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def activate(self):
        """ Activates a Promotion from the data store """
        logger.info("Activating %s", self.name)
        self.status = True
        db.session.commit()

    def deactivate(self):
        """ Deactivates a Promotion from the data store """
        logger.info("Deactivating %s", self.name)
        self.status = False
        db.session.commit()

    def serialize(self) -> dict:
        """ Serializes a Promotion into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.name,  # convert enum to string
            "description": self.description,
            "promotion_value": self.promotion_value,
            "promotion_percent": self.promotion_percent,
            "status": self.status,
            "expiry": self.expiry.isoformat()
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the promotion data
        """
        try:
            self.name = data["name"]
            # create enum from string
            self.type = getattr(PromotionType, data["type"])
            self.description = data["description"]
            self.promotion_value = data["promotion_value"]
            self.promotion_percent = data["promotion_percent"]
            if isinstance(data["status"], bool):
                self.status = data["status"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [status]: "
                    + str(type(data["status"]))
                )
            self.expiry = date.fromisoformat(data["expiry"])
        except AttributeError as error:
            raise DataValidationError(
                "Invalid attribute: " + error.args[0]
            ) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Promotion: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    # Class Methods

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Promotions in the database """
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Promotion by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_status(cls, status) -> list:
        """ Returns all Promotions by their status

        :param status: True for promotions that are active
        :type available: bool

        :return: a collection of Promotions that are active or inactive based on given status
        :rtype: list

        """
        logger.info("Processing status query for %s ...", status)
        return cls.query.filter(cls.status == status)
