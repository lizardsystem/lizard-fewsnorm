# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models

from lizard_geo.models import GeoObject


class FewsNormSource(models.Model):
    """
    Define a source database for fews norm.
    """
    name = models.CharField(max_length=128)
    database_name = models.CharField(max_length=40)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.database_name)


class GeoLocationCache(GeoObject):
    """
    Geo cache for locations from all data sources.
    """
    pass
