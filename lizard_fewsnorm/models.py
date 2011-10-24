# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from composite_pk import composite

from lizard_geo.models import GeoObject
from lizard_geo.models import GeoObjectGroup


class Users(models.Model):
    userkey = models.IntegerField(primary_key=True,
                                  db_column='userkey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64, blank=True, null=True)
    class Meta:
        db_table = u'users'
        managed = False


# class GeometryColumns(models.Model):
#     f_table_catalog = models.CharField(max_length=256)
#     f_table_schema = models.CharField(max_length=256)
#     f_table_name = models.CharField(max_length=256)
#     f_geometry_column = models.CharField(max_length=256)
#     coord_dimension = models.IntegerField()
#     srid = models.IntegerField()
#     type = models.CharField(max_length=30)
#     class Meta:
#         db_table = u'geometry_columns'
#         managed = False


# class GeographyColumns(models.Model):
#     f_table_catalog = models.TextField() # This field type is a guess.
#     f_table_schema = models.TextField() # This field type is a guess.
#     f_table_name = models.TextField() # This field type is a guess.
#     f_geography_column = models.TextField() # This field type is a guess.
#     coord_dimension = models.IntegerField()
#     srid = models.IntegerField()
#     type = models.TextField()
#     class Meta:
#         db_table = u'geography_columns'
#         managed = False


# class SpatialRefSys(models.Model):
#     srid = models.IntegerField(primary_key=True,
#                                db_column='srid')
#     auth_name = models.CharField(max_length=256)
#     auth_srid = models.IntegerField()
#     srtext = models.CharField(max_length=2048)
#     proj4text = models.CharField(max_length=2048)
#     class Meta:
#         db_table = u'spatial_ref_sys'
#         managed = False


class ParameterGroups(models.Model):
    groupkey = models.IntegerField(primary_key=True,
                                   db_column='groupkey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    parametertype = models.CharField(max_length=64)
    unit = models.CharField(max_length=64)
    displayunit = models.CharField(max_length=64)
    class Meta:
        db_table = u'parametergroups'
        managed = False


class Locations(models.Model):
    locationkey = models.IntegerField(primary_key=True,
                                      db_column='locationkey')
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
    parameterkey = models.IntegerField(primary_key=True,
                                       db_column='parameterkey')
    groupkey = models.ForeignKey(ParameterGroups,
                                 db_column='groupkey')
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


class Qualifiers(models.Model):
    qualifierkey = models.IntegerField(primary_key=True,
                                       db_column='qualifierkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'qualifiers'
        managed = False


class QualifierSets(models.Model):
    qualifiersetkey = models.IntegerField(primary_key=True,
                                          db_column='qualifiersetkey')
    id = models.CharField(unique=True, max_length=64)
    qualifierkey1 = models.ForeignKey(Qualifiers,
                                      db_column='qualifierkey1',
                                      related_name='qualifierkey1')
    qualifierkey2 = models.ForeignKey(Qualifiers,
                                      db_column='qualifierkey2',
                                      related_name='qualifierkey2',
                                      blank=True, null=True)
    qualifierkey3 = models.ForeignKey(Qualifiers,
                                      db_column='qualifierkey3',
                                      related_name='qualifierkey3',
                                      blank=True, null=True)
    qualifierkey4 = models.ForeignKey(Qualifiers,
                                      related_name='qualifierkey4',
                                      db_column='qualifierkey4',
                                      blank=True, null=True)
    class Meta:
        db_table = u'qualifiersets'
        managed = False


class ModuleInstances(models.Model):
    moduleinstancekey = models.IntegerField(primary_key=True,
                                            db_column='moduleinstancekey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'moduleinstances'
        managed = False


class Timesteps(models.Model):
    timestepkey = models.IntegerField(primary_key=True,
                                      db_column='timestepkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'timesteps'
        managed = False


class AggregationPeriods(models.Model):
    aggregationperiodkey = models.IntegerField(primary_key=True,
                                               db_column='aggregationperiodkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)
    class Meta:
        db_table = u'aggregationperiods'
        managed = False


class TimeseriesKeys(models.Model):
    serieskey = models.IntegerField(primary_key=True,
                                    db_column='serieskey')
    locationkey = models.ForeignKey(Locations,
                                    db_column='locationkey')
    parameterkey = models.ForeignKey(Parameters,
                                     db_column='parameterkey')
    qualifiersetkey = models.ForeignKey(QualifierSets,
                                        db_column='qualifiersetkey',
                                        blank=True, null=True)
    moduleinstancekey = models.ForeignKey(ModuleInstances,
                                          db_column='moduleinstancekey',
                                          blank=True, null=True)
    timestepkey = models.ForeignKey(Timesteps,
                                    db_column='timestepkey',
                                    blank=True, null=True)
    aggregationperiodkey = models.ForeignKey(AggregationPeriods,
                                             db_column='aggregationperiodkey',
                                             blank=True, null=True)
    class Meta:
        db_table = u'timeserieskeys'
        managed = False


class TimeseriesValuesAndFlags(composite.CompositePKModel):
    serieskey = models.ForeignKey(TimeseriesKeys,
                                  primary_key=True,
                                  db_column='serieskey')
    datetime = models.DateTimeField(primary_key=True)
    scalarvalue = models.FloatField()
    flags = models.IntegerField()
    class Meta:
        db_table = u'timeseriesvaluesandflags'
        managed = False


class TimeseriesComments(models.Model):
    serieskey = models.ForeignKey(TimeseriesKeys,
                                  primary_key=True,
                                  db_column='serieskey',
                                  blank=True, null=True)
    datetime = models.DateTimeField(primary_key=True)
    comments = models.CharField(max_length=64)
    class Meta:
        db_table = u'timeseriescomments'
        managed = False


class TimeseriesManualEditsHistory(models.Model):
    serieskey = models.ForeignKey(TimeseriesKeys,
                                  primary_key=True,
                                  db_column='serieskey')
    editdatetime = models.DateTimeField(primary_key=True)
    datetime = models.DateTimeField()
    userkey = models.ForeignKey(Users, db_column='userkey',
                                blank=True, null=True)
    scalarvalue = models.FloatField()
    flags = models.IntegerField()
    comments = models.CharField(max_length=64)
    class Meta:
        db_table = u'timeseriesmanualeditshistory'
        managed = False


class FewsNormSource(models.Model):
    """
    Define a source database for fews norm.
    """
    name = models.CharField(max_length=128)
    database_name = models.CharField(max_length=40)

    def empty_cache(self):
        GeoLocationCache(fews_norm_source=self.source).delete()

    def source_locations(self):
        return Location.objects.using(self.source).all()

    def get_or_create_geoobjectgroup(self, user_name):

        geo_object_group, created = GeoObjectGroup.objects.get_or_create(
            name=self.name, created_by__username=user_name)
        if created:
            geo_object_group.name = 'FEWSNORM::%s' % self.source
            geo_object_group.slug = slugify(geo_object_group.name)
            geo_object_group.source_log = 'FEWSNORM::%s' % self.source
            geo_object_group.save()
        return geo_object_group

    @transaction.commit_on_success
    def syncronize_cache(self):
        self.empty_cache(self.source)
        source_locations = self.source_locations(self.source)
        for location in source_locations:
            obj = GeoLocationCache()
            obj.ident = location.id
            obj.name = location.name
            obj.shortname = location.shortname
            obj.geo_object_group = self.get_or_create_geoobjectgroep(source)
            obj.geometry = None


    def __unicode__(self):
        return '%s (%s)' % (self.name, self.database_name)


class GeoLocationCache(GeoObject):
    """
    Geo cache for locations from all data sources.
    """
    fews_norm_source = models.ForeignKey(FewsNormSource)
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name
