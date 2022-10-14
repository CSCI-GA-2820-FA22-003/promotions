"""
Promotion API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""

import os
import logging
from unittest import TestCase
from datetime import date

# from unittest.mock import MagicMock, patch
from service import app
from service.common import status
from service.models import db, init_db, Promotion
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"

######################################################################
#  P R O M O T I O N   R O U T E S   T E S T   C A S E S
######################################################################


class TestPromotionServer(TestCase):
    """ Promotion REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def _create_promotions(self, count):
        """Factory method to create promotions in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            response = self.client.post(
                BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
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

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion create: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["type"], test_promotion.type.name)
        self.assertEqual(
            new_promotion["description"], test_promotion.description)
        self.assertEqual(
            new_promotion["promotion_value"], test_promotion.promotion_value)
        self.assertEqual(
            new_promotion["promotion_percent"], test_promotion.promotion_percent)
        self.assertEqual(new_promotion["status"], test_promotion.status)
        self.assertEqual(date.fromisoformat(
            new_promotion["expiry"]), test_promotion.expiry)
        self.assertEqual(date.fromisoformat(
            new_promotion["created_at"]), test_promotion.created_at)
        self.assertEqual(date.fromisoformat(new_promotion["last_updated_at"]),
                         test_promotion.last_updated_at)

    def test_update_promotion(self):
        """It should Update an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        new_promotion["description"] = "Updated description"
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}", json=new_promotion)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_promotion = response.get_json()
        self.assertEqual(
            updated_promotion["description"], "Updated description")

    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # make sure this is deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_promotion_no_data(self):
        """It should not Create a Promotion with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_incorrect_content_type(self):
        """It should not Create a Promotion with incorrect content type"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, data=test_promotion.serialize())
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_promotion_with_no_content_type(self):
        """It should not Create a Promotion with no content type"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_promotion_no_id(self):
        """It should return a 404 Not Found Error if the id does not exist on update promotion"""
        # update the promotion with id that is not present in the database
        new_promotion = {'id': 4}
        logging.debug(new_promotion)
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}", json=new_promotion)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
