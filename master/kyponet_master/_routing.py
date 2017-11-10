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

from dijkstar import Graph
from dijkstar.algorithm import extract_shortest_path_from_predecessor_list
from dijkstar.algorithm import single_source_shortest_paths


def extend_networks_with_routing(config_networks, config_network_links):
    network_by_name = {network['name']: network for network in config_networks}

    graph = _create_graph(set(network_by_name), config_network_links)

    for network_name, network in network_by_name.items():
        network['routes'] = []

        predecessors_map = single_source_shortest_paths(graph, network_name)

        for dst_network_name in network_by_name:
            if dst_network_name == network_name:
                continue
            try:
                shortest_path = extract_shortest_path_from_predecessor_list(
                    predecessors_map, dst_network_name)
            except KeyError:  # no route to destination
                continue
            next_hop_network_name = shortest_path[0][1]
            network['routes'].append({
                'dstNetwork': dst_network_name,
                'nextHopNetwork': next_hop_network_name
            })


def _create_graph(network_names, config_network_links):
    graph = Graph()
    for link in config_network_links:
        network_a = link['networkA']
        network_b = link['networkB']
        if network_a in network_names and network_b in network_names:
            graph.add_edge(network_a, network_b, 100)
            graph.add_edge(network_b, network_a, 100)
    return graph
