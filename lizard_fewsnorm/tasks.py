import logging

from celery.task import task

from lizard_task.handler import get_handler

from lizard_fewsnorm.models import FewsNormSource
from lizard_fewsnorm.models import FEWSNORM_LOG_NAME
from lizard_security.models import DataSet


logger = logging.getLogger(__name__)


def get_sources(source=None):
    if source is None:
        logger.info("No database provided, taking all FewsNormSource "
                    "entries.")
        return FewsNormSource.objects.filter(active=True)
    else:
        logger.info("Filtering FewsNormSource on database_name='%s'." %
                    source)
        # Note: you can also sync non-active sources.
        return FewsNormSource.objects.filter(database_name=source)


@task
def sync_fewsnorm(username=None, db_name=None, taskname=None):
    """
    The fewsnorm sync function

    Option data_set_name
    """
    #logger = sync_fewsnorm.get_logger()

    handler = get_handler(username=username, taskname=taskname)
    logger = logging.getLogger(FEWSNORM_LOG_NAME)
    logger.addHandler(handler)
    logger.setLevel(20)

    sources = get_sources(db_name)
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
        locations = source.sync_location_cache()
        # from lizard_fewsnorm.models import GeoLocationCache
        # locations = dict([(l.ident, l) for l in GeoLocationCache.objects.filter(fews_norm_source=source)])

        logger.debug(
            'Updating QualifierSetCache for fewsnorm %s...', source.name)
        qualifier_sets = source.sync_qualifier_set_cache()

        logger.debug(
            'Updating TimeSeriesCache for fewsnorm %s...', source.name)
        source.sync_time_series_cache(
            locations, parameters, modules, time_steps, qualifier_sets)

    logger.removeHandler(handler)

    return 'OK'
