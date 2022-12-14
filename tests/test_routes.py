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
BASE_URL = "/api/promotions"

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
        self.assertIn(b"Promotions Demo RESTful Service", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion create: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)
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

    def test_get_promotion(self):
        """It should retrieve a Promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_list_promotions(self):
        """It should retrieve a list containing all Promotions"""
        # get 5 promotions
        test_promotion = self._create_promotions(5)
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        promotions = response.get_json()
        for i, promotion in enumerate(promotions):
            self.assertEqual(promotion["name"], test_promotion[i].name)

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

    def test_query_promotion_list_by_status(self):
        """It should Query Promotions by Status"""
        promotions = self._create_promotions(10)
        available_promotions = [
            promotion for promotion in promotions if promotion.status is True]
        unavailable_promotions = [
            promotion for promotion in promotions if promotion.status is False]
        available_count = len(available_promotions)
        unavailable_count = len(unavailable_promotions)
        logging.debug(
            "Available Promotions [%d] %s", available_count, available_promotions)
        logging.debug(
            "Unavailable Promotions [%d] %s", unavailable_count, unavailable_promotions)

        # test for available
        response = self.client.get(
            BASE_URL, query_string="status=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["status"], True)

        # test for unavailable
        response = self.client.get(
            BASE_URL, query_string="status=false"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), unavailable_count)
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["status"], False)

    def test_delete_promotion(self):
        """It should Delete a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # make sure this is deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_promotion(self):
        """It should Activate a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.put(f"{BASE_URL}/{test_promotion.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        self.assertEqual(new_promotion["status"], True)

    def test_deactivate_promotion(self):
        """It should deactivate a Promotion"""
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(
            f"{BASE_URL}/{test_promotion.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        self.assertEqual(new_promotion["status"], False)

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
                         status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_no_content_type(self):
        """It should not Create a Promotion with no content type"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_update_promotion_no_id(self):
        """It should return a 404 Not Found Error if the id does not exist on update promotion"""
        # update the promotion with id that is not present in the database
        new_promotion = {'id': 4}
        logging.debug(new_promotion)
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}", json=new_promotion)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_deactivate_promotion_not_found(self):
        """It should return a 404 Not Found Error if the id does not exist on activate or deactivate promotion"""
        # update the promotion with id that is not present in the database
        new_promotion = {'id': 4}
        logging.debug(new_promotion)
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(
            f"{BASE_URL}/{new_promotion['id']}/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
