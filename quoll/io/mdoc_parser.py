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


class Mdoc:
    """Class to hold all mdoc attributes
    """
    def __init__(
        self,
        mdoc: str
    ):
        self.mdoc = mdoc
        self.get_mdoc_attributes()

    def get_mdoc_attributes(self):
        """ Gets mdoc attributes as a dict, which is added to attributes as `mdoc_data`.
        """
        current_z = "Stack"
        mdoc_dict = {current_z: {}}
        with open(self.mdoc, "r") as f:
            mdoc_data = f.readlines()

        for line in mdoc_data:
            if line[0] == "[":
                current_z = int(line.split(" = ")[1].strip("]\n"))
                mdoc_dict[current_z] = {}
            elif line[0] != "[":
                if len(line.split("=")) > 1:
                    key = line.split("=")[0].strip()
                    value = line.split("=")[1].strip("\n")[1:]
                    mdoc_dict[current_z][key] = value
        self.mdoc_data = mdoc_dict

    def get_tilt_angles(self):
        """Get tilt angles from mdoc and add to `Mdoc` attributes as `tilt_angles`
        """
        ta = []
        for z in range(len(self.mdoc_data) - 1):
            ta.append(float(self.mdoc_data[z]["TiltAngle"]))
        self.tilt_angles = ta

    def get_attr_as_list(self, key):
        """Get any attribute from the mdoc as a list

        Args:
            key (str): Attribute to retrieve from mdoc

        Raises:
            ValueError: if key is not found in mdoc

        Returns:
            list: value of the attribute from mdoc
        """
        attr = []
        if key in list(self.mdoc_data[0].keys()):
            for z in range(len(self.mdoc_data) - 1):
                attr.append(self.mdoc_data[z][key])
        else:
            raise ValueError(
                f"Key {key} not found in mdoc. Available keys are {self.mdoc_data[0].keys()}"
            )
        return attr
