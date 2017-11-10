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


def decode(sandbox_config):
    networks_conf = sandbox_config['networks']['networks']
    routes_conf = sandbox_config['routes']['routes']
    hosts_conf = sandbox_config['hosts']['hosts']
    return {
        'networks': _decode_networks(networks_conf),
        'networkLinks': _decode_network_links(routes_conf),
        'hosts': _decode_hosts(hosts_conf)
    }


def _decode_networks(networks_conf):
    return [
        {
            'name': network['name'],
            'cidr4': '{}/{}'.format(network['ip'], network['prefix'])
        }
        for network in networks_conf

    ]


def _decode_network_links(routes_conf):
    return [
        {
            'networkA': route['lan1'],
            'networkB': route['lan2']
        }
        for route in routes_conf
    ]


def _decode_hosts(hosts_conf):
    return [
        {
            'name': host['name'],
            'ports': [{
                'networkName': host['lan'],
                'hostInterface': host.get('hostInterface')
            }]
        }
        for host in hosts_conf
    ]
