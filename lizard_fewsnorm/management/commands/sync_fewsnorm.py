#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from optparse import make_option

from django.core.management.base import BaseCommand
from lizard_fewsnorm.models import FewsNormSource
from django.db import transaction

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Synchronizes the location of datasources
    into GeoLocationCache.
    """

    help = ("Example: bin/django synchronize_geo_location_cache "\
            "--source=fewsnorm1 --user_name=buildout")

    option_list = BaseCommand.option_list + (
        make_option('--db_name',
                    help='name of fewsnorm database, optionally',
                    type='str',
                    default=None),
        make_option('--user_name',
                    help='user name',
                    type='str',
                    default=None))

    def get_sources(self, source):
        if source is None:
            return FewsNormSource.objects.all()
        else:
            return FewsNormSource.objects.filter(database_name=source)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        user_name = options["user_name"]
        if user_name is None:
            logger.error("Provide a user_name, use --help for usage.")
            return

        sources = self.get_sources(options["db_name"])
        if not sources:
            logger.info("No databases selected. Check your db_name, "
                        "if provided.")
        for source in sources:
            logger.debug(
                'Creating ParameterCache for fewsnorm %s...', source.name)
            parameters = source.synchronize_parameter_cache()

            logger.debug(
                'Creating ModuleCache for fewsnorm %s...', source.name)
            modules = source.synchronize_module_cache()

            logger.debug(
                'Creating TimeStepCache for fewsnorm %s...', source.name)
            time_steps = source.synchronize_time_step_cache()

            logger.debug(
                'Creating GeoLocationCache for fewsnorm %s...', source.name)
            locations = source.synchronize_location_cache(user_name)

            logger.debug(
                'Creating TimeSeriesCache for fewsnorm %s...', source.name)
            source.synchronize_time_series_cache(
                locations, parameters, modules, time_steps)