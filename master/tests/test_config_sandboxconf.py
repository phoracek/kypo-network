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

from kyponet_master import _config


def test_decode_sandbox_config():
    sandbox_config = {
        'networks': {
            'networks': [
                {
                    'name': 'net1',
                    'ip': '10.0.1.0',
                    'prefix': 24
                },
                {
                    'name': 'net2',
                    'ip': '10.0.2.0',
                    'prefix': 24
                }
            ]
        },
        'routes': {
            'routes': [
                {
                    'lan1': 'net1',
                    'lan2': 'net2'
                }
            ]
        },
        'hosts': {
            'hosts': [
                {
                    'name': 'host1',
                    'lan': 'net1',
                    'hostInterface': 'eth2'
                }
            ]
        }
    }
    expected_decoded_config = {
        'networks': [
            {
                'name': 'net1',
                'cidr4': '10.0.1.0/24'
            },
            {
                'name': 'net2',
                'cidr4': '10.0.2.0/24'
            }
        ],
        'networkLinks': [
            {'networkA': 'net1', 'networkB': 'net2'}
        ],
        'hosts': [
            {
                'name': 'host1',
                'ports': [
                    {
                        'networkName': 'net1',
                        'hostInterface': 'eth2'
                    }
                ]
            }
        ]
    }
    decoded_config = _config.decode_from_sandbox_config(sandbox_config)
    assert decoded_config == expected_decoded_config
