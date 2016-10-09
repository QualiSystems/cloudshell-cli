import unittest
import cloudshell.tests.cli.test_cli_operations_impl as testCLI



def suite():
    suite = unittest.TestSuite()
    suite.addTest(testCLI.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')