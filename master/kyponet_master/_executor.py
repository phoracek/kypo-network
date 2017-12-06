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

import json
import logging
import threading

import paramiko


def setup_multi_lmn(client_command, config):
    threads = []
    for i, network in enumerate(config['networks']):
        threads.append(threading.Thread(
            target=_setup_lmn,
            args=(
                '172.16.1.{}'.format(i + 2),
                client_command,
                config,
                network['name']
            )
        ))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def setup_single_lmn(client_command, config):
    _setup_lmn('172.16.1.2', client_command, config)


def _setup_lmn(address, client_command, config, network_name=None):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(address)
    logging.info('Connected to LMN %s, requesting config %s', address, config)
    try:
        command = client_command + ' setup'
        if network_name:
            command += ' ' + network_name
        stdin, stdout, stderr = ssh.exec_command(command)
        json.dump(config, stdin)
        stdin.channel.shutdown_write()
        logging.info('Config setup on %s finished with out: %s, err: %s',
                     address, stdout.read(), stderr.read())
    finally:
        ssh.close()
