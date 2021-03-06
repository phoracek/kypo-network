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

from . import _ip
from . import _ovs
from . import _sysctl

BRIDGE_NAME = 'br0'


def setup(config, network_name):
    ovs_idl = _ovs.create_idl()

    _cleanup(ovs_idl)

    networks = config['networks']
    links = config['networkLinks']
    hosts = config['hosts']

    network_by_name = {network['name']: network for network in networks}
    network = network_by_name[network_name]

    _create_bridge(ovs_idl)
    _configure_bridge_address(network)
    _attach_ports(ovs_idl, network, hosts)
    _configure_routes(network, network_by_name, links)


def _create_bridge(ovs_idl):
    ovs_idl.add_br(BRIDGE_NAME).execute(check_error=True)


def _configure_bridge_address(network):
    prefix = network['cidr4'].split('/')[1]
    bridge_address = '{}/{}'.format(network['address4'], prefix)
    _ip.address_add(BRIDGE_NAME, bridge_address)
    _ip.link_set(BRIDGE_NAME, ['up'])


def _attach_ports(ovs_idl, network, hosts):
    with ovs_idl.create_transaction(check_error=True) as txn:
        for host in hosts:
            for port in host['ports']:
                if port['networkName'] != network['name']:
                    continue
                host_iface_name = port['hostInterface']
                txn.add(ovs_idl.add_port(BRIDGE_NAME, host_iface_name))
                _ip.link_set(host_iface_name, ['up'])


def _configure_routes(network, network_by_name, links):
    routes_config = []
    neighbor_routes_config = []
    dev_by_link = {}
    for link in links:
        dev_by_link[(link['networkA'], link['networkB'])] = \
            link['networkAInterface']
        dev_by_link[(link['networkB'], link['networkA'])] = \
            link['networkBInterface']
    for route in network['routes']:
        dst_network_name = route['dstNetwork']
        dst_subnet = network_by_name[dst_network_name]['cidr4']
        next_hop_network_name = route['nextHopNetwork']
        next_hop_address = network_by_name[next_hop_network_name][
            'address4']
        metric = route['metric']
        if next_hop_network_name == dst_network_name:
            dev = dev_by_link[(network['name'], next_hop_network_name)]
            neighbor_routes_config.append({
                'subnet': next_hop_address,
                'dev': dev,
                'src': network['address4'],
                'metric': metric
            })
        routes_config.append({
            'subnet': dst_subnet,
            'via': next_hop_address,
            'src': network['address4'],
            'metric': metric
        })

    _sysctl.enable_ipv4_forwarding()
    for route_config in neighbor_routes_config:
        _ip.link_set(route_config['dev'], ['up'])
        _ip.route_add(**route_config)
    for route_config in routes_config:
        _ip.route_add(**route_config)


def cleanup():
    ovs_idl = _ovs.create_idl()
    _cleanup(ovs_idl)


def _cleanup(ovs_idl):
    _cleanup_bridge(ovs_idl)
    _cleanup_routes()


def _cleanup_bridge(ovs_idl):
    ports_to_detach = [
        port for port in ovs_idl.list_ports(BRIDGE_NAME).execute() or []]
    with ovs_idl.create_transaction(check_error=True) as txn:
        for port in ports_to_detach:
            txn.add(ovs_idl.del_port(port, BRIDGE_NAME))
    _ip.address_flush(BRIDGE_NAME)


def _cleanup_routes():
    for route in _ip.route_list():
        if route != 'default' and not route.startswith('172.16.1.'):
            _ip.route_del(route, check_error=False)
