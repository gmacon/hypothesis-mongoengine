# Version 2.0.0 - TBD

The code has been cleaned up to support newer versions of Hypothesis and Mongoengine.

## Breaking Changes

* The `field_strat` decorator has been renamed to `field_strategy`.
* In the `documents` strategy,
  explicitly passing `None` for a field
  no longer triggers the automatic strategy generation.
  Either omit the field or directly use the `field_values` strategy.
