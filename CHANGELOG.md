# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0-beta50 - 2020-07-12
### Fixed
- [#54](https://github.com/checktheroads/hyperglass/issues/54): A Junos structured/table output parsing error caused routes with multiple next-hops to raise an error.
- RPKI validation no longer occurs twice (once on serialization of the output, once on validation of the API response).

### Changed
- Improved cache type conversion when reading cached data.
- External data via [bgp.tools](https://bgp.tools) is now gathered via their bulk mode API.
- External data via [bgp.tools](https://bgp.tools) is now cached via Redis to reduce external traffic and improve performance.
- RPKI validation via [Cloudflare](https://rpki.cloudflare.com/) is now cached via Redis to reduce external traffic and improve performance.
- Update Python dependencies.
  
### Added
- Synchronous API for Redis caching.
- New `redis-py` dependency for synchronous Redis communication.

## 1.0.0-beta49 - 2020-07-05
### Fixed
- Route lookups for private (RFC 1918) addresses failed due to an unnecessary lookup to [bgp.tools](https://bgp.tools)

### Changed
- Update UI dependencies
- Removed react-textfit in favor of responsive font sizes and line breaking
- Refactor & clean up React components

## 1.0.0-beta48 - 2020-07-04

### Added
- New NOS: **VyOS**. [See docs for important caveats](https://hyperglass.io/docs/commands).

### Fixed
- UI: If the logo `width` parameter was set to ~ 50% and the `title_mode` was set to `logo_subtitle`, the subtitle would appear next to the logo instead of underneath.
- When copying the opengraph image, the copied image was not deleted.
- Default traceroute help link now *actually* points to the new docs site.

## 1.0.0-beta47 - 2020-07-04
### Added
- Opengraph images are now automatically generated in the correct format from any valid image file.
- Better color mode toggle icons (they now match [hyperglass.io](https://hyperglass.io)).

### Changed
- Improved SEO & Accessibility for UI.
- Default traceroute help link now points to new docs site.
- Slightly different default black & white colors (they now match [hyperglass.io](https://hyperglass.io)).
- Various docs site improvements

### Fixed
- Remove `platform.linux_distribution()` which was removed in Python 3.8
- Width of page is no longer askew when `logo_subtitle` is set as the `title_mode`
- Generated favicon manifest files now go to the correct directory.
- Various docs site fixes

## 1.0.0-beta46 - 2020-06-28

### Added
- Support for hyperglass-agent [0.1.5](https://github.com/checktheroads/hyperglass-agent)

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
