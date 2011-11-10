# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import GeoObjectGroup
from django.contrib.auth.models import User


class AdapterTest(TestCase):

    def setUp(self):
        self.source_db = FewsNormSource(
            name='test fewsnorm', database_name='fewsnorm')
        self.source_db.save()
        self.user = User(username='buildout', password='buildout')
        self.user.save()

    # def synchronize_cache_test(self):
    #     """How to test without fewsnorm database?"""
    #     parameters = self.source_db.synchronize_parameter_cache()
    #     modules = self.source_db.synchronize_module_cache()
    #     self.source_db.synchronize_location_cache(
    #         self.user.username,
    #         parameters, modules)
    #     locations = self.source_db.source_locations()
    #     self.assertNotEqual(len(locations), 0)

    def get_or_create_geoobjectgroup(self):
        group = self.source_db.get_or_create_geoobjectgroup(self.user.username)
        self.assertEquals(isinstance(group, GeoObjectGroup), True)
