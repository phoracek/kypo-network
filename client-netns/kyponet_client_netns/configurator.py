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

import random
import string

from . import _ip
from . import _ovs

BRIDGE_PREFIX = 'kbr_'
NETNS_PREFIX = 'kns_'


def setup(config):
    ovs_idl = _ovs.create_idl()

    _cleanup(ovs_idl)

    networks = config['networks']
    network_links = config['networkLinks']
    hosts = config['hosts']

    _create_netns(networks)
    bridge_by_network = _create_bridges(ovs_idl, networks)
    _configure_bridge_addresses(networks, bridge_by_network)
    _attach_ports(ovs_idl, hosts, bridge_by_network)
    veth_by_link = _connect_links(network_links)
    _configure_routes(networks, veth_by_link)


def _create_netns(networks):
    for network in networks:
        netns_name = _get_netns_name(network['name'])
        _ip.netns_add(netns_name)


def _create_bridges(ovs_idl, networks):
    bridge_by_network = {}
    with ovs_idl.create_transaction(check_error=True) as txn:
        for network in networks:
            network_name = network['name']
            bridge_name = _random_bridge_name()
            bridge_by_network[network_name] = bridge_name
            txn.add(ovs_idl.add_br(bridge_name))
    for network_name, bridge_name in bridge_by_network.items():
        netns_name = _get_netns_name(network_name)
        _ip.link_set(bridge_name, ['netns', netns_name])
        _ip.link_set(bridge_name, ['up'], netns=netns_name)
    return bridge_by_network


def _configure_bridge_addresses(networks, bridge_by_network):
    for network in networks:
        network_name = network['name']
        bridge_name = bridge_by_network[network_name]
        netns_name = _get_netns_name(network_name)
        prefix = network['cidr4'].split('/')[1]
        bridge_address = '{}/{}'.format(network['address4'], prefix)
        _ip.address_add(bridge_name, bridge_address, netns_name)


def _attach_ports(ovs_idl, hosts, bridge_by_network):
    with ovs_idl.create_transaction(check_error=True) as txn:
        for host in hosts:
            for port in host['ports']:
                bridge_name = bridge_by_network[port['networkName']]
                host_iface_name = port['hostInterface']
                txn.add(ovs_idl.add_port(bridge_name, host_iface_name))


def _connect_links(network_links):
    veth_by_link = {}
    for network_link in network_links:
        network_a = network_link['networkA']
        network_b = network_link['networkB']
        veth_a_b_name = _random_iface_name('veth_')
        veth_by_link[(network_a, network_b)] = veth_a_b_name
        veth_b_a_name = _random_iface_name('veth_')
        veth_by_link[(network_b, network_a)] = veth_b_a_name
        _ip.link_add_veth(veth_a_b_name, veth_b_a_name)
        network_a_netns_name = _get_netns_name(network_a)
        _ip.link_set(veth_a_b_name, ['netns', network_a_netns_name])
        _ip.link_set(veth_a_b_name, ['up'], netns=network_a_netns_name)
        network_b_netns_name = _get_netns_name(network_b)
        _ip.link_set(veth_b_a_name, ['netns', network_b_netns_name])
        _ip.link_set(veth_b_a_name, ['up'], netns=network_b_netns_name)
    return veth_by_link


def _configure_routes(networks, veth_by_link):
    network_by_name = {network['name']: network for network in networks}

    routes_config = []
    neighbor_routes_config = []
    for network_name, network in network_by_name.items():
        for route in network['routes']:
            dst_network_name = route['dstNetwork']
            dst_subnet = network_by_name[dst_network_name]['cidr4']
            next_hop_network_name = route['nextHopNetwork']
            next_hop_address = network_by_name[next_hop_network_name][
                'address4']
            netns_name = _get_netns_name(network_name)
            if next_hop_network_name == dst_network_name:
                dev = veth_by_link[(network_name, next_hop_network_name)]
                neighbor_routes_config.append({
                    'subnet': next_hop_address,
                    'dev': dev,
                    'netns': netns_name
                })
            routes_config.append({
                'subnet': dst_subnet,
                'via': next_hop_address,
                'netns': netns_name
            })

    for route_config in neighbor_routes_config:
        _ip.route_add(**route_config)
    for route_config in routes_config:
        _ip.route_add(**route_config)


def _get_netns_name(network_name):
    return NETNS_PREFIX + network_name


def _random_bridge_name():
    return _random_iface_name(BRIDGE_PREFIX)


def _random_iface_name(prefix):
    suffix_len = 15 - len(prefix)
    suffix_letters = string.digits + string.ascii_letters
    suffix = ''.join(random.choice(suffix_letters) for _ in range(suffix_len))
    return prefix + suffix


def cleanup():
    ovs_idl = _ovs.create_idl()
    _cleanup(ovs_idl)


def _cleanup(ovs_idl):
    _cleanup_bridges(ovs_idl)
    _cleanup_netns()


def _cleanup_bridges(ovs_idl):
    brides_to_remove = [bridge for bridge in ovs_idl.list_br().execute()
                        if bridge.startswith(BRIDGE_PREFIX)]
    with ovs_idl.create_transaction(check_error=True) as txn:
        for bridge in brides_to_remove:
            txn.add(ovs_idl.del_br(bridge))


def _cleanup_netns():
    for netns in _ip.netns_list():
        if netns.startswith(NETNS_PREFIX):
            _ip.netns_delete(netns)
