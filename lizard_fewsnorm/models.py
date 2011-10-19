# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.contrib.gis.db import models
from django.db import models

from lizard_geo.models import GeoObject

class GeometryColumns(models.Model):
    f_table_catalog = models.CharField(max_length=256)
    f_table_schema = models.CharField(max_length=256)
    f_table_name = models.CharField(max_length=256)
    f_geometry_column = models.CharField(max_length=256)
    coord_dimension = models.IntegerField()
    srid = models.IntegerField()
    type = models.CharField(max_length=30)
    class Meta:
        db_table = u'geometry_columns'
        managed = False

class GeographyColumns(models.Model):
    f_table_catalog = models.TextField() # This field type is a guess.
    f_table_schema = models.TextField() # This field type is a guess.
    f_table_name = models.TextField() # This field type is a guess.
    f_geography_column = models.TextField() # This field type is a guess.
    coord_dimension = models.IntegerField()
    srid = models.IntegerField()
    type = models.TextField()
    class Meta:
        db_table = u'geography_columns'
        managed = False

class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256)
    auth_srid = models.IntegerField()
    srtext = models.CharField(max_length=2048)
    proj4text = models.CharField(max_length=2048)
    class Meta:
        db_table = u'spatial_ref_sys'
        managed = False

class Parametergroups(models.Model):
    groupkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    parametertype = models.CharField(max_length=64)
    unit = models.CharField(max_length=64)
    displayunit = models.CharField(max_length=64)
    class Meta:
        db_table = u'parametergroups'
        managed = False

class Qualifiers(models.Model):
    qualifierkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'qualifiers'
        managed = False

class Locations(models.Model):
    locationkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    icon = models.CharField(max_length=64)
    tooltip = models.CharField(max_length=64)
    parentlocationid = models.CharField(max_length=64)
    visibilitystarttime = models.DateTimeField()
    visibilityendtime = models.DateTimeField()
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    area = models.FloatField()
    relationalocationid = models.CharField(max_length=64)
    relationblocationid = models.CharField(max_length=64)
    attributea = models.CharField(max_length=64)
    attributeb = models.FloatField()
    class Meta:
        db_table = u'locations'
        managed = False

class Parameters(models.Model):
    parameterkey = models.IntegerField(primary_key=True)
    groupkey = models.ForeignKey(Parametergroups, db_column='groupkey')
    id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    valueresolution = models.FloatField()
    attributea = models.CharField(max_length=64)
    attributeb = models.FloatField()
    class Meta:
        db_table = u'parameters'
        managed = False

class Qualifiersets(models.Model):
    qualifiersetkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    qualifierkey1 = models.ForeignKey(Qualifiers, db_column='qualifierkey1')
    qualifierkey2 = models.ForeignKey(Qualifiers, db_column='qualifierkey2')
    qualifierkey3 = models.ForeignKey(Qualifiers, db_column='qualifierkey3')
    qualifierkey4 = models.ForeignKey(Qualifiers, db_column='qualifierkey4')
    class Meta:
        db_table = u'qualifiersets'
        managed = False

class Moduleinstances(models.Model):
    moduleinstancekey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'moduleinstances'
        managed = False

class Timesteps(models.Model):
    timestepkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'timesteps'
        managed = False

class Aggregationperiods(models.Model):
    aggregationperiodkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'aggregationperiods'
        managed = False

class Timeseriesvaluesandflags(models.Model):
    serieskey = models.ForeignKey(Timeserieskeys, db_column='serieskey')
    datetime = models.DateTimeField()
    scalarvalue = models.FloatField()
    flags = models.IntegerField()
    class Meta:
        db_table = u'timeseriesvaluesandflags'
        managed = False

class Timeseriescomments(models.Model):
    serieskey = models.ForeignKey(Timeserieskeys, db_column='serieskey')
    datetime = models.DateTimeField()
    comments = models.CharField(max_length=64)
    class Meta:
        db_table = u'timeseriescomments'
        managed = False

class Timeserieskeys(models.Model):
    serieskey = models.IntegerField(primary_key=True)
    locationkey = models.ForeignKey(Locations, db_column='locationkey')
    parameterkey = models.ForeignKey(Parameters, db_column='parameterkey')
    qualifiersetkey = models.ForeignKey(Qualifiersets, db_column='qualifiersetkey')
    moduleinstancekey = models.ForeignKey(Moduleinstances, db_column='moduleinstancekey')
    timestepkey = models.ForeignKey(Timesteps, db_column='timestepkey')
    aggregationperiodkey = models.ForeignKey(Aggregationperiods, db_column='aggregationperiodkey')
    class Meta:
        db_table = u'timeserieskeys'
        managed = False

class Timeseriesmanualeditshistory(models.Model):
    serieskey = models.ForeignKey(Timeserieskeys, db_column='serieskey')
    editdatetime = models.DateTimeField()
    datetime = models.DateTimeField()
    userkey = models.ForeignKey(Users, db_column='userkey')
    scalarvalue = models.FloatField()
    flags = models.IntegerField()
    comments = models.CharField(max_length=64)
    class Meta:
        db_table = u'timeseriesmanualeditshistory'
        managed = False

class Users(models.Model):
    userkey = models.IntegerField(primary_key=True)
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    class Meta:
        db_table = u'users'
        managed = False


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
