# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from lizard_fewsnorm.models import Locations
from lizard_fewsnorm.models import FewsNormSource


class AdapterTest(TestCase):

    def setUp(self):
        self.source_db = FewsNormSource(name='test fewsnorm', database_name='fewsnorm')
        self.source_db.using(self.source_db.database_name).save()

    def select_locations_test(self):
        locations = Locations.objects.using(self.source_db.database_name).all()
        self.assertNotEqual(len(locations), 0)




