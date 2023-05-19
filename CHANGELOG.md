# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [0.1.6] - 2023-05-18

### Added
- Split the `apply_layers` function into `squash_layers`, `export_squashed_layer`, and `apply_squashed_layer` to allow for more flexibility in how layers are applied.
- Added `apply_squashed_layer` function to a new `virt_customize.py` module for better organization.
- Added enhanced error checking to squashed scripts, with comments indicating the origin of each script for easier debugging.
- Implemented a new function for validating and cloning a Git repository URL. The function checks if the URL is valid, attempts to clone the repository from the specified branch (or defaults to 'master' if the branch is not found), and verifies if the cloned repository follows the correct layer file structure. If the repository is invalid, the function deletes the locally cloned folder and returns a failure status.
- Added a new function `delete_layer_if_invalid` which checks if a given layer directory follows the required structure. If the layer is found to be invalid, it is automatically deleted from the local system to maintain cleanliness and structure compliance. This function returns a boolean indicating whether a layer was deleted or not.
- Implemented `toml_check` helper function to ensure the TOML file has at least one 'layers' key before starting the import process.
- Implemented `toml_export` function to parse a TOML file and export a squashed layer.
- Implemented `toml_apply` function to parse a TOML file and apply a squashed layer to a base image using virt-customize.

### Changed
- Updated `README.md` to reflect new function usage and include `virt_customize.py` in the imports.

### Fixed
- Scripts in squashed layers now include a leading `#!/bin/bash`.
- Fixed an issue where the layer import process would fail silently if the git repository or the local cache directory did not exist.
- Fixed an issue where the layer import process would continue even if a layer import failed. The import process will now stop and warn the user if a layer import fails.
- Updated the layer import process to support git layers. The layer import process will now clone the git repository into the local cache directory.
- Updated the layer import process to support local layers. The import process will now skip layers that are already in the local cache.


