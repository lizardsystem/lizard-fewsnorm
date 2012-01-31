lizard-fewsnorm
==========================================

Introduction
------------

Provide api and interface to fews norm databases.

A FEWS Norm database is a database used by FEWS. The database is
unblobbed and therefore useful results can be retrieved by ordinary
queries, unlike the standard (blobbed) FEWS database. It contains
locations, parameters, timeseries and other (meta) information.

We mainly want to display locations and their timeseries. Use the REST
API or the Lizard interface to browse through the data.

Multiple FEWS Norm databases can be defined in FewsNormSource. We want
to search through locations/parameters/... from all those databases in
a fast way. To accomplish this, locations, parameters, modules
and timeseries (without data) are synchronized to a single database.

Usage
-----

bootstrap
~~~~~~~~~

First time you use lizard_fewsnorm, you will need to follow these instructions.

* get hold of a fewsnorm data source.
* edit your `settings.py` (or `testsettings.py`) and add an entry to the `DATABASES` dictionary.
 * you might need explicitly set all fields, included `HOST` and `PORT`.
 * use the correct `ENGINE`: django.contrib.gis.db.backends.postgis
* syncdb
* in the django site admin, add an item to 'fews norm sources', referring to the `DATABASES` entry.

common administration
~~~~~~~~~~~~~~~~~~~~~
Your fewsnorm data source can contain multiple fews norm databases.

Each time a fews norm database is added to your fewsnorm data source you need synchronize things.

You also need synchronizing when locations, parameters and/or moduleinstances are added.

In practice, you need to synchronize regularly. To sync your locations, timeseries, parameters, modules::

    $> bin/django sync_fewsnorm

What it does is updating all existing locations, timeseries. Locations
and timeseries that do not exist in the source get a flag
inactive. Since version 0.7, objects are not re-created anymore, so it
is safe to run sync_fewsnorm and not break your dependencies.


dumpdata
~~~~~~~~

We only want to dump data from the default database. This is the way
to do it::

    $> bin/django dumpdata lizard_fewsnorm.FewsNormSource lizard_fewsnorm.ParameterCache lizard_fewsnorm.ModuleCache lizard_fewsnorm.TimeStepCache lizard_fewsnorm.TimeSeriesCache lizard_fewsnorm.GeoLocationCache lizard_geo --indent=2



Adapter
-------

The lizard interface shows clickable locations on a map. You can also
put workspace items in your workspace and put locations into your
selections. These features are available using an implementation of
the lizard-map "adapter".


API
---

The REST API provides:
- List of FewsNormSources;
- List of locations;
- List of parameters;
- Adapter access (experimental).


Development installation
------------------------

The first time, you'll have to run the bootstrap script to set up setuptools
and buildout::

    $> python bootstrap.py

And then run buildout to set everything up::

    $> bin/buildout

Note that on Microsoft Windows it is called ``bin\buildout.exe``.

You will have to re-run buildout when ``setup.py`` or ``buildout.cfg`` have
been modified, for example directly by you or through an update of your working
directory.

You need PostGIS in order to use the adapter.


How to use timeseries in your own app
-------------------------------------

1) Find out the database_name. All possible entries are stored in
FewsNormSource.

2) Find out the location_id, parameter_id and optionally module_id. If
module_id is omitted, lines will be drawn from all modules. Examples:
location_id = 'ALM_237/1_Pomp-2', parameter_id = 'du.meting.omgezet2',
module_id = 'Productie'

3) Filter the Series object using this information::

    >>> filtered_series = Series.objects.using(db_name).filter(location__id=l_id, parameter__id=p_id)

4) Use the TimeSeries object to read the data::

    >>> from timeseries import timeseries
    >>> start = datetime.datetime.now() - datetime.timedelta(days=10)
    >>> end = datetime.datetime.now()
    >>> tsd = timeseries.TimeSeries.as_dict(filtered_series, start, end)

Read the events. The result is a dictionary with keys l_id, p_id::

    >>> tsd[l_id, p_id].events.items()


The event items area:
- key is timestamp
- value is 3-tuple with (value, flag, comment)

Note: if you loop through the event items, they do not appear on
timestamp order.
