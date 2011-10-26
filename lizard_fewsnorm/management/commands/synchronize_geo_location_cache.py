#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from optparse import make_option

from django.core.management.base import BaseCommand
from lizard_fewsnorm.models import FewsNormSource
from django.db import transaction

import logging
log = logging.getLogger("lizard-fewsnorm.management.command.sync_cache")


class Command(BaseCommand):
    """
    Synchronizes the location of datasources
    into GeoLocationCache.
    """

    help = ("Example: bin/django synchronize_geo_location_cache "\
            "--source=fewsnorm1 --user_name=buildout")

    option_list = BaseCommand.option_list + (
        make_option('--source',
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

    def handle(self, *args, **options):
        user_name = options["user_name"]
        if user_name is None:
            log.error("Expects a user name, use --help for usage.")
            return

        sources = self.get_sources(options["source"])
        for source in sources:
            source.synchronize_cache(user_name)
