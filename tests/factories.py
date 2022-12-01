"""
Test Factory to make fake objects for testing
"""
from datetime import date

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyInteger
from service.models import Promotion, PromotionType


class PromotionFactory(factory.Factory):
    """Creates fake promotions that you don't have to create"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    type = FuzzyChoice(choices=[PromotionType.ABS_DISCOUNT,
                                PromotionType.PERCENT_DISCOUNT])
    description = factory.Faker("first_name")
    promotion_value = FuzzyInteger(1, 2000)
    promotion_percent = FuzzyInteger(1, 75)
    status = FuzzyChoice(choices=[True, False])
    expiry = FuzzyDate(date(2008, 1, 1))
    created_at = FuzzyDate(date(2008, 1, 1))
    last_updated_at = FuzzyDate(date(2008, 1, 1))
