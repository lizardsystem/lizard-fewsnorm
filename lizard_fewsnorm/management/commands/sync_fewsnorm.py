#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from optparse import make_option

from django.core.management.base import BaseCommand
from lizard_fewsnorm.models import FewsNormSource
from django.db import transaction

from lizard_security.models import DataSet

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Synchronizes locations of datasources into GeoLocationCache.
    """

    help = ("Example: bin/django sync_fewsnorm "\
            "--db_name=fewsnorm1 --data_set=MyDataSet")

    option_list = BaseCommand.option_list + (
        make_option('--db_name',
                    help='name of fewsnorm database, optionally',
                    type='str',
                    default=None),
        make_option('--data_set',
                    help='name of the data set',
                    type='str',
                    default=None))

    def get_sources(self, source):
        if source is None:
            logger.info("No database provided, taking all FewsNormSource "
                        "entries.")
            return FewsNormSource.objects.filter(active=True)
        else:
            logger.info("Filtering FewsNormSource on database_name='%s'." %
                        source)
            # Note: you can also sync non-active sources.
            return FewsNormSource.objects.filter(database_name=source)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        data_set_name = options["data_set"]
        if data_set_name:
            data_set = DataSet.objects.get(name=data_set_name)
        else:
            data_set = None

        sources = self.get_sources(options["db_name"])
        if not sources:
            logger.info("No databases selected. Check your database "
                        "settings and db_name (if provided) .")
        for source in sources:
            logger.info('Updating %s...' % source)
            logger.debug(
                'Updating ParameterCache for fewsnorm %s...', source.name)
            parameters = source.sync_parameter_cache()

            logger.debug(
                'Updating ModuleCache for fewsnorm %s...', source.name)
            modules = source.sync_module_cache()

            logger.debug(
                'Updating TimeStepCache for fewsnorm %s...', source.name)
            time_steps = source.sync_time_step_cache()

            logger.debug(
                'Updating GeoLocationCache for fewsnorm %s...', source.name)
            locations = source.sync_location_cache(data_set)
            # from lizard_fewsnorm.models import GeoLocationCache
            # locations = dict([(l.ident, l) for l in GeoLocationCache.objects.filter(fews_norm_source=source)])

            logger.debug(
                'Updating QualifierSetCache for fewsnorm %s...', source.name)
            qualifier_sets = source.sync_qualifier_set_cache()

            logger.debug(
                'Updating TimeSeriesCache for fewsnorm %s...', source.name)
            source.sync_time_series_cache(
                locations, parameters, modules, time_steps, qualifier_sets)
