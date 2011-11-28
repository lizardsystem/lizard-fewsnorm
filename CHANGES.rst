Changelog of lizard-fewsnorm
===================================================


0.3 (unreleased)
----------------

- Fixed sync_fewsnorm after removing method FewsNormSource.o.

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
