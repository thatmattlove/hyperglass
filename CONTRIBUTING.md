## Getting Help

If you encounter any issues installing or using hyperglass, open a GitHub issue.

## Reporting Bugs

-   Check the [GitHub issues list](https://github.com/checktheroads/hyperglass/issues)
    to see if the bug you've found has already been reported. Feel free to add a comment describing how it's affecting your installation.

-   When submitting an issue, please be as descriptive as possible. Be sure to include:

        - The environment in which hyperglass is running
        - (Scrubbed) `configuration.toml` and `devices.toml` files
        - The exact steps that can be taken to reproduce the issue (if applicable)
        - Any error messages or exceptions generated
        - Screenshots (if applicable)

-   Please avoid prepending any sort of tag (e.g. "Bug") to the issue title. The issue will be appropriately tagged after it is reviewed.

## Feature Requests

-   First, check the [GitHub issues list](https://github.com/checktheroads/hyperglass/issues) to see if the feature you're requesting is already listed. Feel free to add a comment supporting the addition of the feature.

-   When submitting a feature request on GitHub, be sure to include the
    following:

        - A detailed description of the proposed functionality
        - A use case for the feature; who would use it and what value it would add
          to hyperglass
        - Any third-party libraries or other resources which would be involved

-   Please avoid prepending any sort of tag (e.g. "Feature") to the issue title. The issue will be appropriately tagged after it is reviewed.

## Submitting Pull Requests

-   Be sure to open an issue **before** starting work on a pull request, and discuss your idea with the hyperglass maintainers before beginning work. This will help prevent wasting time on something that may be out of hyperglass's intended scope.

-   Any pull request which does _not_ relate to an accepted issue will be closed.

-   When submitting a pull request, please be sure to work off of the `develop` branch, rather than `master`. The `develop` branch is used for ongoing development, while `master` is used for stable, tested, release-worthy versions of hyperglass.

-   All code submissions should meet the following criteria (CI will enforce
    these checks):

        - Python syntax is valid
        - Python code is [black](https://github.com/python/black) formatted
        - Python code is rated **10/10** by Pylint (using provided `.pylintrc` files)
