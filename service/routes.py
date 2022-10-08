"""
Promotion Service


The promotions service is a representation of a special promotion
or sale that is running against a product or perhaps the entire store.
"""

from flask import jsonify, request, abort, url_for
from service.models import Promotion
from .common import status  # HTTP Status Codes
# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Promotions Root URL response"""
    app.logger.info("Request for Promotions Root URL")
    return (
        jsonify(
            name="Promotions Service",
            version="1.0"
        ),
        status.HTTP_200_OK,
    )


######################################################################
# RETRIEVE A PROMOTION
######################################################################
@app.route("/promotion/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
    """
    Retrieve a single Promotion
    This endpoint will return a Promotion based on it's id
    """
    app.logger.info("Request for promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(status.HTTP_404_NOT_FOUND, f"Promotion with id '{promotion_id}' was not found.")

    app.logger.info("Returning promotion: %s", promotion.name)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW PROMOTION
######################################################################
@app.route("/promotion", methods=["POST"])
def create_promotion():
    """
    Creates a Promotion
    This endpoint will create a Promotion based the data in the body that is posted
    """
    app.logger.info("Request to create a Promotion")
    check_content_type("application/json")
    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.create()
    message = promotion.serialize()
    location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)

    app.logger.info("Promotion with ID [%s] created.", promotion.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}



######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Promotion.init_db(app)

def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
