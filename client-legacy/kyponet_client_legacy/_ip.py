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


def link_set(dev, attributes):
    subprocess.check_call(
        [IP, 'link', 'set'] + attributes + ['dev', dev])


def address_add(dev, address):
    subprocess.check_call(
        [IP, 'address', 'add', address, 'dev', dev])


def address_flush(dev):
    subprocess.call([IP, 'address', 'flush', 'dev', dev])


def route_add(subnet, metric, src, dev=None, via=None):
    command = [IP, 'route', 'add', subnet, 'src', src, 'metric', str(metric)]
    if via:
        command += ['via', via]
    if dev:
        command += ['dev', dev]
    subprocess.call(command)


def route_del(subnet, check_error=True):
    command = [IP, 'route', 'del', subnet]
    if check_error:
        subprocess.check_call(command)
    else:
        subprocess.call(command)


def route_list():
    route_list_raw = subprocess.check_output(
        [IP, 'route', 'list'], universal_newlines=True).strip()
    if route_list_raw:
        return [
            route_row.split()[0] for route_row in route_list_raw.split('\n')]
    return []
