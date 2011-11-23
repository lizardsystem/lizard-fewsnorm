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
        db_table = u'parametergroups'
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
        db_table = u'locations'
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
        db_table = u'parameters'
        #db_schema = 'nskv00_opdb'
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
        db_table = u'qualifiersets'
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
        db_table = u'moduleinstances'
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
        db_table = u'timesteps'
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
        db_table = u'aggregationperiods'
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
        db_table = u'timeserieskeys'
        managed = False

    def __unicode__(self):
        return u'%s %s %s %s' % (
            self.location,
            self.parameter,
            self.qualifierset,
            self.moduleinstance)

    @classmethod
    def from_lppairs(cls, lppairs):
        """select series matching zipped location parameter iterable.
        """

        location = None
        for (l, p) in lppairs:
            try:
                location = GeoLocationCache.objects.get(ident=l)
                break
            except:
                pass
        if location is None:
            return None

        db_name = location.fews_norm_source.database_name

        locations = Location.objects.using(db_name).filter(
            id__in=[l for (l, p) in lppairs])
        parameters = Parameter.objects.using(db_name).filter(
            id__in=[p for (l, p) in lppairs])

        l_id_to_pk = dict((l.id, l.pk) for l in locations)
        p_id_to_pk = dict((p.id, p.pk) for p in parameters)

        keys = tuple((l_id_to_pk[l], p_id_to_pk[p]) for (l, p) in lppairs)

        return cls.objects.raw("\
SELECT * FROM \"timeserieskeys\" \
WHERE (locationkey, parameterkey) IN %s" % (keys,)).using(db_name)


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
        db_table = u'timeseriesvaluesandflags'
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

        series_set__pk = tuple(s.pk for s in series_set)
        deadline__iso = deadline.isoformat()

        ## execute the query.
        return cls.objects.raw("""\
SELECT e.* FROM timeseriesvaluesandflags e
  JOIN (SELECT serieskey, max(datetime) AS datetime
        FROM timeseriesvaluesandflags
        WHERE serieskey in %s
          AND datetime < '%s'
              GROUP BY serieskey) latest
  ON e.serieskey = latest.serieskey
  AND e.datetime = latest.datetime""" % (
                series_set__pk, deadline__iso)).using(db_name)


class TimeseriesComments(models.Model):
    serieskey = models.ForeignKey(Series,
                                  primary_key=True,
                                  db_column='serieskey',
                                  blank=True, null=True)
    datetime = models.DateTimeField(primary_key=True)
    comments = models.CharField(max_length=64)

    class Meta:
        db_table = u'timeseriescomments'
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
        db_table = u'timeseriesmanualeditshistory'
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
        return 'loc %s, par %s, mod %s, tstep %s' % (
            self.geolocationcache,
            self.parametercache,
            self.modulecache,
            self.timestepcache)

    def api_url(self):
        return reverse('lizard_fewsnorm_api_timeseries_detail',
                       kwargs={'id': self.id})

    # def get_timeserie(self, dt_start, dt_end):
    #     source = self.geolocationcache.fews_norm_source()
    #     timeserieskey = source.o(self.TimeseriesKey).filter(
    #         locationkey__id=self.geolocationcache.ident,
    #         parameterkey__id=self.parametercache.ident,
    #         moduleinstancekey__id=self.modulecache.ident)
    #     if len(timeserieskey) == 0:
    #         return []
    #     else:
    #         serieskey = timeserieskey[0]
    #         return serieskey.timeseriesvaluesandflags_set.objects.filter(
    #             datetime__gte=dt_start,
    #             datetime__lte=dt_end)

    # def get_latest_value(self, dt_start, dt_end):
    #     timeserie = self.get_timeserie(dt_start, dt_end).order_by(
    # '-timestep')
    #     if len(timeserie) > 0:
    #         return timeserie[0]


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
        for parameter in self.o(Parameter).all():
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
        for module in self.o(ModuleInstances).all():
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
        for time_step in self.o(Timesteps).all():
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

        timeserieskeys = self.o(Series).all()
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

    # def o(self, model_object):
    #     """
    #     Return Model using database_name.

    #     Using the short name o because the function is supposed to be
    #     a shortcut.

    #     Example usage:

    #     >>> source = FewsNormSource(name='test', database_name='default')
    #     >>> source.o(FewsNormSource).all()
    #     []
    #     """

    #     return model_object.objects.using(self.database_name)

    def api_url(self):
        return reverse(
            'lizard_fewsnorm_api_adapter',
            kwargs={'fews_norm_source_slug': self.slug})
