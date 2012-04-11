# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import datetime

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from django.contrib.gis.geos import Point
#from django.conf import settings

from composite_pk import composite

from lizard_geo.models import GeoObject
from lizard_geo.models import GeoObjectGroup

from lizard_map.coordinates import rd_to_wgs84

from lizard_security.manager import FilteredGeoManager
from lizard_security.models import DataSet

from timeseries import timeseries


import logging
logger = logging.getLogger(__name__)


# Note: all fewsnorm dbs are assumed to have this schema.
#SCHEMA_PREFIX = 'nskv00_opdb\".\"'
SCHEMA_PREFIX = 'kvwn00_opdb\".\"'
#SCHEMA_PREFIX = 'kvrl00_opdb\".\"'


class Users(models.Model):
    userkey = models.IntegerField(primary_key=True,
                                  db_column='userkey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        #db_table = SCHEMA_PREFIX + u'users'
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
        #db_table = SCHEMA_PREFIX + u'parametergroups'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


# class FlexibleSchemaModel(object):
#     """
#     TODO: this doesn't work correctly. Replace all use with raw sqls

#     Create altered model using your own schemaname.

#     Meta.db_table and schema_prefix must be defined when using this
#     class.

#     """

#     @classmethod
#     def get_django_model(cls, schema_prefix=''):
#         """
#         Create a django model using a custom schemaname.
#         """
#         logger.debug('model db_table %s' % cls._meta.db_table)
#         if schema_prefix and '.' not in cls._meta.db_table:
#             cls._meta.db_table = schema_prefix + u'"."' + cls._meta.db_table
#             logger.debug('Added db_table %s', cls._meta.db_table)
#         return cls


class Location(models.Model):
    """
    Fewsnorm Location.
    """
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
    #relationalocationid = models.CharField(max_length=64)
    #relationblocationid = models.CharField(max_length=64)
    #attributea = models.CharField(max_length=64)
    #attributeb = models.FloatField()
    # Temporary related locations for "waterhoogte" and "chloride"
    # l_wathte = models.CharField(max_length=64)
    # l_chlor = models.CharField(max_length=64)

    class Meta:
        #db_table = u'locations'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id

    @classmethod
    def from_raw(cls, schema_prefix=''):
        """Due to schema difficulties and performance, use this function"""
        return cls.objects.raw("""
SELECT locationkey, id, name, shortname, description, icon, tooltip, parentlocationid,
       parentlocationid, visibilitystarttime, visibilityendtime, x, y, z, area
FROM
       "%(schema_prefix)s"."locations"
""" % {'schema_prefix': schema_prefix})


# TODO: flexible schema_prefix
# def getParameterModel(schema_prefix=None):

#     class ParameterMetaclass(models.base.ModelBase):
#         def __new__(cls, name, bases, attrs):
#             name += schema_prefix
#             return models.base.ModelBase.__new__(cls, name, bases, attrs)

class Parameter(models.Model):
    parameterkey = models.IntegerField(primary_key=True,
                                       db_column='parameterkey')
    # groupkey = models.ForeignKey(ParameterGroups,
    #                              db_column='groupkey')
    groupkey = models.CharField(max_length=64, db_column='groupkey')
    id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    valueresolution = models.FloatField()
    attributea = models.CharField(max_length=64)
    attributeb = models.FloatField()

    class Meta:
        #db_table = SCHEMA_PREFIX + u'parameters'
        managed = False

    def __unicode__(self):
        return '%s' % self.id

    @classmethod
    def from_raw(cls, schema_prefix=''):
        """Due to schema difficulties and performance, use this function"""
        return cls.objects.raw("""
SELECT par.parameterkey as parameterkey, gr.id as groupkey,
       par.id as id, par.name as name, par.shortname as shortname,
       par.description as description, par.valueresolution as valueresolution,
       par.attributea as attributea, par.attributeb as attributeb
FROM
       "%(schema_prefix)s"."parameters" as par
INNER JOIN "%(schema_prefix)s"."parametergroups" as gr ON (par.groupkey = gr.groupkey)
""" % {'schema_prefix': schema_prefix})


class Qualifiers(models.Model):
    qualifierkey = models.IntegerField(primary_key=True,
                                       db_column='qualifierkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        #db_table = SCHEMA_PREFIX + u'qualifiers'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class QualifierSets(models.Model):
    qualifiersetkey = models.IntegerField(primary_key=True,
                                          db_column='qualifiersetkey')
    id = models.CharField(unique=True, max_length=64)
    qualifierkey1 = models.CharField(max_length=64)
    qualifierkey2 = models.CharField(max_length=64)
    qualifierkey3 = models.CharField(max_length=64)
    qualifierkey4 = models.CharField(max_length=64)
    # qualifierkey1 = models.ForeignKey(Qualifiers,
    #                                   db_column='qualifierkey1',
    #                                   related_name='qualifierkey1')
    # qualifierkey2 = models.ForeignKey(Qualifiers,
    #                                   db_column='qualifierkey2',
    #                                   related_name='qualifierkey2',
    #                                   blank=True, null=True)
    # qualifierkey3 = models.ForeignKey(Qualifiers,
    #                                   db_column='qualifierkey3',
    #                                   related_name='qualifierkey3',
    #                                   blank=True, null=True)
    # qualifierkey4 = models.ForeignKey(Qualifiers,
    #                                   related_name='qualifierkey4',
    #                                   db_column='qualifierkey4',
    #                                   blank=True, null=True)

    class Meta:
        # db_table = SCHEMA_PREFIX + u'qualifiersets'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id

    @classmethod
    def from_raw(cls, schema_prefix=''):
        """Due to schema difficulties and performance, use this function
        """
        return cls.objects.raw("""
SELECT qs.qualifiersetkey as qualifiersetkey, qs.id as id,
       q1.id as qualifierkey1, q2.id as qualifierkey2,
       q3.id as qualifierkey3, q4.id as qualifierkey4
FROM
       "%(schema_prefix)s"."qualifiersets" as qs
LEFT OUTER JOIN "%(schema_prefix)s"."qualifiers" as q1 ON (qs.qualifierkey1 = q1.qualifierkey)
LEFT OUTER JOIN "%(schema_prefix)s"."qualifiers" as q2 ON (qs.qualifierkey2 = q2.qualifierkey)
LEFT OUTER JOIN "%(schema_prefix)s"."qualifiers" as q3 ON (qs.qualifierkey3 = q3.qualifierkey)
LEFT OUTER JOIN "%(schema_prefix)s"."qualifiers" as q4 ON (qs.qualifierkey4 = q4.qualifierkey)
""" % {'schema_prefix': schema_prefix})


class ModuleInstances(models.Model):
    moduleinstancekey = models.IntegerField(primary_key=True,
                                            db_column='moduleinstancekey')
    id = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        # db_table = SCHEMA_PREFIX + u'moduleinstances'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id

    @classmethod
    def from_raw(cls, schema_prefix=''):
        """Due to schema difficulties and performance, use this function
        """
        return cls.objects.raw("""
SELECT moduleinstancekey, id, name, description
FROM
       "%(schema_prefix)s"."moduleinstances"
""" % {'schema_prefix': schema_prefix})


class Timesteps(models.Model):
    timestepkey = models.IntegerField(primary_key=True,
                                      db_column='timestepkey')
    id = models.CharField(unique=True, max_length=64)
    #description = models.CharField(max_length=64)  # on testdatabase
    #label = models.CharField(max_length=64)  # on fewsnorm-dev

    class Meta:
        #db_table = SCHEMA_PREFIX + u'timesteps'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id

    @classmethod
    def from_raw(cls, schema_prefix=''):
        """Due to schema difficulties and performance, use this function
        """
        return cls.objects.raw("""
SELECT timestepkey, id
FROM
       "%(schema_prefix)s"."timesteps"
""" % {'schema_prefix': schema_prefix})


class AggregationPeriods(models.Model):
    aggregationperiodkey = models.IntegerField(
        primary_key=True,
        db_column='aggregationperiodkey')
    id = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        #db_table = SCHEMA_PREFIX + u'aggregationperiods'
        managed = False

    def __unicode__(self):
        return u'%s' % self.id


class Series(models.Model):
    """
    Due to difficulties in different schemas and databases:

    Use from_raw.
    """
    serieskey = models.IntegerField(primary_key=True,
                                    db_column='serieskey')
    location = models.CharField(max_length=64)
    parameter = models.CharField(max_length=64)
    qualifierset = models.CharField(max_length=64, blank=True, null=True)
    moduleinstance = models.CharField(max_length=64, blank=True, null=True)
    timestep = models.CharField(max_length=64, blank=True, null=True)
    aggregationperiod = models.CharField(max_length=64, blank=True, null=True)
    # location = models.ForeignKey(Location,
    #                              db_column='locationkey')
    # parameter = models.ForeignKey(Parameter,
    #                               db_column='parameterkey')
    # qualifierset = models.ForeignKey(QualifierSets,
    #                                     db_column='qualifiersetkey',
    #                                     blank=True, null=True)
    # moduleinstance = models.ForeignKey(ModuleInstances,
    #                                    db_column='moduleinstancekey',
    #                                    blank=True, null=True)
    # timestep = models.ForeignKey(Timesteps,
    #                              db_column='timestepkey',
    #                              blank=True, null=True)
    # aggregationperiod = models.ForeignKey(AggregationPeriods,
    #                                       db_column='aggregationperiodkey',
    #                                       blank=True, null=True)

    class Meta:
        #db_table = SCHEMA_PREFIX + u'timeserieskeys'
        managed = False

    def hash(self):
        return '%s::%s::%s::%s::%s' % (
            self.location, self.parameter, self.moduleinstance,
            self.timestep, self.qualifierset)

    def __unicode__(self):
        return u'%s %s %s %s' % (
            self.location,
            self.parameter,
            self.qualifierset,
            self.moduleinstance)

    @classmethod
    def from_raw(cls, schema_prefix=''):
        return cls.objects.raw("""
SELECT serieskey,
       loc.id as location,
       par.id as parameter,
       qua.id as qualifierset,
       mod.id as moduleinstance,
       tst.id as timestep ,
       agg.id as aggregationperiod
FROM
       "%(schema_prefix)s"."timeserieskeys" as ts
INNER JOIN "%(schema_prefix)s"."locations" as loc ON (ts.locationkey = loc.locationkey)
INNER JOIN "%(schema_prefix)s"."parameters" as par ON (ts.parameterkey = par.parameterkey)
LEFT OUTER JOIN "%(schema_prefix)s"."qualifiersets" as qua ON (ts.qualifiersetkey = qua.qualifiersetkey)
INNER JOIN "%(schema_prefix)s"."moduleinstances" as mod ON (ts.moduleinstancekey = mod.moduleinstancekey)
INNER JOIN "%(schema_prefix)s"."timesteps" as tst ON (ts.timestepkey = tst.timestepkey)
LEFT OUTER JOIN "%(schema_prefix)s"."aggregationperiods" as agg ON (ts.aggregationperiodkey = agg.aggregationperiodkey)
""" % {'schema_prefix': schema_prefix})


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
        #db_table = SCHEMA_PREFIX + u'timeseriesvaluesandflags'
        managed = False

    def __unicode__(self):
        return u'%s %s value=%s %s' % (
            self.series,
            self.timestamp,
            self.value,
            self.flag)

    @classmethod
    def filter_latest_before_deadline(
        cls, series_set, deadline, schema_prefix=''):
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

        if schema_prefix:
            schemaprefix_ = schema_prefix + '"."'
        else:
            schemaprefix_ = ''
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
                'schema_prefix': schema_prefix_,
                'serieskey': series_set__pk,
                'deadline': deadline__iso}).using(db_name)


