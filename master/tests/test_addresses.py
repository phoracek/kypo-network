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

from kyponet_master import _addresses


def test_addresses():
    config_networks = [
        {
            'name': 'net1',
            'cidr4': '10.0.1.0/24'
        }
    ]
    expected_config_networks = [
        {
            'name': 'net1',
            'cidr4': '10.0.1.0/24',
            'address4': '10.0.1.1'
        }
    ]
    _addresses.extend_networks_with_addresses(config_networks)
    assert config_networks == expected_config_networks
