# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from lizard_fewsnorm.models import Locations
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


class TestIconStyle(TestCase):
    #fixtures = ('lizard_fewsjdbc_test', )

    def test_styles(self):
        """See if styles() output correspond to database contents.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png', color='ff00ff').save()

        expected = {
            '::::::':
            {'icon': 'icon.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)}}

        self.assertEqual(IconStyle._styles(), expected)

    def test_styles2(self):
        """See if styles_lookup() output correspond to database contents.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png', color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='ff00ff').save()

        expected = {
            '::::::':
            {'icon': 'icon.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)},
            '::filter1::::':
            {'icon': 'filter1.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)}}

        self.assertEqual(IconStyle._styles(), expected)

    def test_lookup(self):
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png',
                  color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='loc1',
                  fews_parameter='par1',
                  icon='loc1par1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='loc1',
                  fews_parameter='',
                  icon='loc1.png', mask='mask.png', color='00ffff').save()

        expected = {
            # Level0: jdbc_source_id
            None: {
                # Level1: fews_filter
                None: {
                    # Level2: fews_location
                    None: {
                        # Level3: fews_parameter
                        None: '::::::'
                       },
                    'loc1': {
                        # Level3: fews_parameter
                        None: '::::loc1::',
                        'par1': '::::loc1::par1'
                       }
                    },
                'filter1': {
                    # Level2: fews_location
                    None: {
                        # Level3: fews_parameter
                        None: '::filter1::::'
                       }
                    }
                }
            }

        self.assertEqual(IconStyle._lookup(), expected)

    def test_style(self):
        """See if style() output correspond to expected lookup.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='', fews_parameter='',
                  icon='icon.png', mask='mask.png', color='ff00ff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='par1', fews_parameter='',
                  icon='par1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='loc1',
                  fews_parameter='',
                  icon='loc1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='loc1',
                  fews_parameter='par1',
                  icon='par1.png', mask='mask.png', color='00ffff').save()
        IconStyle(jdbc_source=None,
                  fews_filter='', fews_location='loc1',
                  fews_parameter='par1',
                  icon='loc1par1.png', mask='mask.png', color='00ffff').save()

        jdbc_source = JdbcSource.objects.all()[0]

        expected1 = (
            '::::::',
            {'icon': 'icon.png', 'mask': ('mask.png', ),
             'color': (1.0, 0.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'locy', 'parz'),
            expected1)
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'locy', 'parz',
                            ignore_cache=True),
            expected1)

        expected2 = (
            '::filter1::::',
            {'icon': 'filter1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'l', 'p'),
            expected2)
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'l', 'p',
                            ignore_cache=True),
            expected2)

        expected3 = (
            '::filter1::loc1::',
            {'icon': 'loc1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'loc1', 'p'),
            expected3)

        expected4 = (
            '::filter1::loc1::par1',
            {'icon': 'par1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filter1', 'loc1', 'par1'),
            expected4)

        expected5 = (
            '::::loc1::par1',
            {'icon': 'loc1par1.png', 'mask': ('mask.png', ),
             'color': (0.0, 1.0, 1.0, 1.0)})
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'loc1', 'par1'),
            expected5)

    def test_empty(self):
        """Do not crash when no iconstyles are available, just return default.
        """

        expected = (
            '::::::',
            {'icon': 'meetpuntPeil.png', 'mask': ('meetpuntPeil_mask.png', ),
             'color': (0.0, 0.5, 1.0, 1.0)})

        jdbc_source = JdbcSource.objects.all()[0]
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'loc1', 'par1'),
            expected)

    def test_not_found(self):
        """Do not crash when corresponding iconstyle is notavailable,
        just return default.
        """
        IconStyle(jdbc_source=None,
                  fews_filter='filter1', fews_location='', fews_parameter='',
                  icon='filter1.png', mask='mask.png', color='00ffff').save()

        expected = (
            '::::::',
            {'icon': 'meetpuntPeil.png', 'mask': ('meetpuntPeil_mask.png', ),
             'color': (0.0, 0.5, 1.0, 1.0)})

        jdbc_source = JdbcSource.objects.all()[0]
        self.assertEqual(
            IconStyle.style(jdbc_source, 'filterx', 'loc1', 'par1'),
            expected)
