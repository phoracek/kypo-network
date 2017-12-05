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

import itertools
import random
import subprocess

from . import _ip
from . import _ovn_nb
from . import _ovs

BRIDGE_NAME = 'br-int'
LS_PREFIX = 'ls_'
LR_PREFIX = 'lr_'


def setup(config):
    ovs_idl = _ovs.create_idl()
    ovn_idl = _ovn_nb.create_idl()

    _cleanup(ovs_idl, ovn_idl)

    hosts = config['hosts']
    networks = config['networks']
    network_groups = _group_interconnected_networks(networks)

    with ovn_idl.create_transaction(check_error=True) as ovn_txn, \
            ovs_idl.create_transaction(check_error=True) as ovs_txn:
        _extend(ovn_txn, _create_routers_and_switches(
            ovn_idl, networks, network_groups))
        ovn_ports_cmds, ovs_ports_cmds = _attach_ports(ovs_idl, ovn_idl, hosts)
        _extend(ovn_txn, ovn_ports_cmds)
        _extend(ovs_txn, ovs_ports_cmds)
    _configure_routes(networks, network_groups)


# TODO: https://review.openstack.org/#/c/524308/
def _extend(transaction, commands):
    for command in commands:
        transaction.add(command)


def _group_interconnected_networks(networks):
    network_groups = []
    for network in networks:
        if network['name'] in itertools.chain.from_iterable(network_groups):
            continue
        network_groups.append(
            {network['name']} |
            {route['dstNetwork'] for route in network['routes']})
    return network_groups


def _create_routers_and_switches(ovn_idl, networks, network_groups):
    network_by_name = {network['name']: network for network in networks}

    cmds = []
    for network_group_index, network_group in enumerate(network_groups):
        lr_name = _get_lr_name(network_group_index)
        cmds.append(ovn_idl.lr_add(lr_name))
        for network_name in network_group:
            network = network_by_name[network_name]
            ls_name = _get_ls_name(network_name)
            lrp_name = '{}-{}'.format(lr_name, ls_name)
            lsp_name = '{}-{}'.format(ls_name, lr_name)
            mac = _random_unicast_local_mac()
            prefix = network['cidr4'].split('/')[1]
            ip_address = '{}/{}'.format(network['address4'], prefix)

            cmds.append(ovn_idl.lrp_add(lr_name, lrp_name, mac, [ip_address]))
            cmds.append(ovn_idl.ls_add(ls_name))
            cmds.append(ovn_idl.lsp_add(ls_name, lsp_name))
            cmds.append(ovn_idl.lsp_set_type(lsp_name, 'router'))
            cmds.append(ovn_idl.lsp_set_addresses(lsp_name, ['router']))
            cmds.append(ovn_idl.lsp_set_options(
                lsp_name, **{'router-port': lrp_name}))
    return cmds


def _attach_ports(ovs_idl, ovn_idl, hosts):
    ovn_cmds = []
    ovs_cmds = []
    mac_by_iface = _get_mac_by_iface()
    for host in hosts:
        ports_by_net = {}
        for port in host['ports']:
            ports_by_net.setdefault(port['networkName'], []).append(port)
        for net, ports in ports_by_net.items():
            for i, port in enumerate(ports):
                host_iface_name = port['hostInterface']
                ovs_cmds.append(ovs_idl.add_port(BRIDGE_NAME, host_iface_name))
                _ip.link_set(host_iface_name, ['up'])
                iface_id = '{}-{}-{}'.format(host['name'], net, i)
                ovn_cmds.append(ovs_idl.iface_set_external_id(
                    host_iface_name, 'iface-id', iface_id))
                ovn_cmds.append(ovn_idl.lsp_add(
                    _get_ls_name(net), iface_id))
                guest_iface_mac = _get_incremented_mac(
                    mac_by_iface[host_iface_name])
                ovn_cmds.append(ovn_idl.lsp_set_addresses(
                    iface_id, [guest_iface_mac]))
    return ovn_cmds, ovs_cmds


# TODO: use ovsdbapp when static routes are fixed
def _configure_routes(networks, network_groups):
    network_by_name = {network['name']: network for network in networks}

    for network_group_index, network_group in enumerate(network_groups):
        lr_name = _get_lr_name(network_group_index)
        for network_name in network_group:
            network = network_by_name[network_name]
            dst_subnet = network['cidr4']
            next_hop_address = network['address4']
            subprocess.check_call([
                'ovn-nbctl', 'lr-route-add',
                lr_name, dst_subnet, next_hop_address
            ])


def _get_lr_name(lr_index):
    return '{}{}'.format(LR_PREFIX, lr_index)


def _get_ls_name(network_name):
    return LS_PREFIX + network_name


def _random_unicast_local_mac():
    macaddr = random.randint(0x000000000000, 0xffffffffffff)
    macaddr |= 0x020000000000  # locally administered
    macaddr &= 0xfeffffffffff  # unicast
    macaddr_str = '{:0>12x}'.format(macaddr)
    return ':'.join([macaddr_str[i:i + 2]
                     for i in range(0, len(macaddr_str), 2)])


def _get_mac_by_iface():
    # TODO: use ip link show from _ip
    mac_by_iface = {}
    links_lines = subprocess.check_output(
        ['ip', 'link', 'show'], universal_newlines=True).strip().split('\n')
    for i in range(0, len(links_lines), 2):
        iface = links_lines[i].split()[1][:-1]
        mac = links_lines[i+1].split()[1]
        mac_by_iface[iface] = mac
    return mac_by_iface


def _get_incremented_mac(mac):
    mac_int = int(mac.replace(':', ''), 16)
    incremented_mac_int = mac_int + 1
    incremented_mac_hex = '{:012x}'.format(incremented_mac_int)
    incremented_mac = ':'.join([
        incremented_mac_hex[i] + incremented_mac_hex[i+1]
        for i in range(0, 12, 2)])
    return incremented_mac


def cleanup():
    ovs_idl = _ovs.create_idl()
    ovn_idl = _ovn_nb.create_idl()
    _cleanup(ovs_idl, ovn_idl)


def _cleanup(ovs_idl, ovn_idl):
    _detach_ports(ovs_idl)
    _remove_routers_and_switches(ovn_idl)


def _detach_ports(ovs_idl):
    ports_to_detach = [
        port for port in ovs_idl.list_ports(BRIDGE_NAME).execute()]
    with ovs_idl.create_transaction(check_error=True) as txn:
        for port in ports_to_detach:
            txn.add(ovs_idl.del_port(port, BRIDGE_NAME))


def _remove_routers_and_switches(ovn_idl):
    with ovn_idl.create_transaction(check_error=True) as txn:
        for router in ovn_idl.lr_list().execute():
            txn.add(ovn_idl.lr_del(router.name))
        for switch in ovn_idl.ls_list().execute():
            txn.add(ovn_idl.ls_del(switch.name))
