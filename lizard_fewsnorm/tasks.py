

from celery.task import task
from django.core import management


@task()
def sync_fewsnorm(user_name=None, db_name=None):
    """
    Importing location into cache table.
    """
    options = {"user_name": user_name, "db_name": db_name}
    management.call_command('sync_fewsnorm',
                            **options)
