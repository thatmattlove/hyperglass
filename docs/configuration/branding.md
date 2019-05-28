<style>
.bd-color {
    border-radius: 1px;
    box-shadow: 0 1px 2px 0 rgba(0,0,0,.1), inset 0 0 0 1px rgba(0,0,0,.1);
    display: inline-block;
    float: left;
    height: 16px;
    margin-right: 2px;
    width: 16px;
}
</style>

From `hyperglass/hyperglass/configuration/configuration.toml` `[branding]` table.

# Site Parameters
#### site_title

| Type   | Default Value  |
| ------ | -------------- |
| String | `"hyperglass"` |

HTML `<title>` element that is shown in a browser's title bar.

#### title_mode

| Type   | Default Value |
| ------ | ------------- |
| String | `"none"`      |

Controls the title section on the main page.

- `"none"` Hides Title and Subtitle text, displays logo defined in [logo_path](#logo_path).
- `"both"` Displays both Title and Subtitle text defined in [title](#title) and [subtitle](#subtitle) parameters.
- `"hide_subtitle"` Displays only the Title text defined in the [title](#title) parameter.

#### title

| Type   | Default Value  |
| ------ | -------------- |
| String | `"hyperglass"` |

#### subtitle

| Type   | Default Value        |
| ------ | -------------------- |
| String | `"AS" + primary_asn` |

See [primary_asn](#primary_asn) parameter.

#### enable_footer

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`        |

Enables or disables entire footer element, which contains text defined in `hyperglass/hyperglass/render/templates/footer.md`.

#### enable_credit

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`        |

Enables or disables hoverable icon on the left side of the footer, which links to the hyperglass repo.

#### show_peeringdb

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `True`        |

Enables or disables the PeeringDB link in the upper right corner. If `True`, the [primary_asn](#primary_asn) will be automatically used to create the URL to your ASN's PeeringDB entry.

# Colors

#### color_btn_submit

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#40798c"`   | <span class="bd-color" style="background-color: #40798c;"></span> |

Sets color of the submit button.

#### color_tag_loctitle

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#330036"`   | <span class="bd-color" style="background-color: #330036;"></span> |

Sets color of the title portion of the location tag which appears at the top of the results box on the left side.

#### color_tag_cmdtitle

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#330036"`   | <span class="bd-color" style="background-color: #330036;"></span> |

Sets color of the title portion of the command tag which appears at the top of the results box on the right side.

#### color_tag_cmd

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#ff5e5b"`   | <span class="bd-color" style="background-color: #ff5e5b;"></span> |

Sets color of the command name portion of the command tag which appears at the top of the results box on the right side.

#### color_tag_loc

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#40798c"`   | <span class="bd-color" style="background-color: #40798c;"></span> |

Sets color of the location name portion of the location tag which appears at the top of the results box on the left side.

#### color_bg

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#fbfffe"`   | <span class="bd-color" style="background-color: #fbfffe;"></span> |

Sets the background color of the main page.

#### color_progressbar

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#40798c"`   | <span class="bd-color" style="background-color: #40798c;"></span> |

Sets color of the progress bar that displays while the back-end application processes the request.

# Logo

#### logo_path

| Type   | Default Value                         |
| ------ | ------------------------------------- |
| String | `"static/images/hyperglass-dark.png"` |

Sets the path to the logo file, which will be displayed if [title_mode](#title_mode) is set to `"logo_only"`. This file can be any browser-compatible format, such as JPEG, PNG, or SVG.

#### logo_width

| Type   | Default Value |
| ------ | ------------- |
| String | `"384"`       |

Sets the width of the logo defined in the [logo_path](#logo_path) parameter. This is helpful if your logo is a dimension that doesn't quite work with the default width.

# UI Text

#### placeholder_prefix

| Type   | Default Value                         |
| ------ | ------------------------------------- |
| String | `"Prefix, IP, Community, or AS_PATH"` |

Sets the placeholder text that appears in the main search box.

#### text_results

| Type   | Default Value |
| ------ | ------------- |
| String | `"Results"`   |

Sets the header text of the results box.

#### text_location

| Type   | Default Value |
| ------ | ------------- |
| String | `"Location"`  |

Sets the placeholder text of the location selector.

#### text_cache

| Type   | Default Value                                           |
| ------ | ------------------------------------------------------- |
| String | `"Results will be cached for {cache_timeout} minutes."` |

Sets the text at the bottom of the results box that states the cache timeout. `{cache_timeout}` will be formatted with the value of [cache_timeout](/configuration/general/#cache_timeout).

#### text_limiter_title

| Type   | Default Value     |
| ------ | ----------------- |
| String | `"Limit Reached"` |

Sets the title text for the site-wide rate limit page. Users are redirected to this page when they have accessed the site more than the [specified](/configuration/general/#rate_limit_site) limit.

#### text_limiter_subtitle

| Type   | Default Value                                                                         |
| ------ | ------------------------------------------------------------------------------------- |
| String | `"You have accessed this site more than {rate_limit_site} times in the last minute."` |

Sets the subtitle text for the site-wide rate limit page. Users are redirected to this page when they have accessed the site more than the [specified](/configuration/general/#rate_limit_site) limit. `{rate_limit_site}` will be formatted with the value of [rate_limit_site](/configuration/general/#rate_limit_site).

#### text_500_title

| Type   | Default Value     |
| ------ | ----------------- |
| String | `"Error"`         |

Sets the title text for the full general error page.

#### text_500_subtitle

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"Something went wrong."` |

Sets the subtitle text for the full general error page.

#### text_500_button

| Type   | Default Value     |
| ------ | ----------------- |
| String | `"Home"`          |

Sets the button text for the full general error page.

#### text_help_bgp_route

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"Performs BGP table lookup based on IPv4/IPv6 prefix."` |

Sets the BGP Route query help text, displayed when the **?** icon is hovered.

#### text_help_bgp_community

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `'Performs BGP table lookup based on <a href="https://tools.ietf.org/html/rfc4360">Extended</a> or <a href="https://tools.ietf.org/html/rfc8195">Large</a> community value.'` |

Sets the BGP Community query help text, displayed when the **?** icon is hovered.

!!! note
    Since there are double quotes (`" "`) in the `<a>` HTML tags, single quotes (`' '`) are required for the TOML string.

#### text_help_bgp_aspath

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `'Performs BGP table lookup based on <code>AS_PATH</code> regular expression.<br>For commonly used BGP regular expressions, <a href="https://hyperglass.readthedocs.io/en/latest/Extras/common_as_path_regex/">click here</a>.'` |

Sets the BGP AS Path query help text, displayed when the **?** icon is hovered.

!!! note
    Since there are double quotes (`" "`) in the `<a>` HTML tags, single quotes (`' '`) are required for the TOML string.

#### text_help_ping

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"Sends 5 ICMP echo requests to the target."` |

Sets the Ping query help text, displayed when the **?** icon is hovered.

#### text_help_traceroute

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `'Performs UDP Based traceroute to the target.<br>For information about how to interpret traceroute results, <a href="https://www.nanog.org/meetings/nanog45/presentations/Sunday/RAS_traceroute_N45.pdf">click here</a>.'` |

Sets the Traceroute query help text, displayed when the **?** icon is hovered.

!!! note
    Since there are double quotes (`" "`) in the `<a>` HTML tags, single quotes (`' '`) are required for the TOML string.

# Fonts

#### primary_font_url

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"https://fonts.googleapis.com/css?family=Nunito:400,600,700"` |

Sets the web font URL for the primary font. This font is used for all titles, subtitles, and non-code/preformatted text. The value is passed as a Jinja2 variable to the head block in the base template.

#### primary_font_name

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"Nunito"` |

Sets the web font name for the primary font. This font is used for all titles, subtitles, and non-code/preformatted text. The value is passed as a Jinja2 variable to generate `hyperglass/hyperglass/static/sass/hyperglass.scss`, which ultimately get passed to CSS.

#### mono_font_url

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"https://fonts.googleapis.com/css?family=Fira+Mono"` |

Sets the web font URL for the monospace/code/preformatted text font. This font is used for all query output text, as well as the command title and command name tag. The value is passed as a Jinja2 variable to the head block in the base template.

#### mono_font_name

| Type   | Default Value             |
| ------ | ------------------------- |
| String | `"Fira Mono"` |

Sets the web font URL for the monospace/code/preformatted text font. This font is used for all query output text, as well as the command title and command name tag. The value is passed as a Jinja2 variable to generate `hyperglass/hyperglass/static/sass/hyperglass.scss`, which ultimately get passed to CSS.
