import unittest
import warnings


class TestImportCliDeprecated(unittest.TestCase):
    def test_deprecated_import(self):
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            from cloudshell.cli.cli import CLI  # noqa: F401

            # verify
            self.assertEqual(1, len(w))
            self.assertEqual(DeprecationWarning, w[-1].category)
            self.assertIn(
                "module moved from cloudshell.cli.cli to cloudshell.cli.service.cli",
                str(w[-1].message),
            )
