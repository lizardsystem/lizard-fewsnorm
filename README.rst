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


Usage
-----

Multiple fews norm databases can be configured in
FewsNormSource. Locations, parameters and moduleinstances from all
fews norm databases are synchronized into a single (django-) database
for quick searching through multiple sources.

To sync your locations::

    $> bin/django synchronize_geo_location_cache --source=fewsnorm --user=buildout


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
