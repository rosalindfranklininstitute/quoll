# Copyright 2022 Rosalind Franklin Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


# Utility imports
import unittest
from importlib.metadata import version


class ImportModuleTest(unittest.TestCase):
    """
    Tests the quoll module can be imported and accessed correctly.
    """

    def test_quoll_version_string(self):
        """
        Tests that the version string can be correctly accessed from the root of the quoll project.
        """
        self.assertEqual(type(version("quoll")), str)


if __name__ == '__main__':
    unittest.main()
