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

from kyponet_master import _routing


def test_routes():
    config_networks = [
        {
            'name': 'net1',
            'cidr4': '10.0.1.0/24'
        },
        {
            'name': 'net2',
            'cidr4': '10.0.2.0/24'
        },
        {
            'name': 'net3',
            'cidr4': '10.0.3.0/24'
        },
        {
            'name': 'net4',
            'cidr4': '10.0.4.0/24'
        },
        {
            'name': 'net5',
            'cidr4': '10.0.5.0/24'
        }
    ]
    config_network_links = [
        {'networkA': 'net1', 'networkB': 'net2'},
        {'networkA': 'net2', 'networkB': 'net3'},
        {'networkA': 'net4', 'networkB': 'net5'}
    ]
    expected_config_networks = [
        {
            'name': 'net1',
            'cidr4': '10.0.1.0/24',
            'routes': [
                {'dstNetwork': 'net2', 'nextHopNetwork': 'net2'},
                {'dstNetwork': 'net3', 'nextHopNetwork': 'net2'}
            ]
        },
        {
            'name': 'net2',
            'cidr4': '10.0.2.0/24',
            'routes': [
                {'dstNetwork': 'net1', 'nextHopNetwork': 'net1'},
                {'dstNetwork': 'net3', 'nextHopNetwork': 'net3'}
            ]
        },
        {
            'name': 'net3',
            'cidr4': '10.0.3.0/24',
            'routes': [
                {'dstNetwork': 'net1', 'nextHopNetwork': 'net2'},
                {'dstNetwork': 'net2', 'nextHopNetwork': 'net2'}
            ]
        },
        {
            'name': 'net4',
            'cidr4': '10.0.4.0/24',
            'routes': [{'dstNetwork': 'net5', 'nextHopNetwork': 'net5'}]
        },
        {
            'name': 'net5',
            'cidr4': '10.0.5.0/24',
            'routes': [{'dstNetwork': 'net4', 'nextHopNetwork': 'net4'}]
        }
    ]

    _routing.extend_networks_with_routing(
        config_networks, config_network_links)
    assert config_networks == expected_config_networks
