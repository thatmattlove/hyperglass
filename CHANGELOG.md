# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2.0.4 - 2024-06-30

### Fixed

- [#264](https://github.com/thatmattlove/hyperglass/issues/264): Fixed issue where IPv6 traceroutes fail on Juniper devices due to `traceroute: wait must be >1 sec.` error. Thanks @renatoornelas!
- [#267](https://github.com/thatmattlove/hyperglass/issues/267): Fixed issue where responses were incorrectly cached, resulting in no data being shown in the AS Path viewer.
- [#268](https://github.com/thatmattlove/hyperglass/issues/268): Fixed issue where some Mikrotik commands failed to execute properly.
- [#269](https://github.com/thatmattlove/hyperglass/issues/269): Updated documentation regarding `structured.rpki.mode`.
- Removed unnecessary logging statements which caused logging errors.
- Fixed issue where validation of structured BGP route data may have failed under certain conditions.

### Changed
- Error responses are no longer cached.

## 2.0.3 - 2024-06-16

### Fixed

- [#262](https://github.com/thatmattlove/hyperglass/issues/262): Fix issue where Mikrotik output was improperly parsed and displayed an error as a result.
- Fixed issue where incorrect error styles were displayed.
- Fixed issue where 'results' accordion component did not re-open when closed.
- Fixed issue where pattern-based directive rules failed validation.

### Changed

- Set default logo width (back) to 50%, adjusted how the `web.logo.width` setting is handled in the UI.

## 2.0.2 - 2024-06-01

### Fixed

- [#257](https://github.com/thatmattlove/hyperglass/issues/257): Fix issue where if `web.location_display_mode` is set to `dropdown` (automatically or otherwise), the menu would remain open but become detached from the main element because the Query Type element came into view.
- [#253](https://github.com/thatmattlove/hyperglass/issues/253): _Actually_ fix issue where configuration values were improperly prepended with the `HYPERGLASS_APP_PATH` value.
- [#258](https://github.com/thatmattlove/hyperglass/issues/258): Center logo alignment on small screens.
- Fix broken license link in default credit menu.

### Added

- Added license to docs.
- [#254](https://github.com/thatmattlove/hyperglass/issues/254): Users may specify their own DNS over HTTPS provider if desired.

## 2.0.1 - 2024-05-31

### Fixed
- [#244](https://github.com/thatmattlove/hyperglass/issues/244): Fix issue with UI build where UI build directory already existed and therefore could not be created.
- [#249](https://github.com/thatmattlove/hyperglass/issues/249): Fix issue where configuration values were improperly prepended with the `HYPERGLASS_APP_PATH` value.
- [#251](https://github.com/thatmattlove/hyperglass/issues/251): Fix issue where browser-based DNS resolution did not show, causing FQDN queries to fail due to validation.
- Fix issue where logo was improperly sized on small screens.

## 2.0.0 - 2024-05-28

_v2.0.0 is a major release of hyperglass. Many things have changed, and it is likely best to redeploy hyperglass in a new environment to migrate to v2._

### Added

- Commands are now defined as [directives](https://hyperglass.dev/configuration/directives), which is a configuration definition of one or more commands to run on a device. A directive defines:
  - What command (or commands) to run on the device
  - Type of UI field, text input or select
  - If the field can accept multiple values
  - Help information to show about the directive
  - Validation rules
- hyperglass now supports Docker, and using Docker is the default and recommended method for deployment.
- The list of locations (devices) is displayed as a gallery when the number of devices is 5 or less. This is a default value and is configurable.
- hyperglass now supports custom [input or output plugins](https://hyperglass.dev/plugins).
  - Input Plugins: Apply custom validation logic or transform user input before the query is sent to a device.
  - Output Plugins: Interact with the output from a device before it's displayed to the user.
- [#206](https://github.com/thatmattlove/hyperglass/issues/206): OpenBGPD is natively supported by hyperglass.
- [#176](https://github.com/thatmattlove/hyperglass/issues/176): Custom javascript or HTML can be injected into the web page (for tracking applications such as Google Analytics).
- [#173](https://github.com/thatmattlove/hyperglass/issues/173): Any output, such as BGP Communities, can be highlighted in the UI by defining [highlight patterns](https://hyperglass.dev/configuration/config/web-ui#highlighting).
- [#155](https://github.com/thatmattlove/hyperglass/issues/155): A user can now use the "My IP" button to insert their own IP into the query target field.
- [#143](https://github.com/thatmattlove/hyperglass/issues/143): Any HTTP endpoint may be configured as device from which to collect output.

### Fixed
- [#229](https://github.com/thatmattlove/hyperglass/issues/229): Fixed an issue where the logo was not visible when using Firefox.
- [#180](https://github.com/thatmattlove/hyperglass/issues/180): Fixed an issue where certain FQDNs were considered invalid.
- [#178](https://github.com/thatmattlove/hyperglass/issues/178): Fixed an issue where parsing of Arista EOS routes failed if MED is unset.
- [#145](https://github.com/thatmattlove/hyperglass/issues/145): Fixed an issue where menu links were improperly generated.

## 1.0.4 - 2021-07-03

### Fixed
- [#148](https://github.com/thatmattlove/hyperglass/issues/148): Update Debian/Ubuntu Python package name in installer and documentation.
- [#151](https://github.com/thatmattlove/hyperglass/issues/151): Fix issue with Junos structured output parsing from d1160fe where hyperglass would always query both IPv4 and IPv6 for any query type.

### Changed
- Improve handling of Junos XML errors. When a Junos device returns an error in the XML output, it will be displayed in the UI.
- Improve `hyperglass system-info` output. NodeJS version is now included in the output.

## 1.0.3 - 2021-06-23

_1.0.3 is a cosmetic release to factor in code-level changes related to the repository name change from checktheroads to thatmattlove._

## 1.0.2 - 2021-06-18

### Fixed
- [#150](https://github.com/thatmattlove/hyperglass/issues/150): Fix handling of BIRD AS_PATH/Community targets.

## 1.0.1 - 2021-06-17

### Fixed
- UI: fix body overflow issue

## 1.0.0 - 2021-05-30

### BREAKING CHANGES
- The `external_link`, `help`, and `terms` parameters no longer exist and have been replaced with generic `links` and `menus` options.
- The transitionary `frr_ssh` and `bird_ssh` NOS parameters no longer exist — `frr` and `bird` can now be used for SSH-based connectivity. hyperglass-agent users must now use `frr_legacy` and `bird_legacy` until hyperglass-agent is fully deprecated.

### Fixed
- [#139](https://github.com/thatmattlove/hyperglass/issues/139): Fix an issue where the API cannot be queried by device name.

### Changed
- Updated UI dependencies

### Added
- [#140](https://github.com/thatmattlove/hyperglass/issues/140): Genericize links and menus so that multiple links and/or menus can be defined and fully customized.

## 1.0.0-beta.82 - 2021-04-22

### BREAKING CHANGE
**NodeJS 14.15 or later is required**. See [the docs](https://hyperglass.dev/docs/getting-started) for installation instructions.

### Fixed
- [#135](https://github.com/thatmattlove/hyperglass/issues/135): Fix an issue where Juniper indirect next-hops were empty.
- Fix an issue where Juniper structured AS_PATH or Community queries would appear to fail if one address family (IPv4 or IPv6) had an empty response. For example, if an AS_PATH query for `.* 29414 .*` was made (which only returns IPv4 routes), the query would fail.

### Changed
- Updated major Python dependencies (FastAPI, Scrapli, Netmiko, Pydantic, Uvicorn, Gunicorn, etc.)
- Updated UI dependencies
- [#128](https://github.com/thatmattlove/hyperglass/pull/128): Add `best` to all Juniper BGP Route queries. See [Juniper docs](https://www.juniper.net/documentation/us/en/software/junos/bgp/topics/ref/command/show-route-best.html) for more details.

### Added
- The driver for devices can now be overridden with the `driver` parameter.

## 1.0.0-beta.81 - 2021-04-10

### Fixed
- [#124](https://github.com/thatmattlove/hyperglass/issues/124): Fix an issue where networks weren't always sorted alphabetically.
- [#126](https://github.com/thatmattlove/hyperglass/issues/126): Fix rendering of markdown tables.
- [#132](https://github.com/thatmattlove/hyperglass/issues/132): Fix an issue where iBGP routes on Arista devices caused output parsing to fail.
- [#133](https://github.com/thatmattlove/hyperglass/issues/133): Use body styles for background/foreground color, allowing the user to override the `light` and `dark` colors per the docs.
- Fix an issue with select menu list style.

### 1.0.0-beta.80 - 2021-03-03

### Fixed
- Fix an issue where the UI did not properly filter and detect the correct Query VRF when only one was defined.
- [#121](https://github.com/thatmattlove/hyperglass/issues/121): Fix issue with select menu styling in light mode.

### 1.0.0-beta.79 - 2021-02-26

### BREAKING CHANGE
**Major changes have been made to how VRFs are defined and handled.** Previously, you would signal to hyperglass that a VRF was the "default" VRF (meaning, a VRF does not need to be specified in any commands) by setting `name: default` in the VRF block. This limitation meant that a VRF named `default` _had_ to be defined, and that any users who keep their global routing table in a non-default VRF must define it separately.

Moving forward, the `name` field is only used to define the name of the VRF **as known by the device**. To signal that hyperglass should use the device's default VRF, set `default: true` on the VRF. **This is not the default**.

### Fixed
- Fix an issue where long-running commands, such as traceroutes that never complete, time out and display an error instead of the output.

### Changed
- Don't do external RPKI lookups for non global unicast prefixes.
- Migrate to palette-by-numbers for theming.
- Update UI dependencies.

### 1.0.0-beta.78 - 2021-02-12

### Added
- Experimental table output/structured data support for Arista EOS.

### Fixed
- Corrected warning color on active routes in table output.

### Changed
- Caught fetch errors now display the HTTP status text in the UI, instead of the caught error message.

### 1.0.0-beta.77 - 2021-02-10

**POTENTIALLY BREAKING CHANGE**: The device `display_name` field is being deprecated, in favor of a single `name` field, which will be displayed to the end user. The `display_name` field still works, but you should migrate away from it as soon as possible.

### Fixed
- [#117](https://github.com/thatmattlove/hyperglass/issues/117): Fix naming and mapping of the Arista EOS driver. `arista` and `arista_eos` will both work now.

### Changed
- Removed `display_name` field from device model. The `name` field will be used in the UI. If a `display_name` is defined, it will be used, for backwards compatibility.

### 1.0.0-beta.76 - 2021-02-06

**NOTICE**: *[hyperglass-agent](https://github.com/thatmattlove/hyperglass-agent) will be deprecated soon. Use `frr_ssh` or `bird_ssh` for SSH connectivity in the meantime.*

### Added
- FRR & BIRD may now be accessed via standard SSH using the `frr_ssh` and `bird_ssh` NOS. [See the docs](https://hyperglass.dev/docs/platforms#caveats) for important caveats.

### Changed
- `port` in `devices.yaml` now defaults to 22 if not specified.

### Fixed
- AS Path graph view now uses [dagre](https://github.com/dagrejs/dagre) to properly arrange each AS.
- Added timeout argument to `hyperglass start --build` - fixes issue where running a UI build in this way failed due to a missing timeout argument error.

### 1.0.0-beta.75 - 2021-01-28

### Changed
- Default UI build timeout is now 180 seconds.
- The hyperglass `build-ui` CLI command now accepts a `--timeout` argument to override the UI build timeout.

### 1.0.0-beta.74 - 2021-01-25

### Changed
- The Scrapli driver no longer specifically ignores the system's SSH config file.
- Updated UI dependencies.

### Fixed
- [#109](https://github.com/thatmattlove/hyperglass/issues/109): Remove the custom error page, because it doesn't work and doesn't really add much.

### 1.0.0-beta.73 - 2021-01-18

### Added
- [#106](https://github.com/thatmattlove/hyperglass/issues/106): Add built-in support for Nokia SR OS (thanks @paunadeu!).

### Changed
- [#105](https://github.com/thatmattlove/hyperglass/issues/105): Check NodeJS version on startup to ensure the minimum supported version is present.
- Update UI dependencies.

### Fixed
- [#107](https://github.com/thatmattlove/hyperglass/issues/107): Fix footer menu styling so it doesn't overflow the viewport, especially on mobile.

### 1.0.0-beta.72 - 2021-01-16

### Fixed
- [#104](https://github.com/thatmattlove/hyperglass/issues/104): Handle the usage of `juniper_junos` as a NOS. `juniper_junos` will now automatically be mapped to `juniper`.
- Fix an issue with dual RP juniper devices and structured output, where output containing `{master}` outside of the XML output was improperly stripped out, causing a parsing failure.

### Changed
- **BREAKING**: The installer no longer generates a Systemd service file. While this was likely convenient for most, it introduced significant complexity and caused most installations using `~/hyperglass` as the app path to fail, with no clear way to resolve it. Further, while Systemd is arguably the most common, it is not the *only* process manager available. As such, the docs will be updated with a Systemd example, much like the current reverse proxy documentation.

### 1.0.0-beta.71 - 2021-01-10

### Added
- Added Google Analytics Support. Use the `google_analytics` field for the tracking ID in `hyperglass.yaml`.

### Changed
- Minor frontend code improvements.

### 1.0.0-beta.70 - 2021-01-05

### Fixed

- [#100](https://github.com/thatmattlove/hyperglass/issues/100): Fix result panel bug where incorrect panels would open, or panels would not open at all. Resolved by accessing internal state of the `Accordion />` component via `useAccordionContext()` instead of directly changing the index prop via state.

### Changed
- Query results now automatically cancel when each result panel unmounts (e.g. when one clicks the back button).

### 1.0.0-beta.69 - 2021-01-03

### Fixed

- Fix Safari browser-specific issues
- Setup no longer fails when `commands.yaml` doesn't exist, even though it isn't needed.

### Changed

- Setup no longer adds example files

### 1.0.0-beta.67 - 2021-01-02

### Fixed

- Fix handling of `web.theme.default_color_mode`. Starting in 1.0.0-beta.65, it was completely ignored and used the library's default of `light`. Now, it's handled properly.
- Fix table output layout issues, particularly on mobile.

### 1.0.0-beta.66 - 2021-01-02

### Fixed

- Fixed Safari browser-specific issues
- Fixed mobile layout issues

### Changed

- `web.theme.colors.black` and `web.theme.colors.white` are now `web.theme.colors.dark` and `web.theme.colors.light respectively`

### 1.0.0-beta.65 - 2021-01-01

### Added

- [#72](https://github.com/thatmattlove/hyperglass/issues/72): _EXPERIMENTAL_ BGP map support for devices supporting structured output (Juniper Junos, currently).

### Fixed

- Fix an issue causing Juniper Junos BGP output parsing to fail if the XML output contains a banner.

### Changed

- `web.text.title` and `web.text.subtitle` now carry a 32 character limit for simpler styling.
- Various UI layout, styling improvements, and stability improvements.

### 1.0.0-beta.63 - 2020-10-18

### Added

- [#87](https://github.com/thatmattlove/hyperglass/issues/87): [TNSR] Support. To add a TNSR device, use the `tnsr` [NOS key](https://hyperglass.dev/docs/adding-devices#all-device-parameters).

### Fixed

- Fix an issue causing hyperglass custom exceptions to not be properly raised, which caused more generic error messages in the UI/API.

### 1.0.0-beta.62 - 2020-10-17

### Fixed

- Fix an issue causing exceptions not to be logged to the log file (but logged to stdout).

### 1.0.0-beta.61 - 2020-10-11

### POTENTIALLY BREAKING CHANGE

When hyperglass starts up, it will check to see if `~/hyperglass` or `/etc/hyperglass/` exists. Previously, it would silently choose the first one found, even if both exist. Now, if both exist, an exception is raised with instruction to delete one of them. If your system has both directories, hyperglass may not start up normally after you upgrade.

### Fixed

- Fix a DNS resolution issue which caused Debian systems to be unable to resolve the hostnames of any devices. This was due to differences in how the Python socket module works on Debian vs other distros (even Ubuntu).

### Added

- [#81](https://github.com/thatmattlove/hyperglass/issues/81): Add support for SSH key authentication. See [the docs](https://hyperglass.dev/docs/adding-devices#credential) for more details.

### 1.0.0-beta.60 - 2020-10-10

### Fixed

- [#90](https://github.com/thatmattlove/hyperglass/issues/90): Fix a typing error that caused ping & traceroute queries to fail for certain devices.

### Added

- [#82](https://github.com/thatmattlove/hyperglass/issues/82): Add support for Redis password authentication. Authentication can be configured in the following manner:

```yaml
# hyperglass.yaml
cache:
  password: examplepassword
```

This would correspond with the following stanza in the Redis configuration file:

```
requirepass examplepassword
```

### 1.0.0-beta.59 - 2020-10-05

### Added

- Native Mikrotik support.
- `hyperglass clear-cache` command for easy manual clearing of the Redis cache.

### Changed

- Improve output parsing scalability - parsers can now be defined on a per-NOS basis regardless of whether or not structured-data is used.
- Restructure model locations & importing to remove some complexities.

### 1.0.0-beta.58 - 2020-09-28

### Changed

- [#79](https://github.com/thatmattlove/hyperglass/issues/79): Run the UI build on startup & clarify docs.
- Removed all f-strings from log messages.
- Migrate icon library to [@meronex/icons](https://github.com/meronex/meronex-icons) for better tree-shaking.
- Improve console (stdout) logging
- Fix file logging format

### Fixed

- [#74](https://github.com/thatmattlove/hyperglass/issues/74): Fix UI build failures caused by `.alias.js`.
- [#75](https://github.com/thatmattlove/hyperglass/issues/75): Fix whitespace stripping of query target.
- [#77](https://github.com/thatmattlove/hyperglass/issues/77): Allow dashes in FQDN validation pattern.
- [#83](https://github.com/thatmattlove/hyperglass/issues/83): Fix lack of support for `protocol-nh` field in Juniper XML BGP table.

### 1.0.0-beta.57 - 2020-07-30

### BREAKING CHANGE

If you use [hyperglass-agent](https://github.com/thatmattlove/hyperglass-agent), you must upgrade your version of hyperglass-agent to 0.1.6 or later. If using hyperglass-agent with SSL, this release will require you to re-generate & re-send your SSL certificates to hyperglass:

```console
$ hyperglass-agent certificate
$ hyperglass-agent send-certificate
```

### Changed

- Verify a device's address is either an IPv4 or IPv6 address, or a resolvable hostname.
- Devices using hyperglass-agent (FRR, BIRD) no longer need to use a DNS-resolvable hostname in the `address:` field, as long as the certificate has been generated by hyperglass-agent, and the proper IP addresses were selected during the prompts to generate the certificate. _If using your own certificate and you want to connect to hyperglass-agent via an IP address instead of a hostname, you need to ensure the IP address of hyperglass-agent is listed as a Subject Alternative Name in the certificate extensions._
- Refactored device, query, proxy models to no longer scrub unsupported characters from the device name for the purposes of Python class attribute accessing.
- Updated hyperglass-agent docs.

### 1.0.0-beta.56 - 2020-07-28

### Changed

- Improved Gunicorn address formatting.
- Improved Redis connection error handling.

### Fixed

- [#56](https://github.com/thatmattlove/hyperglass/issues/56): Fix a silent Redis connection error if the Redis server was anything other than `localhost`, preventing hyperglass from starting.

### 1.0.0-beta.55 - 2020-07-27

### Changed

- Removed JS favicon build process in favor of native Python implementation ([favicons](https://github/thatmattlove/favicons))

### 1.0.0-beta.54 - 2020-07-25

### Fixed

- Queries to hyperglass-agent devices failed due to the error `AttributeError: 'AgentConnection' object has no attribute 'collect'`

### 1.0.0-beta.53 - 2020-07-23

### Added

- **BREAKING CHANGE**: [Scrapli](https://github.com/carlmontanari/scrapli) is now used for SSH connectivity to Cisco IOS, Cisco IOS-XE, Cisco IOS-XR, Cisco NX-OS Juniper Junos, and Arista EOS, which should improve the speed at which output is gathered from devices. _As of this release, Cisco IOS/IOS-XE and Juniper Junos have been directly tested and worked without issue. However, if you discover any anomalies with any of these operating systems, please [open an issue](https://github.com/thatmattlove/hyperglass/issues)._

### Changed

- Refactor of SSH & HTTPS command execution to enable pluggable underlying driver capabilities.
- Remove `aiofile` dependency by removing unnecessary asyncio file operations in the UI build process.
- Added `scrapli[asyncssh]` dependency for Scrapli driver support.

### Fixed

- UI: Error messages couldn't be copied with the copy button

### 1.0.0-beta.52 - 2020-07-19

### Added

- API route `/api/info`, which displays general system information such as the name of the organization and version of hyperglass.
- API docs configuration parameters for the `/api/info` route.
- [#63](https://github.com/thatmattlove/hyperglass/issues/63): Minimum RAM requirements.
- `hyperglass system-info` CLI command to gather system CPU, Memory, Disk, Python Version, hyperglass Version, & OS info. _Note: this information is only gathered if you run the command, and even then, is printed to the console and not otherwise shared or exported_.

### Changed

- Updated docs dependencies.
- Improved YAML alias & anchor docs.
- [#55](https://github.com/thatmattlove/hyperglass/issues/55): Removed YAML alias & anchors from default examples to avoid confusion.

### Fixed

- API docs logo URL now displays correctly.
- [#62](https://github.com/thatmattlove/hyperglass/issues/62): Added `epel-release` to CentOS installation instructions.
- [#59](https://github.com/thatmattlove/hyperglass/issues/59): Fixed copy output for Juniper devices on non-table output query types.
- [hyperglass-agent #6](https://github.com/hyperglass-agent/issues/6): Fixed hyperglass-agent documentation issues.
- Improve command customization docs.
- [#61](https://github.com/thatmattlove/hyperglass/issues/61): Fixed copy output for table data. Output is now a bulleted list of parsed data.

### 1.0.0-beta.51 - 2020-07-13

### Changed

- Improved config import process & error handling.
- Improved logging initialization so that noisy logs aren't generated on startup unless debugging is enabled.

### Fixed

- [#54](https://github.com/thatmattlove/hyperglass/issues/54): A Junos parsing error caused routes with no communities to raise an error.
- Pre-validated config files are no longer logged on startup unless debugging is enabled.

### 1.0.0-beta.50 - 2020-07-12

### Added

- Synchronous API for Redis caching.
- New `redis-py` dependency for synchronous Redis communication.

### Changed

- Improved cache type conversion when reading cached data.
- External data via [bgp.tools](https://bgp.tools) is now gathered via their bulk mode API.
- External data via [bgp.tools](https://bgp.tools) is now cached via Redis to reduce external traffic and improve performance.
- RPKI validation via [Cloudflare](https://rpki.cloudflare.com/) is now cached via Redis to reduce external traffic and improve performance.
- Update Python dependencies.

### Fixed

- [#54](https://github.com/thatmattlove/hyperglass/issues/54): A Junos structured/table output parsing error caused routes with multiple next-hops to raise an error.
- RPKI validation no longer occurs twice (once on serialization of the output, once on validation of the API response).

### 1.0.0-beta.49 - 2020-07-05

### Changed

- Update UI dependencies
- Removed react-textfit in favor of responsive font sizes and line breaking
- Refactor & clean up React components

### Fixed

- Route lookups for private (RFC 1918) addresses failed due to an unnecessary lookup to [bgp.tools](https://bgp.tools)

### 1.0.0-beta.48 - 2020-07-04

### Added

- New NOS: **VyOS**. [See docs for important caveats](https://hyperglass.dev/docs/commands).

### Fixed

- UI: If the logo `width` parameter was set to ~ 50% and the `title_mode` was set to `logo_subtitle`, the subtitle would appear next to the logo instead of underneath.
- When copying the opengraph image, the copied image was not deleted.
- Default traceroute help link now _actually_ points to the new docs site.

### 1.0.0-beta.47 - 2020-07-04

### Added

- Opengraph images are now automatically generated in the correct format from any valid image file.
- Better color mode toggle icons (they now match [hyperglass.dev](https://hyperglass.dev)).

### Changed

- Improved SEO & Accessibility for UI.
- Default traceroute help link now points to new docs site.
- Slightly different default black & white colors (they now match [hyperglass.dev](https://hyperglass.dev)).
- Various docs site improvements

### Fixed

- Remove `platform.linux_distribution()` which was removed in Python 3.8
- Width of page is no longer askew when `logo_subtitle` is set as the `title_mode`
- Generated favicon manifest files now go to the correct directory.
- Various docs site fixes

### 1.0.0-beta.46 - 2020-06-28

### Added

- Support for hyperglass-agent [0.1.5](https://github.com/thatmattlove/hyperglass-agent)

### 1.0.0-beta.45 - 2020-06-27

### Changed

- Removed RIPEStat for external data gathering, switched to [bgp.tools](https://bgp.tools)

### Fixed

- Webhook construction bugs that caused webhooks not to send
- Empty response handling for table output

### 1.0.0-beta.44 - 2020-06-26

### Added

- Support for Microsoft Teams webhook

### Fixed

- If webhooks were enabled, a hung test connection to RIPEStat would cause the query to time out

### 1.0.0-beta.43 - 2020-06-22

### Fixed

- Logo path handling in UI

### 1.0.0-beta.42 - 2020-06-21

### Added

- Automatic favicon generation

### Changed

- **BREAKING CHANGE**: The `logo` section now requires the full path for logo files. See [the docs](https://hyperglass.dev/docs/ui/logo) for details.
