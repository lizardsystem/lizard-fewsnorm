Changelog of lizard-fewsnorm
===================================================


0.22.1 (unreleased)
--------------

- Add part of faster sync_aqmad method.

- Added a commet to time_series method of Event model.

- Pep8 corrections.

- Pinned kgs 3.1.20 due djangorestframework update. 


0.22.1 (2012-06-11)
-------------------

- Remove list function around raw query in sync_fewsnorm.


0.22 (2012-06-11)
-----------------

- Rewrite sync_time_series_cache to sync timeseries on a per-parameter basis,
  to reduce memory consumption.


0.21 (2012-06-04)
-----------------

- Fix bug in sync_aqmad crashing on out-of-sync timeseries.


0.20 (2012-05-31)
-----------------

- Add aqmad caching.


0.19 (2012-05-29)
-----------------

- Fix trackrecords synchronization


0.18 (2012-05-09)
-----------------

- Added tasks.py for celery.

- Added data_set to FewsNormSource to make syncing with data sets
  easier.

- Updated sync_fewsnorm.


0.17 (2012-04-24)
-----------------

- Added aggregation for quarter of year. Event.agg_from_raw.


0.16 (2012-04-23)
-----------------

- Changed behaviour of Event.time_series. The keys of time series are
  now 3-tuples (location, parameter, unit) instead of 2-tuples.

- Started to fix sync_track_records (but unfinished).


0.15 (2012-04-19)
-----------------

- Added related_location and ident option to Location.

- Fixed Event.__unicode__.


0.14 (2012-04-16)
-----------------

- Fixed Event.filter_latest_before_deadline,
  TimeSeriesCache.get_latest_event, TimeSeriesCache.get_timeseries.

- Removed TimeSeriesComments, it is integrated in Event.

- Removed Qualifiers, it is integrated in QualifierSets.

- Commented out TimeseriesManualEditsHistory, unused.

- Commented out AggregationPeriods, unused.

- Work towards fix for sync_track_record_cache method of FewsNormSource.


0.13 (2012-04-12)
-----------------

- Changed behaviour of Event, Series (all apps that depend on these
  models should be upgraded).

- Added support for different schemas.

- Updated sync_fewsnorm, memory usage and performance is now
  acceptable for 300k timeseries (test set for now).

- Added some fields to GeoLocationCache in admin.

- Added Event.agg_from_raw: aggregate using raw query.


0.12 (2012-03-28)
-----------------

- Added with_comments option in TimeSeriesCache.get_latest_event.


0.11 (2012-03-22)
-----------------

- Renamed TimeseriesComments.comments to comment.


0.10 (2012-03-22)
-----------------

- Added fields to TimeSeriesCache admin screen.

- Removed locations columns (Deltares removed these columns):
    #relationalocationid = models.CharField(max_length=64)
    #relationblocationid = models.CharField(max_length=64)
    #attributea = models.CharField(max_length=64)
    #attributeb = models.FloatField()


0.9.4 (2012-03-05)
------------------

- Add model for track records

- Add method to fewsnormsourcemodel for syncing track records

- Add management command for syncing track records



0.9.3 (2012-03-01)
------------------

- Add fields name and shortname to parameter cache and
  adjust sync_fewsnorm management command accordingly.


0.9.2 (2012-02-13)
------------------

- Fixed help string in 'sync_fewsnorm' management command.


0.9.1 (2012-02-07)
------------------

- Fixed sync_fewsnorm bug get_or_create.

- Added transaction.commit_on_success.


0.9 (2012-02-02)
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
