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

from . import _addresses
from . import _config
from . import _executor
from . import _ports
from . import _routing


CLIENT_TYPE_DRY_SINGLE_LMN = 'dry-single-lmn'
CLIENT_TYPE_DRY_MULTI_LMN = 'dry-multi-lmn'
CLIENT_TYPE_LEGACY = 'legacy'
CLIENT_TYPE_NETNS = 'netns'

SINGLE_LMN_CLIENT_TYPES = [
    CLIENT_TYPE_DRY_SINGLE_LMN,
    CLIENT_TYPE_NETNS
]

MULTI_LMN_CLIENT_TYPES = [
    CLIENT_TYPE_DRY_MULTI_LMN,
    CLIENT_TYPE_LEGACY
]

DRY_CLIENT_TYPES = [
    CLIENT_TYPE_DRY_SINGLE_LMN,
    CLIENT_TYPE_DRY_MULTI_LMN
]


def setup(client_type, sandbox_config=None):
    if sandbox_config:
        config = _config.decode_from_sandbox_config(sandbox_config)
    else:
        config = _config.decode_from_db()

    _addresses.extend_networks_with_addresses(config['networks'])

    if client_type in SINGLE_LMN_CLIENT_TYPES:
        _ports.extend_hosts_with_host_interfaces(config['hosts'])

    _routing.extend_networks_with_routing(
        config['networks'], config['networkLinks'])

    if client_type not in DRY_CLIENT_TYPES:
        if client_type in SINGLE_LMN_CLIENT_TYPES:
            _executor.setup_single_lmn('kyponet-client-' + client_type, config)
        elif client_type in MULTI_LMN_CLIENT_TYPES:
            _executor.setup_multi_lmn('kyponet-client-' + client_type, config)

    return config