class TimeseriesComments(models.Model):
    serieskey = models.ForeignKey(Series,
                                  primary_key=True,
                                  db_column='serieskey',
                                  blank=True, null=True)
    datetime = models.DateTimeField(primary_key=True)
    comment = models.CharField(max_length=64)

    class Meta:
        #db_table = SCHEMA_PREFIX + u'timeseriescomments'
        managed = False

    def __unicode__(self):
        return u'%s' % self.comment

    @classmethod
    def filter_comment(cls, series, datetime, schema_prefix=''):
        """
        Return comment object for given series and datetime.

        Crashes if nothing found.

        Comparable with Event.filter_latest_before_deadline
        """
        location = GeoLocationCache.objects.get(
            ident=series.location.id)
        db_name = location.fews_norm_source.database_name
        return TimeseriesComments.get_raw(
            schema_prefix=schema_prefix).objects.using(
            db_name).get(serieskey=series, datetime=datetime)

    @classmethod
    def from_raw(cls, schema_prefix=''):
        """Due to schema difficulties and performance, use this function
        TO BE TESTED
        """
        return cls.objects.raw("""
SELECT serieskey, datetime, comment
FROM
       "%(schema_prefix)s"."timeseriescomments"
""" % {'schema_prefix': schema_prefix})


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

