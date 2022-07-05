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

from quoll.io import mdoc_parser


class MdocTest(unittest.TestCase):
    """
    Tests the Mdoc parser module.
    Test data is from https://www.ebi.ac.uk/empiar/EMPIAR-10987/
    """

    def setUp(self):
        self.mdoc_test = mdoc_parser.Mdoc(
            mdoc="./data/L4_ts_03_sort.mrc.mdoc"
        )

    def test_basic_mdoc(self):
        """ Tests that the test mdoc is read """
        self.assertEqual(type(self.mdoc_test.mdoc), str)
        self.assertEqual(len(self.mdoc_test.mdoc_data), 42)

    def test_mdoc_tilt_angle(self):
        """ Tests that tilt angles are imported correctly """
        self.mdoc_test.get_tilt_angles()
        self.assertEqual(len(self.mdoc_test.tilt_angles), 41)

    def test_mdoc_attr_retrieval(self):
        """ Tests that attributes can be retrieved from the mdoc """
        attr = self.mdoc_test.get_attr_as_list("PixelSpacing")
        self.assertEqual(len(attr), 41)

    def test_mdoc_attr_retrieval_error(self):
        """ Tests that retrieving attributes not present in mdoc raise errors"""
        self.assertRaises(ValueError, self.mdoc_test.get_attr_as_list, "NotAKey")

if __name__ == '__main__':
    unittest.main()
