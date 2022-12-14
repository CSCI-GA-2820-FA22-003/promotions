"""
Promotion  Service

The promotions service is a representation of a special promotion
or sale that is running against a product or perhaps the entire store

Paths:
------
GET /api/promotions - Returns a list all of the Promotions
GET /api/promotions?status=true - Returns a list of Promotions with active status
GET /api/promotions/{id} - Returns the Promotion with a given id number
POST /api/promotions - Creates a new Promotion record in the database
PUT /api/promotions/{id} - Updates a Promotion record in the database
DELETE /api/promotions/{id} - Deletes a Promotion record in the database
PUT /api/promotions/activate/{id} - Activates a Promotion
DELETE /api/promotions/activate/{id} - Deactivates a Promotion
"""

from flask import jsonify, request
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Promotion, PromotionType
from service.common import status  # HTTP Status Codes
# Import Flask application
from . import app, api


######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# Define the model so that the docs reflect what can be sent
######################################################################


create_model = api.model('Promotion', {
    'name': fields.String(required=True,
                          description='The name of the Promotion'),
    'type': fields.String(enum=PromotionType._member_names_, description='The type of the Promotion'),  # pylint: disable=W0212
    'description': fields.String(required=True,
                                 description='The description of the Promotion'),
    'promotion_value': fields.Integer(required=True,
                                      description='The value of the discount Promotion'),
    'promotion_percent': fields.Float(required=True,
                                      description='The percentage of the Promotion'),
    'status': fields.Boolean(required=True,
                             description='Is the Promotion active or not'),
    'expiry': fields.Date(required=True, description='The expiry date of the Promotion')
})

promotion_model = api.inherit(
    'PromotionModel',
    create_model,
    {
        'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)

# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument(
    'status', type=inputs.boolean, required=False, help='List Promotions by status')


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route('/promotions/<promotion_id>')
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class
    Allows the manipulation of a single Promotion
    GET /promotion{id} - Returns a Promotion with the id
    PUT /promotion{id} - Update a Promotion with the id
    DELETE /promotion{id} -  Deletes a Promotion with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('get_promotions')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion
        This endpoint will return a Promotion based on its id
        """
        app.logger.info("Request for promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Promotion with id '{promotion_id}' was not found.")
        app.logger.info("Returning promotion: %s", promotion.name)
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc('update_promotions')
    @api.response(400, 'The posted Promotion data was not valid')
    @api.response(404, 'Promotion not found')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    def put(self, promotion_id):
        """
        Update a Promotion
        This endpoint will update a Promotion based on the body that is posted
        """
        app.logger.info(
            "Request to update promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Promotion with id '{promotion_id}' was not found.")
        app.logger.debug('Payload = %s', api.payload)
        promotion.deserialize(request.get_json())
        promotion.id = promotion_id
        promotion.update()
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('delete_promotions')
    @api.response(204, 'Promotion deleted')
    def delete(self, promotion_id):
        """
        Delete a Promotion
        This endpoint will delete a Promotion based the id specified in the path
        """
        app.logger.info(
            "Request to delete a promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if promotion:
            promotion.delete()
            app.logger.info(
                "Promotion with ID [%s] delete complete.", promotion_id)
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotions """

    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc('list_promotions')
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns a list of all of the Promotions"""
        app.logger.info("Request for promotion list")
        promotions = []
        status_type = request.args.get("status")
        if status_type:
            app.logger.info('Filtering by status: %s', status_type)
            promotions = Promotion.find_by_status(status_type)
        else:
            app.logger.info('Returning unfiltered list.')
            promotions = Promotion.all()

        results = [promotion.serialize() for promotion in promotions]
        app.logger.info('[%s] Promotions returned', len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc('create_promotions')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    def post(self):
        """
        Creates a Promotion
        This endpoint will create a Promotion based on the data
        in the body that is posted
        """
        app.logger.info("Request to create a Promotion")
        promotion = Promotion()
        app.logger.debug('Payload = %s', api.payload)
        promotion.deserialize(api.payload)
        promotion.create()
        app.logger.info('Promotion with new id [%s] created!', promotion.id)
        location_url = api.url_for(
            PromotionResource, promotion_id=promotion.id, _external=True)
        return promotion.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
#  PATH: /promotions/{id}/activate
######################################################################
@api.route('/promotions/<promotion_id>/activate')
@api.param('promotion_id', 'The Promotion identifier')
class ActivateResource(Resource):
    """ Activate actions on Promotions """

    # ------------------------------------------------------------------
    # ACTIVATE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('activate_promotion')
    @api.response(404, 'Promotion not found')
    def put(self, promotion_id):
        """
        Activates a Promotion
        This endpoint will Activate a Promotion based on the id specified in the path
        """
        app.logger.info(
            "Request to Activate a promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Promotion with id '{promotion_id}' was not found.")
        promotion.activate()
        app.logger.info(
            "Promotion with ID [%s] activation complete.", promotion_id)
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DEACTIVATE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('deactivate_promotion')
    @api.response(404, 'Promotion not found')
    def delete(self, promotion_id):
        """
        Deactivates a Promotion
        This endpoint will Deactivate a Promotion based on the id specified in the path
        """
        app.logger.info(
            "Request to Deactivate a promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Promotion with id '{promotion_id}' was not found.")
        promotion.deactivate()
        app.logger.info(
            "Promotion with ID [%s] deactivation complete.", promotion_id)
        return promotion.serialize(), status.HTTP_200_OK

######################################################################
#  UTILITY FUNCTIONS
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
