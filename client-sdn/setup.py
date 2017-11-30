# Copyright 2017 kypo-network authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.core import setup


with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


setup(
    name='kyponet-client-sdn',
    version='0.0.1',
    packages=['kyponet_client_sdn'],
    scripts=['scripts/kyponet-client-sdn'],
    install_requires=install_requires
)
