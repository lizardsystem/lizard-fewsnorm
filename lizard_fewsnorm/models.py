# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import datetime

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from django.contrib.gis.geos import Point
from django.conf import settings

from composite_pk import composite

from lizard_geo.models import GeoObject
from lizard_geo.models import GeoObjectGroup

from lizard_map.coordinates import rd_to_wgs84

from timeseries import timeseries


import logging
logger = logging.getLogger(__name__)


# Note: all fewsnorm dbs are assumed to have this schema.
SCHEMA_PREFIX = 'nskv00_opdb\".\"'


class Users(models.Model):
    userkey = models.IntegerField(primary_key=True,
                                  db_column='userkey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = SCHEMA_PREFIX + u'users'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


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
        db_table = SCHEMA_PREFIX + u'parametergroups'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class Location(models.Model):
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
        db_table = SCHEMA_PREFIX + u'locations'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class Parameter(models.Model):
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
        db_table = SCHEMA_PREFIX + u'parameters'
        managed = False

    def __unicode__(self):
        return '%s' % self.id


class Qualifiers(models.Model):
    qualifierkey = models.IntegerField(primary_key=True,
                                       db_column='qualifierkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        db_table = SCHEMA_PREFIX + u'qualifiers'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


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
        db_table = SCHEMA_PREFIX + u'qualifiersets'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class ModuleInstances(models.Model):
    moduleinstancekey = models.IntegerField(primary_key=True,
                                            db_column='moduleinstancekey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        db_table = SCHEMA_PREFIX + u'moduleinstances'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class Timesteps(models.Model):
    timestepkey = models.IntegerField(primary_key=True,
                                      db_column='timestepkey')
    id = models.CharField(unique=True, max_length=64)
    #description = models.CharField(max_length=64)  # on testdatabase
    #label = models.CharField(max_length=64)  # on fewsnorm-dev

    class Meta:
        db_table = SCHEMA_PREFIX + u'timesteps'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class AggregationPeriods(models.Model):
    aggregationperiodkey = models.IntegerField(
        primary_key=True,
        db_column='aggregationperiodkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        db_table = SCHEMA_PREFIX + u'aggregationperiods'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class Series(models.Model):
    serieskey = models.IntegerField(primary_key=True,
                                    db_column='serieskey')
    location = models.ForeignKey(Location,
                                 db_column='locationkey')
    parameter = models.ForeignKey(Parameter,
                                  db_column='parameterkey')
    qualifierset = models.ForeignKey(QualifierSets,
                                        db_column='qualifiersetkey',
                                        blank=True, null=True)
    moduleinstance = models.ForeignKey(ModuleInstances,
                                       db_column='moduleinstancekey',
                                       blank=True, null=True)
    timestep = models.ForeignKey(Timesteps,
                                 db_column='timestepkey',
                                 blank=True, null=True)
    aggregationperiod = models.ForeignKey(AggregationPeriods,
                                          db_column='aggregationperiodkey',
                                          blank=True, null=True)

    class Meta:
        db_table = SCHEMA_PREFIX + u'timeserieskeys'
        managed = False

    def __unicode__(self):
        return u'%s %s %s %s' % (
            self.location,
            self.parameter,
            self.qualifierset,
            self.moduleinstance)

#     @classmethod
#     def from_lppairs(cls, lppairs):
#         """select series matching zipped location parameter iterable.
#         """

#         location = None
#         for (l, p) in lppairs:
#             try:
#                 location = GeoLocationCache.objects.get(ident=l)
#                 break
#             except:
#                 pass
#         if location is None:
#             return None

#         db_name = location.fews_norm_source.database_name

#         locations = Location.objects.using(db_name).filter(
#             id__in=[l for (l, p) in lppairs])
#         parameters = Parameter.objects.using(db_name).filter(
#             id__in=[p for (l, p) in lppairs])

#         l_id_to_pk = dict((l.id, l.pk) for l in locations)
#         p_id_to_pk = dict((p.id, p.pk) for p in parameters)

#         keys = tuple((l_id_to_pk[l], p_id_to_pk[p]) for (l, p) in lppairs)

#         return cls.objects.raw("\
# SELECT * FROM \"timeserieskeys\" \
# WHERE (locationkey, parameterkey) IN %s" % (keys,)).using(db_name)


class Event(composite.CompositePKModel):
    """
    A single event.

    Use the model Series to find out more.
    """
    series = models.ForeignKey(Series,
                               primary_key=True,
                               db_column='serieskey')
    timestamp = models.DateTimeField(primary_key=True, db_column='datetime')
    value = models.FloatField(db_column='scalarvalue')
    flag = models.IntegerField(db_column='flags')
    comment = None  # not yet there

    class Meta:
        db_table = SCHEMA_PREFIX + u'timeseriesvaluesandflags'
        managed = False

    def __unicode__(self):
        return u'%s %s value=%s %s' % (
            self.series,
            self.timestamp,
            self.value,
            self.flag)

    @classmethod
    def filter_latest_before_deadline(cls, series_set, deadline):
        """filter events matching series_set

        `series_set` is a QuerySet holding Series.

        `deadline` is a time threshold: we only consider the events
        before `deadline` and per Series we return the latest one.
        """

        ## get the concrete database from one of the locations in the
        ## series set.

        # assume the serie_set is not empty!
        first_serie = series_set[0]
        location = GeoLocationCache.objects.get(ident=first_serie.location.id)
        db_name = location.fews_norm_source.database_name

        series_set__pk = ','.join(tuple(str(s.pk) for s in series_set))
        deadline__iso = deadline.isoformat()

        ## execute the query.
        return cls.objects.raw("""\
SELECT e.* FROM \"%(schema_prefix)stimeseriesvaluesandflags\" e
  JOIN (SELECT serieskey, max(datetime) AS datetime
        FROM \"%(schema_prefix)stimeseriesvaluesandflags\"
        WHERE serieskey in (%(serieskey)s)
          AND datetime < '%(deadline)s'
              GROUP BY serieskey) latest
  ON e.serieskey = latest.serieskey
  AND e.datetime = latest.datetime""" % {
                'schema_prefix': SCHEMA_PREFIX,
                'serieskey': series_set__pk,
                'deadline': deadline__iso}).using(db_name)


class TimeseriesComments(models.Model):
    serieskey = models.ForeignKey(Series,
                                  primary_key=True,
                                  db_column='serieskey',
                                  blank=True, null=True)
    datetime = models.DateTimeField(primary_key=True)
    comments = models.CharField(max_length=64)

    class Meta:
        db_table = SCHEMA_PREFIX + u'timeseriescomments'
        managed = False

    def __unicode__(self):
        return u'%s' % self.comments


class TimeseriesManualEditsHistory(models.Model):
    serieskey = models.ForeignKey(Series,
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
        db_table = SCHEMA_PREFIX + u'timeseriesmanualeditshistory'
        managed = False

    def __unicode__(self):
        return u'%s %s' % (self.serieskey, self.datetime)


# Managed models that are in the default database.

class ParameterCache(models.Model):
    ident = models.CharField(max_length=64)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return '%s' % self.ident

    def api_url(self):
        return reverse('lizard_fewsnorm_api_parameter_detail',
                       kwargs={'ident': self.ident})


class ModuleCache(models.Model):
    ident = models.CharField(max_length=64)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return u'%s' % self.ident

    # def api_url(self):
    #     return reverse('lizard_fewsnorm_api_module')


class TimeStepCache(models.Model):
    ident = models.CharField(max_length=64)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return u'%s' % self.ident


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
        ParameterCache, null=True, blank=True, through='TimeSeriesCache')
    module = models.ManyToManyField(
        ModuleCache, null=True, blank=True, through='TimeSeriesCache')
    timestep = models.ManyToManyField(
        TimeStepCache, null=True, blank=True, through='TimeSeriesCache')
    objects = models.GeoManager()

    class Meta:
        ordering = ('ident', 'name')

    def __unicode__(self):
        try:
            return '%s (%s)' % (self.ident, self.fews_norm_source)
        except:
            # You can use GeoLocationCache as a memory object without
            # defining fews_norm_source.
            return '%s' % self.ident

    def api_url(self):
        return reverse('lizard_fewsnorm_api_location_detail',
                       kwargs={'ident': self.ident})


class TimeSeriesCache(models.Model):
    """
    Cache time series objects from all sources.

    Use this object as an entrypoint to fetch data.
    """
    geolocationcache = models.ForeignKey(GeoLocationCache)
    parametercache = models.ForeignKey(ParameterCache)
    modulecache = models.ForeignKey(ModuleCache)
    timestepcache = models.ForeignKey(TimeStepCache)

    def __unicode__(self):
        return '%s,%s,%s' % (
            self.geolocationcache.ident,
            self.parametercache.ident,
            self.id)

    def api_url(self):
        return reverse('lizard_fewsnorm_api_timeseries_detail',
                       kwargs={'id': self.id})

    def _series_set(self):
        """
        Return django QuerySet of Series.
        """
        db_name = self.geolocationcache.fews_norm_source.database_name
        series_query = (
            "SELECT * from \"%(schema_prefix)stimeserieskeys\" as ts, "
            "\"%(schema_prefix)sparameters\" as p, "
            "\"%(schema_prefix)slocations\" as l, "
            "\"%(schema_prefix)smoduleinstances\" as m "
            "WHERE "
            "ts.parameterkey = p.parameterkey and "
            "ts.locationkey = l.locationkey and "
            "ts.moduleinstancekey = m.moduleinstancekey and "
            "(l.id, p.id, m.id) IN "
            "(('%(loc_id)s', '%(par_id)s', '%(mod_id)s'))" % (
                {'schema_prefix':SCHEMA_PREFIX,
                 'loc_id': str(self.geolocationcache.ident),
                 'par_id': str(self.parametercache.ident),
                 'mod_id': str(self.modulecache.ident) }))
        return Series.objects.raw(series_query).using(db_name)

    def get_latest_event(self, now=None):
        """
        Return latest event for this timeseries.
        """
        if now is None:
            now = datetime.datetime.now()
        series_set = self._series_set()
        return Event.filter_latest_before_deadline(series_set, now)[0]

    def get_timeseries(self, dt_start, dt_end):
        """
        Return TimeSeries dictionary.

        Key is (location, parameter), Value is TimeSeries object.
        """
        series_set = self._series_set()
        return timeseries.TimeSeries.as_dict(series_set, dt_start, dt_end)


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
        return Location.objects.using(self.database_name).all()

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
        for parameter in Parameter.objects.using(self.database_name).all():
            logger.debug('Get or create parameter cache %s', parameter.id)
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
        for module in ModuleInstances.objects.using(self.database_name).all():
            module_cache, _ = ModuleCache.objects.get_or_create(
                ident=module.id)
            modules[module_cache.ident] = module_cache
        return modules

    @transaction.commit_on_success
    def synchronize_time_step_cache(self):
        """
        Fill TimeStepCache.
        """
        time_steps = {}
        for time_step in Timesteps.objects.using(self.database_name).all():
            time_step_cache, _ = TimeStepCache.objects.get_or_create(
                ident=time_step.id)
            time_steps[time_step_cache.ident] = time_step_cache
        return time_steps

    @transaction.commit_on_success
    def synchronize_location_cache(
        self, user_name):
        """
        Fill GeoLocationCache.

        parameters and modules are dicts with ParameterCache and
        ModuleCache. Keys are their idents.
        """
        self._empty_cache()  # For GeoLocationCache
        source_locations = self.source_locations()
        geo_object_group = self.get_or_create_geoobjectgroup(user_name)
        locations = {}
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
            locations[geo_location_cache.ident] = geo_location_cache
        return locations

    def synchronize_time_series_cache(
        self, locations, parameters, modules, time_steps):

        timeserieskeys = Series.objects.using(self.database_name).all()
        for single_timeserieskeys in timeserieskeys:
            logger.debug('processing timeseries: %s %s %s %s' % (
                    single_timeserieskeys.location.id,
                    single_timeserieskeys.parameter.id,
                    single_timeserieskeys.moduleinstance.id,
                    single_timeserieskeys.timestep.id))
            time_series_cache = TimeSeriesCache(
                geolocationcache=locations[
                    single_timeserieskeys.location.id],
                parametercache=parameters[
                    single_timeserieskeys.parameter.id],
                modulecache=modules[
                    single_timeserieskeys.moduleinstance.id],
                timestepcache=time_steps[
                    single_timeserieskeys.timestep.id],
                )
            time_series_cache.save()

    def __unicode__(self):
        return '%s' % (self.name)

    def api_url(self):
        return reverse(
            'lizard_fewsnorm_api_adapter',
            kwargs={'fews_norm_source_slug': self.slug})