class QualifierSetCacheManager(models.Manager):
    def get_by_natural_key(self, ident):
        return self.get(ident=ident)


class QualifierSetCache(models.Model):
    objects = QualifierSetCacheManager()

    ident = models.CharField(max_length=64)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return '%s' % self.ident

    def natural_key(self):
        return (self.ident, )


class ParameterCacheManager(models.Manager):
    def get_by_natural_key(self, ident):
        return self.get(ident=ident)


class ParameterCache(models.Model):
    objects = ParameterCacheManager()

    ident = models.CharField(max_length=64)

    name = models.CharField(max_length=64, null=True, blank=True)

    shortname = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return '%s' % self.ident

    def api_url(self):
        return reverse('lizard_fewsnorm_api_parameter_detail',
                       kwargs={'ident': self.ident})

    def natural_key(self):
        return (self.ident, )


class ModuleCacheManager(models.Manager):
    def get_by_natural_key(self, ident):
        return self.get(ident=ident)


class ModuleCache(models.Model):
    objects = ModuleCacheManager()

    ident = models.CharField(max_length=64)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return u'%s' % self.ident

    def natural_key(self):
        return (self.ident, )


class TimeStepCacheManager(models.Manager):
    def get_by_natural_key(self, ident):
        return self.get(ident=ident)


