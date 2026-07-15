# Changelog

## [unreleased]
- Change name instances of "Nexus Mod Archive" to "Nexus Archive"
- Add randomizer
- Add custom seed control
- Change user app_config.json to TOML format
- Change config validation dialogs to be more user-friendly and understandable
- Add skip and GUI notification for size errors raised from _check_size_limits() in `mod_archive_installer.py` (currently terminates app)
- Orchestrate state changes (like prune_orphaned_mods() in `mod_service.py`) from a higher place (such as `app_initializer.py`).
  They are currently difficult to locate and troubleshoot.
- Add proper logging to all modules.

## [1.0.0-alpha.7]
### Added
- Added logic to `mod_service.py` for removing broken symlinks at runtime
- Refactored `mod_archive_installer.py` to be more thread-friendly and provide better progress feedback

## [1.0.0-alpha.6]
### Added
- Uninstall wiring to `main_window.py`
- Mod display sync and uninstall logic to `mod_service.py`

## [1.0.0-alpha.5]
### Added
- Layered config service that merges base configs with user-customized overlay configs
- User config files and directories will now automatically create themselves if missing
- JSON config source abstraction for loading and saving config data
- Mod registry for storing loaded mods, with search filters and framework for identifying deployed/orphaned/foreign mod groups
- Config validation dialog to fix invalid config fields interactively instead of crashing on startup

### Changed
- Reworked the config layer, replacing the single-file config service with layered config services and sources
- Moved startup procedures into a setup step (`app_setup.py`)
- Renamed the Nexus Index to the Nexus Mod Archive
- Clarified regex pattern key names for mod paths and Nexus metadata
- Bumped version to 1.0.0-alpha.5

### Removed
- Obsolete dev scripts (`resolve_config.py`, `nexus_index.py`, `mhw_dir_validator.py`, `mod_item_model_yuki.py`)


## [1.0.0-alpha.3]
### Changed
- Updated CHANGELOG and README

### Added
- Consolodated convenience scripts into start_mgr
    - Added menu
    - Added automatic git fetch and pull for development branch

## [1.0.0-alpha.1]
### Changed
- Updated CHANGELOG and README
- Refactored main window design, added placeholder content to pages

### Added
- Convenience scripts for venv setup and app startup (Windows/Linux)

### Fixed
- Browse dialog showing previous browse location in setup wizard
- Corrupt config crashing app on startup
