Changelog of lizard-fewsnorm
===================================================


0.9 (unreleased)
----------------

- Added QualifierSetCache.

- Added 'active' to model admin screens, so you can delete inactive
  objects easily.


0.8 (2012-02-01)
----------------

- Load and dump using natural keys now works.


0.7.1 (2012-01-31)
------------------

- Fixed bug in option sync_fewsnorm.


0.7 (2012-01-31)
----------------

- Improved sync_fewsnorm: All objects are updated and objects not in
  the source are set to inactive. Before, it deleted all entries
  and re-inserts them.

- Added lizard_security.

- Created tasks.py to run sync_fewsnorm from celery.

- Added natural key functions to all cache objects. They are used when
  you use dumpdata with the natural option. They cannot be loaded
  yet.


0.6 (2011-12-09)
----------------

- Added fixed filter functionality with fixed parameter for timeserie selection api


0.5.1 (2011-12-08)
------------------

- Nothing changed yet.


0.5 (2011-12-08)
----------------

- Added TimeSeriesCache function get_latest_event and get_timeseries.


0.4 (2011-11-29)
----------------

- Added schema prefix for fewsnorm sources. Note that all sources
  should have the same prefix. Not a problem for now, but later this
  can be an issue.


0.3 (2011-11-28)
----------------

- Fixed sync_fewsnorm after removing method FewsNormSource.o.

- Extended return string of get() in TimeserieSelectionView.

- Added timeseries api view (displays timeseries as json events).


0.2 (2011-11-16)
----------------

- Renamed management command. Changed options.

- Added ordering to some models.

- Added module_id to identifier in adapter.

- Fixed graphs after renaming.

- Renamed Series.aggregationperiody to aggregationperiod.

- Fixed adapter.layer, some models were changed.

- Pylint.

- Renamed model names.


0.1 (2011-11-07)
----------------

- Added extra horizontal lines for bar charts.

- Activated layout_extra parameter in image(..).

- Edited image to plot bar charts only for equidistant timeseries.

- Started experimental REST API.

- Implemented adapter functions search, location, image.

- Added migrations.

- Added management command to sync. locations.

- Added models for FEWSNORM database.

- Added models for FewsNormSource, GeoLocationCache, ParameterCache,
  ModuleCache.

- Initial library skeleton created by nensskel.  [Jack Ha]
