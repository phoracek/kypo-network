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

from kyponet_master import _ports


def test_ports():
    config_hosts = [
        {
            'name': 'host1',
            'ports': [
                {'networkName': 'net1'},
                {'networkName': 'net2'}
            ]
        },
        {
            'name': 'host2',
            'ports': [
                {'networkName': 'net1'}
            ]
        }
    ]
    expected_config_hosts = [
        {
            'name': 'host1',
            'ports': [
                {'networkName': 'net1', 'hostInterface': 'eth1'},
                {'networkName': 'net2', 'hostInterface': 'eth2'}
            ]
        },
        {
            'name': 'host2',
            'ports': [
                {'networkName': 'net1', 'hostInterface': 'eth3'}
            ]
        }
    ]
    _ports.extend_hosts_with_host_interfaces(config_hosts)
    assert config_hosts == expected_config_hosts
