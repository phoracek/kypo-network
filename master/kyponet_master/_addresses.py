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

import ipaddress


def extend_networks_with_addresses(config_networks):
    for network in config_networks:
        network['address4'] = _get_first_address(network['cidr4'])


def _get_first_address(subnet):
    net = ipaddress.ip_network(subnet)
    return str(next(net.hosts()))
