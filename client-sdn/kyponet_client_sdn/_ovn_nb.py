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

import ovsdbapp.backend.ovs_idl.connection
import ovsdbapp.schema.ovn_northbound.impl_idl

CONNECTION = 'unix:/var/run/openvswitch/ovnnb_db.sock'
TABLE = 'OVN_Northbound'


def create_idl():
    ovsdbidl = ovsdbapp.backend.ovs_idl.connection.OvsdbIdl.from_server(
        CONNECTION, TABLE)
    connection = ovsdbapp.backend.ovs_idl.connection.Connection(
        ovsdbidl, timeout=10)
    return ovsdbapp.schema.ovn_northbound.impl_idl.OvnNbApiIdlImpl(connection)
