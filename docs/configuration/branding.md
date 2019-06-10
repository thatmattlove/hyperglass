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

# `[branding]` - Site Parameters
#### site_name

| Type   | Default Value  |
| ------ | -------------- |
| String | `"hyperglass"` |

HTML `<title>` element that is shown in a browser's title bar.

## `[branding.footer]` - Footer Configuration
#### enable

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables entire footer element.

The footer text itself can be customized by adding a [Markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) document to `hyperglass/hyperglass/render/templates/info/details/footer.md`. The example file, `footer.md.example`, can be copied to `footer.md` and modified. All Markdown files in this directory are excluded from change control and will not be overwritten when hyperglass is updated.

!!! note "Syntax"
    The custom content Markdown files *must* have TOML Front Matter, even if there are no attributes used.

## `[branding.credit]` - Credit Configuration
#### enable

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables text below the footer element, which links to the hyperglass repo:

> Powered by Hyperglass. Source code licensed BSD 3-Clause Clear.

## `[branding.peering_db]` - PeeringDB Configuration
#### enable

| Type    | Default Value |
| ------- | ------------- |
| Boolean | `true`        |

Enables or disables the PeeringDB link in the upper right corner. If `true`, the [primary_asn](#primary_asn) will be automatically used to create the URL to your ASN's PeeringDB entry.

## `[branding.text]` - Site-Wide Text Customizations

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

#### query_type

| Type   | Default Value        |
| ------ | -------------------- |
| String | `"Query Type"`       |

Placeholder text that appears in the Query Type dropdown.

#### results

| Type   | Default Value        |
| ------ | -------------------- |
| String | `"Results"`       |

Title text used for the results message box which contains the results of the query.

#### location

| Type   | Default Value          |
| ------ | ---------------------- |
| String | `"Select Location..."` |

Placeholder text that appears in the Location dropdown.

#### query_placeholder

| Type   | Default Value                         |
| ------ | ------------------------------------- |
| String | `"IP, Prefix, Community, or AS Path"` |

Placeholder text that appears in the main search box.

#### bgp_route

| Type   | Default Value |
| ------ | ------------- |
| String | `"BGP Route"` |

Dropdown text used for the BGP Route query type.

#### bgp_community

| Type   | Default Value     |
| ------ | ----------------- |
| String | `"BGP Community"` |

Dropdown text used for the BGP Community query type.

#### bgp_aspath

| Type   | Default Value   |
| ------ | --------------- |
| String | `"BGP AS Path"` |

Dropdown text used for the BGP AS Path query type.

#### ping

| Type   | Default Value |
| ------ | ------------- |
| String | `"Ping"`      |

Dropdown text used for the Ping query type.

#### traceroute

| Type   | Default Value  |
| ------ | -------------- |
| String | `"Traceroute"` |

Dropdown text used for the Traceroute query type.

### `[branding.text.404]` - 404 Error Page Text Customization

The 404 error page will be displayed if a user attempts to visit any non-existent URI, e.g. `http://lg.domain.tld/this_isnt_real`

#### title

| Type   | Default Value |
| ------ | ------------- |
| String | `"Error"`     |

#### subtitle

| Type   | Default Value      |
| ------ | ------------------ |
| String | `"Page Not Found"` |

### `[branding.text.500]` - 500 Error Page Text Customization

The 500 error page will be displayed if there is a backend problem or if an exception is raised. If you get this page, you should probably enable debug mode to find out why.

#### title

| Type   | Default Value |
| ------ | ------------- |
| String | `"Error"`     |

#### subtitle

| Type   | Default Value            |
| ------ | ------------------------ |
| String | `"Something Went Wrong"` |

## `[branding.logo]` - Logo & Favicon Configuration

#### path

| Type   | Default Value                         |
| ------ | ------------------------------------- |
| String | `"static/images/hyperglass-dark.png"` |

Sets the path to the logo file, which will be displayed if [title_mode](#title_mode) is set to `"logo_only"`. This file can be any browser-compatible format, such as JPEG, PNG, or SVG.

!!! note "Custom Files"
    The `hyperglass/hyperglass/static/custom/` directory is excluded from change control, and will not be overwritten when hyperglass is updated. Custom image files should be placed here.

#### width

| Type   | Default Value |
| ------ | ------------- |
| String | `"384"`       |

Sets the width of the logo defined in the [logo_path](#logo_path) parameter. This is helpful if your logo is a dimension that doesn't quite work with the default width.

#### favicons

| Type   | Default Value                         |
| ------ | ------------------------------------- |
| String | `"static/images/favicon/"` |

Sets the path to the favicons directory (must have a trailing `/`). For full browser and platform comatability, it is recommended to use [RealFaviconGenerator](https://realfavicongenerator.net/) and place all the generated files in `static/custom/images/favicon/` (and update the `favicons` parameter).

## `[branding.color]` - Color Customization

#### background

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#fbfffe"`   | <span class="bd-color" style="background-color: #fbfffe;"></span> |

Sets the background color of the main page.


#### button_submit

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#40798c"`   | <span class="bd-color" style="background-color: #40798c;"></span> |

Sets color of the submit button.

#### danger

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#ff3860"`   | <span class="bd-color" style="background-color: #ff3860;"></span> |

Sets color of the Bulma "danger" class, which is used for some user-facing error, and as the background color for the 404, 500 and Rate Limit error pages.

#### progress_bar

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#40798c"`   | <span class="bd-color" style="background-color: #40798c;"></span> |

Sets color of the progress bar that displays while the back-end application processes the request.

### `[branding.color.tag]` - Tag Color Customization

Bulma tags are used to show attributes for the active query being run.

#### type_title

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#330036"`   | <span class="bd-color" style="background-color: #330036;"></span> |

Sets color of the title portion of the query type tag which appears at the top of the results box on the right side.

#### type

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#ff5e5b"`   | <span class="bd-color" style="background-color: #ff5e5b;"></span> |

Sets color of the type portion of the query type tag which appears at the top of the results box on the right side.

#### location_title

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#330036"`   | <span class="bd-color" style="background-color: #330036;"></span> |

Sets color of the title portion of the location tag which appears at the top of the results box on the left side.

#### location

| Type   | Default Value | Preview                                                           |
| ------ | ------------- | ----------------------------------------------------------------- |
| String | `"#40798c"`   | <span class="bd-color" style="background-color: #40798c;"></span> |

Sets color of the location name portion of the location tag which appears at the top of the results box on the left side.

## `[branding.font]` - Font Customization

Hyperglass makes use of two font families - a primary family and a monospace family. The primary family is used for all paragraph, title/subtitle, and non-code/preformatted text, and the monospace font is used for any code/preformatted blocks as well as the query results.

The values are passed as a Jinja2 variable to generate `hyperglass/hyperglass/static/sass/hyperglass.scss`, which will be compiled from Sass to CSS.

### `[branding.font.primary]` - Primary Font Customization

#### name

| Type   | Default Value |
| ------ | ------------- |
| String | `"Nunito"`    |

Sets the web font name for the primary font.

#### url

| Type   | Default Value                                                  |
| ------ | -------------------------------------------------------------- |
| String | `"https://fonts.googleapis.com/css?family=Nunito:400,600,700"` |

Sets the web font URL for the primary font.

### `[branding.font.mono]` - Monospace Font Customization

#### name

| Type   | Default Value |
| ------ | ------------- |
| String | `"Fira Mono"` |

Sets the web font name for the monospace/code/preformatted text font.

#### url

| Type   | Default Value                                         |
| ------ | ----------------------------------------------------- |
| String | `"https://fonts.googleapis.com/css?family=Fira+Mono"` |

Sets the web font URL for the monospace/code/preformatted text font.


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
