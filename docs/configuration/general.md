From `hyperglass/hyperglass/config/config.toml`:

### primary_asn

| Type   | Default Value |
| ------ | ------------- |
| String | `"65000"`       |

Your network's _primary_ ASN. Number only, e.g. `65000`, **not** `AS65000`.

### debug

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `False`         |

Enables Flask debugging. May be used to enable other module debugs in the future.

### google_analytics

| Type   | Default Value |
| ------ | ------------- |
| String | None          |

Google Analytics ID number. For more information on how to set up Google Analytics, see [here](https://support.google.com/analytics/answer/1008080?hl=en).

### message_error

| Type   | Default Value         |
| ------ | --------------------- |
| String | `"{input} is invalid."` |

Message presented to the user when invalid input is detected. `{input}` will be formatted as the input received from the main search field. For each command, input is validated via regular expression in the following patterns:

| Command       | Pattern                                      |
| ------------- | -------------------------------------------- |
| BGP Route     | Valid IPv4 or IPv6 Address                   |
| BGP Community | Valid new-format, 32 bit, or large community |
| BGP AS Path   | Any pattern                                  |
| Ping          | Valid IPv4 or IPv6 Address                   |
| Traceroute    | Valid IPv4 or IPv6 Address                   |

!!! note
    The BGP AS Path command currently allows `(.*)` to be submitted to the end device. Obviously, the device itself will return an error for garbage input, but ideally this would be "locked down" further. If you have an idea for a regex pattern to validate an `AS_PATH` regex, please submit a PR.

### message_blacklist

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"{input} is not allowed."` |

Message presented to the user when an IPv4 or IPv6 address matches the `blacklist.toml` array. `{input}` will be formatted as the input received from the main search field. For information on how this works, please see the [blacklist documentation](/configuration/blacklist).

### message_rate_limit_query

| Type   | Default Value                                                                                |
| ------ | -------------------------------------------------------------------------------------------- |
| String | `"Query limit of {rate_limit_query} per minute reached. Please wait one minute and try again."` |

Message presented to the user when the [query limit](#rate_limit_query) is reached. `{rate_limit_query}` will be formatted as the [`rate_limit_query`](#rate_limit_query) parameter. For information on how this works, please see the [rate limiting documentation](/ratelimiting/query).

### enable_bgp_route

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`          |

Enables or disables the BGP Route query type.

### enable_bgp_community

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`          |

Enables or disables the BGP Community query type.

### enable_bgp_aspath

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`          |

Enables or disables the BGP AS Path query type.

### enable_ping

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`          |

Enables or disables the Ping query type.

### enable_traceroute

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`          |

Enables or disables the Traceroute query type.

### rate_limit_query

| Type    | Default Value |
| ------- | ------------- |
| String  | `"5"`           |

Sets the number of queries **per minute** allowed by `remote_address` of the request. For information on how this works, please see the [rate limiting documentation](/ratelimiting/query).

### rate_limit_site

| Type    | Default Value |
| ------- | ------------- |
| String  | `"120"`         |

Sets the number of site loads **per minute** allowed by `remote_address` of the request. For information on how this works, please see the [rate limiting documentation](/ratelimiting/site).

### cache_timeout

| Type     | Default Value |
| -------- | ------------- |
| Integer  | `120`           |

Sets the number of **seconds** to cache the back-end response. For information on how this works, please see the [caching documentation](/caching).

### cache_directory

| Type     | Default Value                        |
| -------- | ------------------------------------ |
| String   | `"hyperglass/hyperglass/.flask_cache"` |

Sets the directory where the back-end responses are cached. For information on how this works, please see the [caching documentation](/caching).