class TimeStepCache(models.Model):
    objects = TimeStepCacheManager()

    ident = models.CharField(max_length=64)

    class Meta:
        ordering = ('ident', )

    def __unicode__(self):
        return u'%s' % self.ident

    def natural_key(self):
        return (self.ident, )


class GeoLocationCacheManager(FilteredGeoManager):
    def get_by_natural_key(self, ident):
        # Normally we would use self.get, but that doesn't work in
        # this case.
        return GeoLocationCache.objects.get(ident=ident)


class GeoLocationCache(GeoObject):
    """
    Geo cache for locations from all data sources.
    """
    objects = GeoLocationCacheManager()

    data_set = models.ForeignKey(DataSet, null=True, blank=True)
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
    active = models.BooleanField(default=True)

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

    def natural_key(self):
        return (self.ident, )


class TimeSeriesCache(models.Model):
    """
    Cache time series objects from all sources.

    Use this object as an entrypoint to fetch data.
    """
    geolocationcache = models.ForeignKey(GeoLocationCache)
    parametercache = models.ForeignKey(ParameterCache)
    modulecache = models.ForeignKey(ModuleCache)
    timestepcache = models.ForeignKey(TimeStepCache)
    qualifiersetcache = models.ForeignKey(QualifierSetCache,
                                          blank=True, null=True)
    active = models.BooleanField(default=True)

    # class Meta:
    #     unique_together = ('geolocationcache', 'parametercache',
    #                        'modulecache', 'timestepcache')

    def __unicode__(self):
        return '%s,%s,%s' % (
            self.geolocationcache.ident,
            self.parametercache.ident,
            self.id)

    def hash(self):
        if self.qualifiersetcache is not None:
            qualifier_set_id = self.qualifiersetcache.id
        else:
            qualifier_set_id = None
        return '%s::%s::%s::%s::%s' % (
            self.geolocationcache.ident, self.parametercache.ident,
            self.modulecache.ident, self.timestepcache.ident, qualifier_set_id)

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
                {'schema_prefix': SCHEMA_PREFIX,
                 'loc_id': str(self.geolocationcache.ident),
                 'par_id': str(self.parametercache.ident),
                 'mod_id': str(self.modulecache.ident)}))
        return Series.objects.raw(series_query).using(db_name)

    def get_latest_event(self, now=None, with_comments=False):
        """
        Return latest event for this timeseries.

        TODO: improve with_comments option.
        """
        if now is None:
            now = datetime.datetime.now()
        series_set = self._series_set()
        event = Event.filter_latest_before_deadline(
            series_set, now)[0]
        if with_comments:
            # event.comment = 'test comment'
            # assume the serie_set is not empty!
            try:
                comment = TimeseriesComments.filter_comment(
                    series_set[0], event.timestamp)
                event.comment = comment.comment
            except TimeseriesComments.DoesNotExist:
                # No comment found
                pass
        return event

    def get_timeseries(self, dt_start=None, dt_end=None):
        """
        Return TimeSeries dictionary.

        Key is (location, parameter), Value is TimeSeries object.
        """
        series_set = self._series_set()
        return timeseries.TimeSeries.as_dict(series_set, dt_start, dt_end)

    @classmethod
    def save_raw_dict(cls, timeseries):
        """
        Use this to save a batch of timeseries.

        Timeseries are stored as dictionaries as when using .values() function.

        You must add an attribute 'new' to each timeseries to
        determine create or update.
        """
        # Slow version
        # no_saved = 0
        # no_nonactive = 0
        # logger.debug('Saving %d objects...' % len(timeseries))
        # for single_timeseries in timeseries:
        #     if not single_timeseries.active:
        #         no_nonactive += 1
        #         logger.warning('Inactive timeseries: %s' % single_timeseries)
        #     single_timeseries.save()
        #     no_saved += 1
        #     if no_saved % 100 == 0:
        #         logger.debug('Saved %d timeseries' % no_saved)
        # return no_saved, no_nonactive

        from django.db import connection, transaction
        cursor = connection.cursor()

        no_saved = 0
        no_created = 0
        no_existing = 0
        no_nonactive = 0

        for single_timeseries in timeseries:
            if not single_timeseries['active']:
                no_nonactive += 1
            timeseries_dict = {
                'id': single_timeseries.get('id', None),  # Id only for existing items
                'geo_id': single_timeseries['geolocationcache__id'],
                'par_id': single_timeseries['parametercache__id'],
                'mod_id': single_timeseries['modulecache__id'],
                'tst_id': single_timeseries['timestepcache__id'],
                'active': 'TRUE' if single_timeseries['active'] else 'FALSE',
                'qua_id': single_timeseries['qualifiersetcache__id'] if
                single_timeseries['qualifiersetcache__id'] else 'null',  # Can be None
                }
            if single_timeseries['new']:
                #insert
                cursor.execute("""
INSERT INTO lizard_fewsnorm_timeseriescache (geolocationcache_id, parametercache_id, modulecache_id, timestepcache_id, active, qualifiersetcache_id) VALUES (%(geo_id)d, %(par_id)d, %(mod_id)d, %(tst_id)d, %(active)s, %(qua_id)s)
""" % timeseries_dict)
                no_created += 1
            else:
                cursor.execute("""
UPDATE lizard_fewsnorm_timeseriescache SET geolocationcache_id = %(geo_id)d, parametercache_id = %(par_id)d, modulecache_id = %(mod_id)d, timestepcache_id = %(tst_id)d, active = %(active)s, qualifiersetcache_id = %(qua_id)s WHERE id = %(id)d
""" % timeseries_dict)
                no_existing += 1

            no_saved += 1
            if no_saved % 10000 == 0:
                logger.debug('Saved %d objects.' % no_saved)
        logger.debug('committing...')
        transaction.commit_unless_managed()

        return no_saved, no_created, no_existing, no_nonactive



