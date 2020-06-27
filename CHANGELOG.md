# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0-beta45 - 2020-06-27

### Fixed
- Webhook construction bugs that caused webhooks not to send
- Empty response handling for table output

### Changed
- Removed RIPEStat for external data gathering, switched to [bgp.tools](https://bgp.tools)

## 1.0.0-beta44 - 2020-06-26

### Added
- Support for Microsoft Teams webhook

### Fixed
- If webhooks were enabled, a hung test connection to RIPEStat would cause the query to time out

## 1.0.0-beta43 - 2020-06-22

### Fixed
- Logo path handling in UI

## 1.0.0-beta42 - 2020-06-21

### Added
- Automatic favicon generation

### Changed
- **BREAKING CHANGE**: The `logo` section now requires the full path for logo files. See [the docs](https://hyperglass.io/docs/ui/logo) for details.
