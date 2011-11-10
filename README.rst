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

TODO: edit this paragraph( from all
fews norm databases are synchronized into a single (django-) database
for quick searching through multiple sources.)

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

In practice, you need synchronize regularly.

To sync your locations::

    $> bin/django synchronize_geo_location_cache --user_name=<django user name>


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