class TrackRecordCache(GeoObject):
    """
    Hold results from complex query on fewsnorm database
    """
    objects = FilteredGeoManager()

    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    fews_norm_source = models.ForeignKey('FewsNormSource')

    parameter = models.ForeignKey(ParameterCache, null=True, blank=True)
    location = models.ForeignKey(GeoLocationCache, null=True, blank=True)
    module = models.ForeignKey(ModuleCache, null=True, blank=True)

    datetime = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        ordering = ['datetime']

    def __unicode__(self):
        return '%s - %s' % (self.location, self.parameter)


class FewsNormSource(models.Model):
    """
    Define a source database for fews norm.

    We're using fewsnorm database models:
    - Location
    - Parameter
    - ModuleInstances
    - Timesteps
    - QualifierSets
    - Series
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    database_name = models.CharField(max_length=40, unique=True)
    database_schema_name = models.CharField(
        max_length=80, null=True, blank=True)
    active = models.BooleanField(default=True)

    def source_locations(self):
        return list(Location.from_raw(
            schema_prefix=self.database_schema_name).using(self.database_name))

    @transaction.commit_on_success
    def get_or_create_geoobjectgroup(self, user_name=None):
        if user_name is None:
            user_obj = User.objects.all()[0]  # Random user
        else:
            user_obj = User.objects.get(username=user_name)
        group_name = 'FEWSNORM::%s' % self.database_name
        group_slug = slugify(group_name)
        geo_object_group, created = GeoObjectGroup.objects.get_or_create(
            slug=group_slug,
            defaults={'name': group_name, 'created_by': user_obj})
        if not created:
            geo_object_group.name = group_name
            geo_object_group.created_by = user_obj
            geo_object_group.save()
        if created:
            logger.info('Newly created geoobjectgroup %s' % geo_object_group)
            geo_object_group.source_log = 'FEWSNORM::%s' % self.database_name
            geo_object_group.save()
        return geo_object_group

    @transaction.commit_on_success
    def sync_parameter_cache(self):
        """
        Fill ParameterCache
        """
        parameters = {}
        no_touched = 0
        no_created = 0
        for parameter in Parameter.from_raw(
            self.database_schema_name).using(self.database_name):

            parameter_cache, created = ParameterCache.objects.get_or_create(
                ident=parameter.id,
                defaults={
                    'name': parameter.name,
                    'shortname': parameter.shortname,
                }
            )
            if created:
                logger.info('Newly created parameter %s' % parameter_cache)
                no_created += 1
            else:
                parameter_cache.name = parameter.name
                parameter_cache.shortname = parameter.shortname
                parameter_cache.save()
                # logger.debug('Updated/touched parameter %s' % parameter_cache)
                no_touched += 1
            parameters[parameter_cache.ident] = parameter_cache
        logger.info('No of parameters created: %d' % no_created)
        logger.info('No of parameters updated/touched: %d' % no_touched)
        return parameters

    @transaction.commit_on_success
    def sync_module_cache(self):
        """
        Fill ModuleCache.
        """
        modules = {}
        for module in ModuleInstances.from_raw(
            self.database_schema_name).using(self.database_name):

            module_cache, _ = ModuleCache.objects.get_or_create(
                ident=module.id)
            modules[module_cache.ident] = module_cache
        return modules

    @transaction.commit_on_success
    def sync_time_step_cache(self):
        """
        Fill TimeStepCache.
        """
        time_steps = {}
        for time_step in Timesteps.from_raw(
            self.database_schema_name).using(self.database_name):

            time_step_cache, _ = TimeStepCache.objects.get_or_create(
                ident=time_step.id)
            time_steps[time_step_cache.ident] = time_step_cache
        return time_steps

    @transaction.commit_on_success
    def sync_qualifier_set_cache(self):
        """
        Fill QualifierSetCache
        """
        qualifier_sets = {}
        for qualifier_set in QualifierSets.from_raw(
            self.database_schema_name).using(
            self.database_name):

            qualifier_set_cache, cr = QualifierSetCache.objects.get_or_create(
                ident=qualifier_set.id)
            qualifier_sets[qualifier_set_cache.ident] = qualifier_set_cache
            if cr:
                logger.info('Newly created qualifier set %s' %
                            qualifier_set_cache)
        return qualifier_sets

    @transaction.commit_on_success
    def sync_location_cache(
        self, data_set=None, user_name=None):
        """
        Fill GeoLocationCache.

        Inactivates all existing entries, then re-enable all
        occurrences that are present in the source.

        parameters and modules are dicts with ParameterCache and
        ModuleCache. Keys are their idents.
        """
        logger.debug('Reading existing locations from source...')
        source_locations = self.source_locations()
        geo_object_group = self.get_or_create_geoobjectgroup(user_name)

        logger.debug('Reading current locations cache...')
        locations = {}
        for glc in GeoLocationCache.objects.filter(fews_norm_source=self):
            glc.active = False
            locations[glc.ident] = glc

        no_existing = 0
        no_created = 0
        no_nonactive = 0
        logger.debug('Checking %d locations...' % len(source_locations))
        for location in source_locations:
            new_ident = location.id[:80]
            if new_ident in locations:
                # Update existing
                no_existing += 1
                current_location = locations[new_ident]
            else:
                # New
                no_created += 1
                current_location = GeoLocationCache(ident=new_ident)
            # (Over)write params
            wgs84_x, wgs84_y = rd_to_wgs84(location.x, location.y)
            current_location.data_set = data_set
            current_location.fews_norm_source = self
            current_location.name = '%s' % location.name
            current_location.shortname = '%s' % location.shortname
            current_location.icon = '%s' % location.icon
            current_location.tooltip = '%s' % location.tooltip
            current_location.geo_object_group = geo_object_group
            current_location.geometry = GEOSGeometry(
                Point(wgs84_x, wgs84_y), srid=4326)
            current_location.active = True
            locations[new_ident] = current_location

        # Save locations
        logger.debug('Saving %d objects...' % len(locations))
        for location in locations.values():
            if not location.active:
                no_nonactive += 1
                logger.warning('Inactive location: %s' % location)
            location.save()

        logger.info('Newly created locations: %d' % no_created)
        logger.info('Updated/touched locations: %d' % no_existing)
        logger.info('Non-active locations: %d' % no_nonactive)
        return locations

    @transaction.commit_on_success
    def sync_time_series_cache(
        self, locations, parameters, modules, time_steps,
        qualifier_sets, data_set_name=None):
        """
        Synchronize the time series cache with the source.

        Inactivates all existing entries, then re-enable all
        occurrences that are present in the source.

        Note that active timeseries CAN refer to an inactive location.
        """
        def ts_hash(ts_dict):
            """Generate temp hash for a timeseries dict"""
            return '%s::%s::%s::%s::%s' % (
                ts_dict['geolocationcache__ident'],
                ts_dict['parametercache__ident'],
                ts_dict['modulecache__ident'],
                ts_dict['timestepcache__ident'],
                ts_dict.get('qualifiersetcache__ident', None))

        # Collect new series
        logger.debug('Reading existing series from source...')
        series = list(Series.from_raw(self.database_schema_name).using(
            self.database_name))
        # series_dict = dict([(single_series.hash(), single_series) for
        #                     single_series in series])

        # Current cache: fist set all to non-active
        logger.debug('Reading existing series cache...')
        time_series_cache_dict = {}
        for single_time_series_cache in TimeSeriesCache.objects.filter(
            geolocationcache__fews_norm_source=self).values(
            'geolocationcache__ident', 'geolocationcache__id',
            'parametercache__ident', 'parametercache__id',
            'modulecache__ident', 'modulecache__id',
            'timestepcache__ident', 'timestepcache__id',
            'qualifiersetcache__ident', 'qualifiersetcache__id',
            'id'):
            # The idents are only needed to create the temporary
            # hash. When creating a new object, it is sufficient to
            # use an id only.

            single_time_series_cache['active'] = False
            single_time_series_cache['new'] = False  # Custom, for TimeSeriesCache.save_raw
            time_series_cache_dict[
                ts_hash(single_time_series_cache)] = single_time_series_cache

        no_processed = 0
        logger.debug('Checking %d series...' % len(series))
        for single_series in series:
            series_hash = single_series.hash()
            no_processed += 1
            if series_hash in time_series_cache_dict:
                # Update existing
                current_time_series = time_series_cache_dict[series_hash]
            else:
                # New
                if qualifier_sets[single_series.qualifierset]:
                    qualifier_set_id = qualifier_sets[single_series.qualifierset].id
                else:
                    qualifier_set_id = None
                current_time_series = {
                    'geolocationcache__id': locations[single_series.location].id,
                    'parametercache__id': parameters[single_series.parameter].id,
                    'modulecache__id': modules[single_series.moduleinstance].id,
                    'timestepcache__id': time_steps[single_series.timestep].id,
                    'qualifiersetcache__id': qualifier_set_id,
                    }
                current_time_series['new'] = True  # For TimeSeriesCache.save_raw
            current_time_series['active'] = True
            time_series_cache_dict[series_hash] = current_time_series
            # if no_processed % 100000 == 0:
            #     logger.debug('# processed timeseries: %d' % no_processed)

        no_saved, no_created, no_existing, no_nonactive = TimeSeriesCache.save_raw_dict(
            time_series_cache_dict.values())

        logger.info('Saved timeseries: %d' % no_saved)
        logger.info('Newly created timeseries: %d' % no_created)
        logger.info('Updated existing timeseries: %d' % no_existing)
        logger.info('Non-active timeseries: %d' % no_nonactive)

    # @transaction.commit_on_success
    def sync_track_record_cache(self, data_set=None):
        """
        Synchronize trackrecords
        """
        TRACKRECORD_PARAMETERS = ('BodemP.kritisch', )
        TRACKRECORD_COORDINATES = ('Xpos', 'Ypos')
        TRACKRECORD_GEOOBJECTGROUP = 'TrackRecordCache'

        # Get the first superuser for the geoobject group
        geo_object_group_user = User.objects.filter(is_superuser=True)[0]

        geo_object_group = GeoObjectGroup.objects.get_or_create(
            name=TRACKRECORD_GEOOBJECTGROUP,
            slug=slugify(TRACKRECORD_GEOOBJECTGROUP),
            defaults = {'created_by': geo_object_group_user}
        )[0]

        parametercaches = [ParameterCache.objects.get(ident=trp)
                           for trp in TRACKRECORD_PARAMETERS]
        xpos_cache, ypos_cache = [ParameterCache.objects.get(ident=trp)
                                  for trp in TRACKRECORD_COORDINATES]

        for p in parametercaches:
            geolocationcaches = GeoLocationCache.objects.filter(parameter=p)

            for g in geolocationcaches:
                # Collect value, xpos and ypos events at this location
                value_events = TimeSeriesCache.objects.get(
                    geolocationcache=g,
                    parametercache=p,
                ).get_timeseries().values()[0].get_events()
                xpos_events = TimeSeriesCache.objects.get(
                    geolocationcache=g,
                    parametercache=xpos_cache,
                ).get_timeseries().values()[0].get_events()
                ypos_events = TimeSeriesCache.objects.get(
                    geolocationcache=g,
                    parametercache=ypos_cache,
                ).get_timeseries().values()[0].get_events()

                # Some dicts for easy matching of events by date
                xpos_events_dict = dict([(str(e[0]), e)
                                          for e in xpos_events])
                ypos_events_dict = dict([(str(e[0]), e)
                                          for e in ypos_events])

                for value_event in value_events:
                    # Note we check if coordinates are present for a value,
                    # but not if values are present for each coordinate.
                    datestr = str(value_event[0])
                    if (datestr in xpos_events_dict and
                        datestr in ypos_events_dict):
                        x_rd = xpos_events_dict[datestr][1][0]
                        y_rd = ypos_events_dict[datestr][1][0]
                        x_wgs84, y_wgs84 = rd_to_wgs84(x_rd, y_rd)
                        geometry = GEOSGeometry(
                            Point(x_wgs84, y_wgs84),
                            srid=4326,
                        )

                        track_record_cache_kwargs = {
                            'data_set': data_set,
                            'fews_norm_source': self,
                            'parameter': p,
                            'location': g,
                            'module': None,
                            'geo_object_group': geo_object_group,
                            'geometry': geometry,
                            'datetime': value_event[0],
                            'value': value_event[1][0],
                        }
                        TrackRecordCache.objects.get_or_create(
                            **track_record_cache_kwargs)
        return None

    def __unicode__(self):
        return '%s' % (self.name)

    def api_url(self):
        return reverse(
            'lizard_fewsnorm_api_adapter',
            kwargs={'fews_norm_source_slug': self.slug})
