"""hyperglass CLI custom exceptions."""

# Third Party
from click import ClickException, echo
from click._compat import get_text_stderr


class CliError(ClickException):
    """Custom exception to exclude the 'Error:' prefix from echos."""

    def show(self, file=None):
        """Exclude 'Error:' prefix from raised exceptions."""
        if file is None:
            file = get_text_stderr()
        echo(self.format_message())
