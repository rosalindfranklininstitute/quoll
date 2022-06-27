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


from setuptools import setup, find_packages


setup(
    version='0.0',
    name='quoll',
    description='Image quality assessment for electron tomography',
    url='https://github.com/rosalindfranklininstitute/quoll',
    packages=find_packages('quoll'),
    package_dir={'': 'quoll'},
    test_suite='tests',
    license='Apache License, Version 2.0',
    zip_safe=False,
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
        ]
    }
)