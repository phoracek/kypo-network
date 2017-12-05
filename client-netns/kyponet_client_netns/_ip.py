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

import subprocess

IP = 'ip'


def link_set(dev, attributes, netns=None):
    subprocess.check_call(_in_netns(
        [IP, 'link', 'set'] + attributes + ['dev', dev],
        netns))


def link_add_veth(veth_a, veth_b):
    subprocess.check_call([IP, 'link', 'add', veth_a, 'type', 'veth',
                           'peer', 'name', veth_b])


def address_add(dev, address, netns=None):
    subprocess.check_call(_in_netns(
        [IP, 'address', 'add', address, 'dev', dev],
        netns))


def route_add(subnet, metric, dev=None, via=None, netns=None):
    command = ['ip', 'route', 'add', subnet, 'metric', str(metric)]
    if via:
        command += ['via', via]
    if dev:
        command += ['dev', dev]
    subprocess.check_call(_in_netns(command, netns))


def _in_netns(command, netns):
    if netns:
        return [IP, 'netns', 'exec', netns] + command
    return command


def netns_list():
    netns_list_raw = subprocess.check_output(
        [IP, 'netns', 'list'], universal_newlines=True).strip()
    if netns_list_raw:
        return netns_list_raw.split('\n')
    return []


def netns_add(netns):
    subprocess.check_call([IP, 'netns', 'add', netns])


def netns_delete(netns):
    subprocess.check_call([IP, 'netns', 'del', netns])
