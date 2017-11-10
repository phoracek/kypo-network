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


def test_decode_kypodb_config(mocker):
    mocker.patch('psycopg2.connect', autospec=True)
    mocker.patch.object(
        _config._kypodb, '_get_network_table_from_db', return_value=[
            {'name': 'net1', 'cidr4': '10.0.1.0/24', 'connectable_id': 1},
            {'name': 'net2', 'cidr4': '10.0.2.0/24', 'connectable_id': 2}
        ]
    )
    mocker.patch.object(
        _config._kypodb, '_get_link_table_from_db', return_value=[
            {
                'src_connectable_id': 1,
                'dst_connectable_id': 2,
                'src_interface': 'eth1'
            },
            {
                'src_connectable_id': 2,
                'dst_connectable_id': 1,
                'src_interface': 'eth1'
            },
            {
                'src_connectable_id': 1,
                'dst_connectable_id': 3,
                'src_interface': 'eth2'
            },
            {
                'src_connectable_id': 3,
                'dst_connectable_id': 1,
                'src_interface': None
            }
        ]
    )
    mocker.patch.object(
        _config._kypodb, '_get_node_table_from_db', return_value=[
            {'name': 'host1', 'measurable_id': 1}
        ]
    )
    mocker.patch.object(
        _config._kypodb, '_get_node_interface_table_from_db', return_value=[
            {'connectable_id': 3, 'measurable_id': 1}
        ]
    )
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
            {
                'networkA': 'net1',
                'networkAInterface': 'eth1',
                'networkB': 'net2',
                'networkBInterface': 'eth1'
            }
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
    decoded_config = _config.decode_from_db()
    assert decoded_config == expected_decoded_config
