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
    Synchronizes trackrecords in datasources into TrackRecordCache.
    """

    help = ("Example: bin/django sync_track_records "\
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
            logger.debug(
                'Updating AqmadCache for %s...', source.name,
            )
            source.sync_aqmad()
