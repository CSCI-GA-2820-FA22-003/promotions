"""
Test cases for Promotion Model

Test cases for Promotion Model
Test cases can be run with:
    nosetests
    coverage report -m
"""
import os
import logging
import unittest
from datetime import date
from service.models import Promotion, PromotionType, DataValidationError, db
from service import app
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  P R O M O T I O N   M O D E L   T E S T   C A S E S
######################################################################


# pylint: disable=too-many-public-methods
class TestPromotion(unittest.TestCase):
    """ Test Cases for Promotion Model """

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
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion(self):
        """It should Create a promotion and assert that it exists"""
        promotion = Promotion(name="Sale", type=PromotionType.ABS_DISCOUNT,
                              description="Sale on Products", promotion_value=1000,
                              promotion_percent=0)
        self.assertEqual(str(promotion), "<Promotion Sale id=[None]>")
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.name, "Sale")
        self.assertEqual(promotion.type, PromotionType.ABS_DISCOUNT)
        self.assertEqual(promotion.description, "Sale on Products")
        self.assertEqual(promotion.promotion_value, 1000)
        self.assertEqual(promotion.promotion_percent, 0)
        promotion = Promotion(name="Sale", type=PromotionType.PERCENT_DISCOUNT,
                              description="Sale on Products", promotion_value=0,
                              promotion_percent=50, status=False)
        self.assertEqual(promotion.type, PromotionType.PERCENT_DISCOUNT)
        self.assertEqual(promotion.promotion_percent, 50)
        self.assertEqual(promotion.status, False)

    def test_add_a_promotion(self):
        """It should Create a promotion and add it to the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(name="Sale", type=PromotionType.ABS_DISCOUNT,
                              description="Sale on Products", promotion_value=1000,
                              promotion_percent=0, status=True)
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(promotion.id)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_read_a_promotion(self):
        """It should Read a Promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        self.assertIsNotNone(promotion.id)
        # Fetch it back
        found_promotion = Promotion.find(promotion.id)
        self.assertEqual(found_promotion.id, found_promotion.id)
        self.assertEqual(found_promotion.name, found_promotion.name)
        self.assertEqual(found_promotion.description,
                         found_promotion.description)

    def test_update_a_promotion(self):
        """It should Update a Promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        logging.debug(promotion)
        self.assertIsNotNone(promotion.id)
        # Change it an save it
        promotion.description = "A new promotion"
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.description, "A new promotion")
        # Fetch it back and make sure the id hasn't changed
        # But the data did change
        promotions = promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].id, original_id)
        self.assertEqual(promotions[0].description, "A new promotion")

    def test_update_no_id(self):
        """It should not Update a Promotion with no id"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        self.assertRaises(DataValidationError, promotion.update)

    def test_delete_a_promotion(self):
        """It should Delete a Promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertEqual(len(Promotion.all()), 1)
        # Delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_list_all_promotions(self):
        """It should List all Promotions in the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        # Create 5 Promotions
        for _ in range(5):
            promotion = PromotionFactory()
            promotion.create()
        # See if we get back 5 promotions
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 5)

    def test_serialize_a_promotion(self):
        """It should serialize a Promotion"""
        promotion = PromotionFactory()
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], promotion.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], promotion.name)
        self.assertIn("type", data)
        self.assertEqual(data["type"], promotion.type.name)
        self.assertIn("description", data)
        self.assertEqual(data["description"], promotion.description)
        self.assertIn("promotion_value", data)
        self.assertEqual(data["promotion_value"], promotion.promotion_value)
        self.assertIn("promotion_percent", data)
        self.assertEqual(data["promotion_percent"],
                         promotion.promotion_percent)
        self.assertIn("status", data)
        self.assertEqual(data["status"], promotion.status)
        self.assertIn("expiry", data)
        self.assertEqual(date.fromisoformat(data["expiry"]), promotion.expiry)

    def test_deserialize_a_promotion(self):
        """It should de-serialize a Promotion"""
        data = PromotionFactory().serialize()
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.name, data["name"])
        self.assertEqual(promotion.type.name, data["type"])
        self.assertEqual(promotion.description, data["description"])
        self.assertEqual(promotion.promotion_value, data["promotion_value"])
        self.assertEqual(promotion.promotion_percent,
                         data["promotion_percent"])
        self.assertEqual(promotion.status, data["status"])
        self.assertEqual(promotion.expiry, date.fromisoformat(data["expiry"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a Promotion with missing data"""
        data = {"id": 1, "name": "Promotion",
                "description": "A great Promotion"}
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_promotion = PromotionFactory()
        data = test_promotion.serialize()
        data["status"] = "true"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_type(self):
        """It should not deserialize a bad type attribute"""
        test_promotion = PromotionFactory()
        data = test_promotion.serialize()
        data["type"] = "random"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_find_promotion(self):
        """It should Find a Promotion by ID"""
        promotions = PromotionFactory.create_batch(5)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)
        # Make sure they got saved
        self.assertEqual(len(Promotion.all()), 5)
        # Find the 2nd promotion in the list
        promotion = Promotion.find(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.name, promotions[1].name)
        self.assertEqual(promotion.type, promotions[1].type)
        self.assertEqual(promotion.status, promotions[1].status)
        self.assertEqual(promotion.expiry, promotions[1].expiry)

    def test_find_by_status(self):
        """It should Find Promotions by Status"""
        promotions = PromotionFactory.create_batch(10)
        for promotion in promotions:
            promotion.create()
        status = promotions[0].status
        count = len([promotion for promotion in promotions if promotion.status == status])
        found = Promotion.find_by_status(status)
        self.assertEqual(found.count(), count)
        for promotion in found:
            self.assertEqual(promotion.status, status)
