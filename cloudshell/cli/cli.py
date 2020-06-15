"""Deprecated,CLI moved to cloudshell.cli.service.cli.CLI."""
import warnings

from cloudshell.cli.service.cli import CLI

warnings.warn(
    "Module cloudshell.cli.cli moved to cloudshell.cli.service.cli",
    category=DeprecationWarning,
    stacklevel=2,
)
warnings.simplefilter("default", DeprecationWarning)
__all__ = [CLI]
