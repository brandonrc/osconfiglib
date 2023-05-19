# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [0.1.6] - 2023-05-17

### Added
- Split the `apply_layers` function into `squash_layers`, `export_squashed_layer`, and `apply_squashed_layer` to allow for more flexibility in how layers are applied.
- Added `apply_squashed_layer` function to a new `virt_customize.py` module for better organization.
- Added enhanced error checking to squashed scripts, with comments indicating the origin of each script for easier debugging.

### Changed
- Updated `README.md` to reflect new function usage and include `virt_customize.py` in the imports.

### Fixed
- Scripts in squashed layers now include a leading `#!/bin/bash`.


