#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction
from lizard_fewsnorm.tasks import sync_fewsnorm as sync_fewsnorm_task

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Synchronizes locations of datasources into GeoLocationCache.
    """

    help = ("Example: bin/django sync_fewsnorm "\
            "--db_name=fewsnorm1 --celery")

    option_list = BaseCommand.option_list + (
        make_option('--db_name',
                    help='name of fewsnorm database, optionally',
                    type='str',
                    default=None),
        make_option('--celery',
                    help='run the task with celery',
                    action='store_true',
                    dest='celery',
                    default=False),
        )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        #data_set_name = options.get("data_set", None)
        #print data_set_name
        if options["celery"]:
            sync_fewsnorm_task.delay(
                username=None,
                taskname=None,
                db_name=options.get("db_name", None))
        else:
            sync_fewsnorm_task(
                username=None,
                taskname=None,
                db_name=options.get("db_name", None))
        # return 'started'
