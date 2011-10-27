# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from django.contrib.gis.geos import Point

from composite_pk import composite

from lizard_geo.models import GeoObject
from lizard_geo.models import GeoObjectGroup

from lizard_map.coordinates import rd_to_wgs84

import logging
logger = logging.getLogger(__name__)


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

    def __unicode__(self):
        return '%s' % self.id


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
    aggregationperiodkey = models.IntegerField(
        primary_key=True,
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


# Managed models that are in the default database.

class ParameterCache(models.Model):
    ident = models.CharField(max_length=64)

    def __unicode__(self):
        return '%s' % self.ident

    def api_url(self):
        return reverse('lizard_fewsnorm_api_parameter_detail',
                       kwargs={'ident': self.ident})


class ModuleCache(models.Model):
    ident = models.CharField(max_length=64)

    def __unicode__(self):
        return '%s' % self.ident

    # def api_url(self):
    #     return reverse('lizard_fewsnorm_api_module')


class GeoLocationCache(GeoObject):
    """
    Geo cache for locations from all data sources.
    """
    fews_norm_source = models.ForeignKey('FewsNormSource')
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=64)
    icon = models.CharField(max_length=64)
    tooltip = models.CharField(max_length=64)
    parameter = models.ManyToManyField(
        ParameterCache, null=True, blank=True)
    module = models.ManyToManyField(
        ModuleCache, null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return '%s %s ' % (self.fews_norm_source, self.ident)

    def api_url(self):
        return reverse('lizard_fewsnorm_api_location_detail',
                       kwargs={'ident': self.ident})


class FewsNormSource(models.Model):
    """
    Define a source database for fews norm.
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    database_name = models.CharField(max_length=40, unique=True)

    def _empty_cache(self):
        logger.debug('Empty GeoLocationCache for fewsnorm %s...', self.name)
        self.geolocationcache_set.all().delete()

    def source_locations(self):
        return Locations.objects.using(self.database_name).all()

    def get_or_create_geoobjectgroup(self, user_name):
        user_obj = User.objects.get(username=user_name)
        group_name = 'FEWSNORM::%s' % self.database_name
        group_slug = slugify(group_name)
        geo_object_group, created = GeoObjectGroup.objects.get_or_create(
            name=group_name, slug=group_slug, created_by=user_obj)
        if created:
            geo_object_group.source_log = 'FEWSNORM::%s' % self.database_name
            geo_object_group.save()
        return geo_object_group

    @transaction.commit_on_success
    def synchronize_parameter_cache(self):
        """
        Fill ParameterCache
        """
        parameters = {}
        for parameter in self.o(Parameters).all():
            print 'Get or create parameter cache %s' % parameter.id
            parameter_cache, _ = ParameterCache.objects.get_or_create(
                ident=parameter.id)
            parameters[parameter_cache.ident] = parameter_cache
        return parameters

    @transaction.commit_on_success
    def synchronize_module_cache(self):
        """
        Fill ModuleCache.
        """
        modules = {}
        for module in self.o(ModuleInstances).all():
            module_cache, _ = ModuleCache.objects.get_or_create(
                ident=module.id)
            modules[module_cache.ident] = module_cache
        return modules

    @transaction.commit_on_success
    def synchronize_location_cache(self, user_name, parameters, modules):
        """
        Fill GeoLocationCache.

        parameters and modules are dicts with ParameterCache and
        ModuleCache. Keys are their idents.
        """
        self._empty_cache()  # For GeoLocationCache
        source_locations = self.source_locations()
        geo_object_group = self.get_or_create_geoobjectgroup(user_name)
        for location in source_locations:
            logger.debug('processing location.id: %s' % location.id)
            wgs84_x, wgs84_y = rd_to_wgs84(location.x, location.y)
            geo_location_cache = GeoLocationCache(
                ident=location.id[:80],
                fews_norm_source=self,
                name='%s' % location.name,
                shortname='%s' % location.shortname,
                icon='%s' % location.icon,
                tooltip='%s' % location.tooltip,
                geo_object_group=geo_object_group,
                geometry=GEOSGeometry(Point(wgs84_x, wgs84_y), srid=4326))
            geo_location_cache.save()

            timeserieskeys = location.timeserieskeys_set.all()
            for single_timeserieskeys in timeserieskeys:
                geo_location_cache.parameter.add(
                    parameters[single_timeserieskeys.parameterkey.id])
                geo_location_cache.module.add(
                    modules[single_timeserieskeys.moduleinstancekey.id])
            if not timeserieskeys:
                logger.warning(
                    'No timeseries associated with location %s, '
                    'the location will not be visible in Lizard.' %
                    location.id)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.database_name)

    def o(self, model_object):
        """
        Return Model using database_name.

        Using the short name o because the function is supposed to be
        a shortcut.

        Example usage:

        >>> source = FewsNormSource.objects.all()[0]
        >>> source.o(ModuleInstances).all()
        """

        return model_object.objects.using(self.database_name)

    def api_url(self):
        return reverse(
            'lizard_fewsnorm_api_adapter',
            kwargs={'fews_norm_source_slug': self.slug})
