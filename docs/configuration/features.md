From `hyperglass/hyperglass/configuration/configuration.toml` `[features]`table.

`[features]`

## Rate Limiting
##### `[features.rate_limit.query]`

#### Query

Configuration paramters for rate limiting the number of queries per visitor. For information on how this works, please see the [rate limiting documentation](/ratelimiting/#query).

##### `rate`

| Type    | Default Value |
| ------- | ------------- |
| Integer | `5`           |

Sets the number of queries **per minute** allowed from the remote IP address of the request.

##### `period`

| Type   | Default Value |
| -------| ------------- |
| String | `"minute"`    |

Sets the time period to which `rate` applies.

##### `message`

| Type   | Default Value                                                                         |
| ------ | ------------------------------------------------------------------------------------- |
| String | `"Query limit of {rate} per minute reached. Please wait one {period} and try again."` |

Message presented to the user when the [query limit](#rate_limit_query) is reached. `{rate_limit_query}` will be formatted as the [`rate_limit_query`](#rate_limit_query) parameter.

#### Site
`[features.rate_limit.site]`

Configuration parameters for rate limiting the number of site visits per visitor. For information on how this works, please see the [rate limiting documentation](/ratelimiting/#site).

##### `rate`

| Type    | Default Value |
| ------- | ------------- |
| Integer | `60`          |

Sets the number of site visits allowed from the remote IP address of the request during the configured [period](#period) below.

##### `period`

| Type   | Default Value |
| -------| ------------- |
| String | `"minute"`    |

Sets the time period to which `rate` applies.

##### `title`

| Type   | Default Value     |
| ------ | ----------------- |
| String | `"Limit Reached"` |

Title text on Rate Limit error page.

##### `subtitle`

| Type   | Default Value                                                                |
| ------ | ---------------------------------------------------------------------------- |
| String | `"You have accessed this site more than {rate} times in the last {period}."` |

Subtitle text on Rate Limit error page.

## Caching
`[features.cache]`

For information on how this works, please see the [caching documentation](/caching).

##### `timeout`

| Type    | Default Value |
| ------- | ------------- |
| Integer | `120`         |

Sets the number of **seconds** to cache the back-end response.

##### `directory`

| Type   | Default Value                          |
| ------ | -------------------------------------- |
| String | `"hyperglass/hyperglass/.flask_cache"` |

Sets the directory where the back-end responses are cached. `hyperglass/hyperglass/.flask_cache` is excluded from change control.

!!! note "Permissions"
    The user hyperglass runs as must have permissions to this directory.

##### `show_text`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

If `true`, a message will be displayed at the bottom of the results box:

> Results will be cached for {seconds / 60} minutes.

##### `text`

| Type   | Default Value                                         |
| ------ | ----------------------------------------------------- |
| String | `"Results will be cached for {seconds / 60} minutes"` |

Sets the caching message text if `show_text` is `true`.

## Maximum Prefix Length
##### `[features.max_prefix]`

##### `enable`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `false`       |

Enables or disables a maximum allowed prefix size for BGP Route queries. If enabled, the prefix length of BGP Route queries must be shorter than the `max_prefix_length_ipv4` and `max_prefix_length_ipv6` parameters. For example, a BGP Route query for `192.0.2.0/25` would result in the following error message:

<img src="/max_prefix_error.png" style="width: 70%"></img>

##### `ipv4`

| Type    | Default Value |
| ------- | ------------- |
| Integer | `24`          |

If `enable` is `true`, sets the maxiumum prefix length allowed for IPv4 BGP Route queries.

##### `ipv6`

| Type    | Default Value |
| ------- | ------------- |
| Integer | `64`          |

If `enable` is `true`, sets the maxiumum prefix length allowed for IPv6 BGP Route queries.

## BGP Route
##### `[features.bgp_route]`

##### `enable`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables the BGP Route query type.

## BGP Community
##### `[features.bgp_community]`

##### `enable`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables the BGP Community query type.

#### Regex
##### `[features.bgp_community.regex]`

Override the default regex patterns for validating BGP Community input.

##### `decimal`

| Type   | Default Value     |
| ------ | ----------------- |
| String | `"^[0-9]{1,10}$"` |

Decimal/32 bit community format.

##### `extended_as`

| Type   | Default Value                    |
| ------ | -------------------------------- |
| String | `"^([0-9]{0,5})\:([0-9]{1,5})$"` |

Extended community format

##### `large`

| Type   | Default Value                                   |
| ------ | ----------------------------------------------- |
| String | `"^([0-9]{1,10})\:([0-9]{1,10})\:[0-9]{1,10}$"` |

Large community format

## BGP AS Path
##### `[features.bgp_aspath]`

##### `enable`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables the BGP AS Path query type.

#### Regex
##### `[features.bgp_aspath.regex]`

##### `mode`

| Type   | Default Value |
| ------ | ------------- |
| String | `"asplain"`   |

Sets the AS Path type used **network-wide**. Options are `asplain`, `asdot`. For more information on what these options mean, [click here](https://tools.ietf.org/html/rfc5396).

!!! warning "AS_PATH Format"
    This pattern will be used to validate AS_PATH queries to your routers, so it should match how your routers are actually configured.

##### `asplain`

| Type   | Default Value                                |
| ------ | -------------------------------------------- |
| String | `"^(\^|^\_)(\d+\_|\d+\$|\d+\(\_\.\+\_\))+$"` |

Regex pattern used to validate `asplain` formatted AS numbers in an AS_PATH. Only used if `mode` is set to `asplain.`

##### `asdot`

| Type   | Default Value                                                     |
| ------ | ----------------------------------------------------------------- |
| String | `"^(\^|^\_)((\d+\.\d+)\_|(\d+\.\d+)\$|(\d+\.\d+)\(\_\.\+\_\))+$"` |

Regex pattern used to validate `asdot` formatted AS numbers in an AS_PATH. Only used if `mode` is set to `asdot.`

## Ping
##### `[features.ping]`

##### `enable`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables the Ping query type.

## Traceroute
##### `[features.traceroute]`

##### `enable`

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables the Traceroute query type.
