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

from collections import defaultdict


def extend_networks_with_routing(config_networks, config_network_links):
    network_by_name = {network['name']: network for network in config_networks}

    graph = _create_graph(network_by_name.keys(), config_network_links)

    for network_name, network in network_by_name.items():
        network['routes'] = []
        for dst_network_name in network_by_name.keys():
            if dst_network_name == network_name:
                continue
            for path in find_all_paths(graph, network_name, dst_network_name):
                network['routes'].append({
                    'dstNetwork': dst_network_name,
                    'nextHopNetwork': path[1],
                    'metric': (len(path) - 1) * 100
                })


def find_all_paths(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


def _create_graph(network_names, config_network_links):
    graph = defaultdict(list)
    for link in config_network_links:
        network_a = link['networkA']
        network_b = link['networkB']
        if network_a in network_names and network_b in network_names:
            graph[network_a].append(network_b)
            graph[network_b].append(network_a)
    return graph
