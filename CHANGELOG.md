# Changelog

# [0.3.1] - 2025-09-09

### Changed

- [AISP-709] Timestamp changes (#98)
- Fix missing renaming for view to attribute group and entity to attribute key (#97)
- [AISP-733] Fix request to the /engines/publish endpoint after updating batch source to contain the attribute group that should be published (#96)

# [0.3.0] - 2025-09-08

### Changed

- [AISP-643] Rename Signals concepts (#94)

# [0.2.0] - 2025-09-01

### Changed

- Update models according to API 0.7 changes and add unpublish() and delete() functions (#90)
- [AISP-583] Interventions pub/sub support (#91)

# [0.1.5] - 2025-08-18

### Changed

- [AISP-685] Add PageView PagePing StructuredEvent wrappers.
- [AISP-684] Allow property wrappers for the property attribute on Attribute class.
- Fix root package export for AtomicProperty, EventProperty and EntityProperty.

# [0.1.4] - 2025-08-11

### Changed

- [AISP-571] Add new StreamView, BatchView and BatchDerivedView classes
- [AISP-532] Criterion new property classes and operator API
- [AISP-555] Typed test arguments
- [AISP-665] Add SDK version on headers
- [AISP-489] Add BigQuery autogen

## [0.1.3] - 2025-07-14

### Changed

- [AISP-566] Fix None attributes sent on API
- [AISP-566] Fix None attributes sent on API
- Remove prompts for now
- Run formatting on batch autogen files
- [AISP-396] Update function to retrieve attribute values

## [0.1.2] - 2025-06-26

### Changed

- [AISP-307] Allow custom entities
- [AISP-437] Use snowplow file (#62)
- [AISP-362] Interventions management in SDK (#64)
- [AISP-441] Filter batch views (#66)
- [AISP-525] Fix datamodel-codegen to work properly with python linters (#69)

## [0.1.1] - 2025-05-23

### Changed

- Fix entity name references in the retrieve attributes request

## [0.1.0] - 2025-05-23

### Changed

- [AISP-435] Slash API URL
- [AISP-348] Make owner required in views (#56)
- [AISP-310] Rename user and session entity to domain_userid and domain_sessionid and add user_id and network_userid (#57)
- Small fixes in the types (#60)

## [0.0.7] - 2025-05-14

### Changed

- Add unit testing for dbt transformations
- Address feedback from internal testing
- Add missing import
- Fix batch source timestamp columns
- Fix Service creation with multiple views (#58)

## [0.0.6] - 2025-04-25

### Changed

- Update models based on API version 0.2.5

## [0.0.5] - 2025-04-23

### Added

- Batch Engine with CLI support

## [0.0.4] - 2025-04-15

### Changed

- Updated README.md to reflect the current project status

## [0.0.3] - 2025-04-15

### Added

- Initial release of Snowplow Signals SDK

### Dependencies

- Python 3.11+ support
