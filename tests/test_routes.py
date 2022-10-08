"""
Promotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import Promotion, PromotionType, DataValidationError, db
from service.models import db
from service.common import status  # HTTP Status Codes
from tests.factories import PromotionFactory
from datetime import date

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/promotion"

######################################################################
#  P R O M O T I O N   R O U T E S   T E S T   C A S E S
######################################################################
class TestPromotionServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
    
    def _create_promotions(self, count):
        """Factory method to create pets in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            response = self.client.post(BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test pet"
            )
            new_pet = response.get_json()
            test_promotion.id = new_pet["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Promotions Service")

    def test_get_promotion(self):
        """It should Get a single Promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])
    
    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["type"], test_promotion.type.name)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["promotion_value"], test_promotion.promotion_value)
        self.assertEqual(new_promotion["promotion_percent"], test_promotion.promotion_percent)
        self.assertEqual(new_promotion["status"], test_promotion.status)
        self.assertEqual(date.fromisoformat(new_promotion["expiry"]), test_promotion.expiry)
        self.assertEqual(date.fromisoformat(new_promotion["created_at"]), test_promotion.created_at)
        self.assertEqual(date.fromisoformat(new_promotion["last_updated_at"]), test_promotion.last_updated_at)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["type"], test_promotion.type.name)
        self.assertEqual(new_promotion["description"], test_promotion.description)
        self.assertEqual(new_promotion["promotion_value"], test_promotion.promotion_value)
        self.assertEqual(new_promotion["promotion_percent"], test_promotion.promotion_percent)
        self.assertEqual(new_promotion["status"], test_promotion.status)
        self.assertEqual(date.fromisoformat(new_promotion["expiry"]), test_promotion.expiry)
        self.assertEqual(date.fromisoformat(new_promotion["created_at"]), test_promotion.created_at)
        self.assertEqual(
            date.fromisoformat(new_promotion["last_updated_at"]), test_promotion.last_updated_at
            )

    def test_create_promotion_with_incorrect_content_type(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, data=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


    def test_create_promotion_with_no_content_type(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
