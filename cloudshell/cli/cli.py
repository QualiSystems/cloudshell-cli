"""Deprecated,CLI moved to cloudshell.cli.service.cli.CLI."""
import warnings

from cloudshell.cli.service.cli import CLI

warnings.warn(
    "CLI module moved from cloudshell.cli.cli to cloudshell.cli.service.cli. "
    "Use import cloudshell.cli.service.cli.",
    DeprecationWarning,
    stacklevel=2,
)
warnings.simplefilter("default", DeprecationWarning)
__all__ = [CLI]
