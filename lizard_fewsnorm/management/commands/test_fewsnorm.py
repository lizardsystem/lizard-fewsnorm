#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

import datetime
from django.core.management.base import BaseCommand
from lizard_fewsnorm.models import TimeSeriesCache

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    """

    help = ("Example: bin/django synchronize_geo_location_cache "\
            "--source=fewsnorm1 --user_name=buildout")

    def handle(self, *args, **options):
        print 'hoi'
        tsc = TimeSeriesCache.objects.filter(
            geolocationcache__ident='PGMO',
            parametercache__ident='NP.Ratio')[0]
        print tsc
        e = tsc.get_latest_event()
        print e
        dt_start = datetime.datetime(2005, 1, 1)
        dt_end = datetime.datetime(2010, 1, 1)
        timeseries = tsc.get_timeseries(dt_start, dt_end)
        for (l, p), single_ts in timeseries.items():
            print '---------------'
            print '%s %s' % (l, p)
            print single_ts.sorted_event_items()
