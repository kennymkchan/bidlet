from django.test import TestCase
from api.forms import SearchPropertyForm
from datetime import datetime, timedelta
from api.models import Property

from api.views import (
    getFilters,
)

# White box testing
class FiltersTest(TestCase):

    def setUp(self):
        today = datetime.today();
        next_day = datetime.today() + timedelta(days=10)
        newProp = Property.objects.create(title="Hello there. This room is awesome", description="This is a test",
                                          ownerID=12, address="100 Unicorn", country="Canada", city="Markham",
                                          postalCode="L38G74", suite=3, image="string.png",
                                          startPrice=321.34, autoWinPrice=800.32,
                                          curPrice=500.00, availStart=today, availEnd=next_day,
                                          rooms=3, status="active")

    # White box testing:
    # You look for: Statement Coverage, Branch Coverage, Condition Coverage,
    # Path Coverage

    # We will be testing every individual path that can be taken
    # This test aims to cover all paths, conditions and branches as much as possible
    def test_search_country(self):
        searchForm = SearchPropertyForm({
            'country': 'Canada'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["AND"][0]
        self.assertEqual(includeFilter, ('country__icontains', 'Canada'))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_avail_city(self):
        searchForm = SearchPropertyForm({
            'city': 'Markham'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["AND"][0]
        self.assertEqual(includeFilter, ('city__icontains', 'Markham'))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_not_city(self):
        searchForm = SearchPropertyForm({
            'city': 'Not City'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["AND"][0]
        self.assertEqual(includeFilter, ('city__icontains', 'Not City'))
        self.assertEqual(len(filters["listings"]), 0)

    def test_search_keyword(self):
        searchForm = SearchPropertyForm({
            'keyword': 'Hello'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["OR"][0]
        print(includeFilter)
        self.assertEqual(includeFilter, ('title__icontains', 'Hello'))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_and_or_no_result(self):
        searchForm = SearchPropertyForm({
            'keyword': 'No',
            'country': 'Canada'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeOrFilter = filters["search"]["OR"][0]
        includeAndFilter = filters["search"]["AND"][0]
        self.assertEqual(includeOrFilter, ('title__icontains', 'No'))
        self.assertEqual(includeAndFilter, ('country__icontains', 'Canada'))
        self.assertEqual(len(filters["listings"]), 0)

    def test_search_and_or_results(self):
        searchForm = SearchPropertyForm({
            'keyword': 'Hello',
            'city': 'Markham'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeOrFilter = filters["search"]["OR"][0]
        includeAndFilter = filters["search"]["AND"][0]
        self.assertEqual(includeOrFilter, ('title__icontains', 'Hello'))
        self.assertEqual(includeAndFilter, ('city__icontains', 'Markham'))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_multi_and(self):
        searchForm = SearchPropertyForm({
            'country': 'Canada',
            'city': 'Markham'
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        firstAndFilter = filters["search"]["AND"][0]
        secondAndFilter = filters["search"]["AND"][1]
        self.assertEqual(firstAndFilter, ('country__icontains', 'Canada'))
        self.assertEqual(secondAndFilter, ('city__icontains', 'Markham'))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_multi_or(self):
        searchForm = SearchPropertyForm({
            'keyword': 'This',
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        firstAndFilter = filters["search"]["OR"][0]
        secondAndFilter = filters["search"]["OR"][1]
        self.assertEqual(firstAndFilter, ('title__icontains', 'This'))
        self.assertEqual(secondAndFilter, ('description__icontains', 'This'))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_rooms(self):
        searchForm = SearchPropertyForm({
            'rooms': 5
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["AND"][0]
        self.assertEqual(includeFilter, ('rooms__exact', 5))
        self.assertEqual(len(filters["listings"]), 0)

    def test_search_price_under(self):
        searchForm = SearchPropertyForm({
            'priceUnder': 500
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["AND"][0]
        self.assertEqual(includeFilter, ('curPrice__lte', 500.00))
        self.assertEqual(len(filters["listings"]), 1)

    def test_search_price_over(self):
        searchForm = SearchPropertyForm({
            'priceOver': 10000
        })
        self.assertTrue(searchForm.is_valid())
        filters = getFilters(searchForm)

        includeFilter = filters["search"]["AND"][0]
        self.assertEqual(includeFilter, ('curPrice__gte', 10000.00))
        self.assertEqual(len(filters["listings"]), 0)
