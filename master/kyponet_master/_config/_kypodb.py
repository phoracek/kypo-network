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

import contextlib

import psycopg2


def decode():
    with _connect_to_db() as conn:
        cursor = conn.cursor()
        network_table = _get_network_table_from_db(cursor)
        link_table = _get_link_table_from_db(cursor)
        node_table = _get_node_table_from_db(cursor)
        node_interface_table = _get_node_interface_table_from_db(cursor)
    return {
        'networks': _decode_networks(network_table),
        'networkLinks': _decode_network_links(network_table, link_table),
        'hosts': _decode_hosts(
            node_table, node_interface_table, network_table, link_table)
    }


@contextlib.contextmanager
def _connect_to_db():
    conn = psycopg2.connect("dbname='kypodb' user='postgres' host='localhost'")
    try:
        yield conn
    finally:
        conn.close()


def _get_node_table_from_db(cursor):
    cursor.execute("""
        SELECT name, measurable_id
        FROM node
        ORDER BY measurable_id ASC
    """)
    node_rows = cursor.fetchall()
    return [{'name': row[0], 'measurable_id': row[1]} for row in node_rows]


def _get_node_interface_table_from_db(cursor):
    cursor.execute("""
        SELECT connectable_id, measurable_id
        FROM node_interface
        ORDER BY connectable_id ASC
    """)
    node_interface_rows = cursor.fetchall()
    return [{'connectable_id': row[0], 'measurable_id': row[1]}
            for row in node_interface_rows]


def _get_network_table_from_db(cursor):
    cursor.execute("""
        SELECT name, connectable_id, cidr4
        FROM network
        ORDER BY connectable_id ASC
    """)
    network_rows = cursor.fetchall()
    return [{'name': row[0], 'connectable_id': row[1], 'cidr4': row[2]}
            for row in network_rows]


def _get_link_table_from_db(cursor):
    cursor.execute("""
        SELECT src_connectable_id, dst_connectable_id, src_interface
        FROM link
        ORDER BY measurable_id ASC
    """)
    net_rows = cursor.fetchall()
    return [
        {
            'src_connectable_id': row[0],
            'dst_connectable_id': row[1],
            'src_interface': row[2]
        }
        for row in net_rows
    ]


def _decode_networks(network_table):
    return [
        {
            'name': network_row['name'],
            'cidr4': network_row['cidr4']
        }
        for network_row in network_table
    ]


def _decode_network_links(network_table, link_table):
    network_name_by_connectable_id = {
        network_row['connectable_id']: network_row['name']
        for network_row in network_table}
    interface_by_src_and_dst_connectable_id = {
        (link_row['src_connectable_id'], link_row['dst_connectable_id']):
            link_row['src_interface']
        for link_row in link_table
    }
    links = set([
        tuple(sorted([
            link_row['src_connectable_id'],
            link_row['dst_connectable_id']]))
        for link_row in link_table
    ])
    return [
        {
            'networkA': network_name_by_connectable_id[link[0]],
            'networkAInterface': interface_by_src_and_dst_connectable_id[
                (link[0], link[1])],
            'networkB': network_name_by_connectable_id[link[1]],
            'networkBInterface': interface_by_src_and_dst_connectable_id[
                (link[1], link[0])]
        }
        for link in links
        if (link[0] in network_name_by_connectable_id and
            link[1] in network_name_by_connectable_id)
    ]


def _decode_hosts(node_table, node_interface_table, network_table, link_table):
    dst_connectable_id_by_src_connectable_id = {
        link_row['src_connectable_id']: link_row['dst_connectable_id']
        for link_row in link_table
    }
    network_name_by_connectable_id = {
        network_row['connectable_id']: network_row['name']
        for network_row in network_table}
    interface_by_src_and_dst_connectable_id = {
        (link_row['src_connectable_id'], link_row['dst_connectable_id']):
            link_row['src_interface']
        for link_row in link_table
    }
    networks_and_ifaces_by_measurable_id = {}
    for node_interface_row in node_interface_table:
        connectable_id = node_interface_row['connectable_id']
        dst_connectable_id = dst_connectable_id_by_src_connectable_id[
            connectable_id]
        dst_network_name = network_name_by_connectable_id[dst_connectable_id]
        host_interface = interface_by_src_and_dst_connectable_id[
            (dst_connectable_id, connectable_id)]
        networks_and_ifaces_by_measurable_id.setdefault(
            node_interface_row['measurable_id'], []).append(
                (dst_network_name, host_interface)
            )
    hosts = []
    for node_row in node_table:
        hosts.append({
            'name': node_row['name'],
            'ports': [
                {
                    'networkName': network_name,
                    'hostInterface': host_iface
                }
                for network_name, host_iface in
                networks_and_ifaces_by_measurable_id.get(
                    node_row['measurable_id'], [])
            ]
        })
    return hosts
