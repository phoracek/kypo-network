# Networking Solution for KYPO2

This project automates process of KYPO LMN networking configuration. Sandbox
configuration is read either from specified JSON or from KYPODB and applied on
LMNs in order to configure desired network topology.

## Architecture

This application consists of two parts, master and client.

### master

Master reads JSON/KYPODB, fills in implicit information, calculate routes to
provide interconnectivity and passes this configuration to LMNs in form of
generic client API.

### client

Client accepts client API configuration and applies changes on the node. There
are multiple clients providing various means of network configuration.

#### client-legacy

Automatizes current network configuration.

#### client-netns

Setups multiple networks on one LMN. This is not yet fully integrated into
KYPO.

## Examples

### Setup legacy multi-LMN networking

Deploy sandbox with 3 networks and 2 hosts.

```
host1 (10.0.1.2/24)
  |
 net1 (10.0.1.1/24)
  |
 net2 (10.0.2.1/24)
  |
 net3 (10.0.3.1/24)
  |
host2 (10.0.3.2/24)
```

This sandbox could be modeled with following configuration.

```json
{
  "sandbox": {
    "name": "kyponet-legacy",
    "document path": "",
    "teams": [
      "single user"
    ],
    "logicalRoles": [
      "none"
    ]
  },
  "networks": {
    "networks": [
      {
        "name": "net1",
        "ip": "10.0.1.0",
        "prefix": 24,
        "maxHosts": 1
      },
      {
        "name": "net2",
        "ip": "10.0.2.0",
        "prefix": 24,
        "maxHosts": 0
      },
      {
        "name": "net3",
        "ip": "10.0.3.0",
        "prefix": 24,
        "maxHosts": 1
      }
    ]
  },
  "routes": {
    "routes": [
      {
        "name": "",
        "lan1": "net1",
        "lan2": "net2"
      },
      {
        "name": "",
        "lan1": "net2",
        "lan2": "net3"
      }
    ]
  },
  "hosts": {
    "hosts": [
      {
        "name": "host1",
        "lan": "net1",
        "ip": "10.0.1.2",
        "physRole": "desktop"
      },
      {
        "name": "host2",
        "lan": "net3",
        "ip": "10.0.3.2",
        "physRole": "desktop"
      }
    ]
  },
  "linksProperties": {
    "linksProperties": []
  },
  "hostsAccess": {
    "teams": [
      {
        "name": "single user",
        "logicalRoles": [
          "none"
        ]
      }
    ]
  }
}
```

Legacy client requires interface names specified per each link in KYPODB.
In case such names are not defined by KYPO itself, following commands executed
on SMN fix it for the aforementioned configuration.

```shell
su postgres
psql -d kypodb -c "
UPDATE link SET src_interface = 'eth1' WHERE measurable_id = 1;
UPDATE link SET src_interface = 'eth1' WHERE measurable_id = 2;
UPDATE link SET src_interface = 'eth2' WHERE measurable_id = 3;
UPDATE link SET src_interface = 'eth1' WHERE measurable_id = 4;
UPDATE link SET src_interface = 'eth2' WHERE measurable_id = 6;
UPDATE link SET src_interface = 'eth2' WHERE measurable_id = 9;
"
```

Install master on SMN.

```shell
# enable NAT to external network
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

apt-get update
apt-get install -y git
git clone https://github.com/phoracek/kypo-network
cd kypo-network/master
pip install .
```

On each LMN install client-legacy.

```shell
# setup connection to external network
ip route add default via 172.16.1.1
sed -i '$ d' /etc/resolv.conf
echo 'nameserver 8.8.8.8' > /etc/resolv.conf

# echo enable forwarding (TODO part of setup)
echo 1 > /proc/sys/net/ipv4/ip_forward

# update pyOpenSSL
pip install -U pyOpenSSL

git clone https://github.com/phoracek/kypo-network
cd kypo-network/client-legacy
pip install .
```

Run master executable on SMN. Following command will obtain configuration from
database, calculate routes for interconnectivity and remotely execute clients
on each LMN with their dedicated configuration.

```shell
kyponet-master --client-type legacy
```

Now there should be interconnectivity between all L3 switches and hosts.

### Setup netns based single-LMN networking


Deploy single-LMN sandbox.

```
host1 (10.0.1.2/24)
  |
 net  (10.0.0.1/24)  # will contain net1, net2 and net3
  |
host2 (10.0.3.2/24)
```

With following steps we will create multiple networks within one LMN.

```
host1 (10.0.1.2/24)
  |
 net1 (10.0.1.1/24)
  |
 net2 (10.0.2.1/24)
  |
 net3 (10.0.3.1/24)
  |
host2 (10.0.3.2/24)
```

Currently there is not support for single-LMN/multiple-networks in KYPO. Due to
that we will use one configuration to setup sandbox and another to configure
networks on top of it.

```json
{
  "sandbox": {
    "name": "kyponet-netns",
    "document path": "",
    "teams": [
      "single user"
    ],
    "logicalRoles": [
      "none"
    ]
  },
  "networks": {
    "networks": [
      {
        "name": "net",
        "ip": "10.0.0.0",
        "prefix": 16,
        "maxHosts": 1
      }
    ]
  },
  "routes": {
    "routes": []
  },
  "hosts": {
    "hosts": [
      {
        "name": "host1",
        "lan": "net",
        "ip": "10.0.1.2",
        "physRole": "desktop"
      },
      {
        "name": "host2",
        "lan": "net",
        "ip": "10.0.3.2",
        "physRole": "desktop"
      }
    ]
  },
  "linksProperties": {
    "linksProperties": []
  },
  "hostsAccess": {
    "teams": [
      {
        "name": "single user",
        "logicalRoles": [
          "none"
        ]
      }
    ]
  }
}
```

Install master on SMN.

```shell
# enable NAT to external network
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

apt-get update
apt-get install -y git
git clone https://github.com/phoracek/kypo-network
cd kypo-network/master
pip install .
```

Install client-netns on LMN.

```shell
# setup connection to external network
ip route add default via 172.16.1.1
sed -i '$ d' /etc/resolv.conf
echo 'nameserver 8.8.8.8' > /etc/resolv.conf

# echo enable forwarding (TODO part of setup)
echo 1 > /proc/sys/net/ipv4/ip_forward

# update pyOpenSSL
pip install -U pyOpenSSL

git clone https://github.com/phoracek/kypo-network
cd kypo-network/client-legacy
pip install .
```

Save following config on SMN, it will be used by master as an input
configuration instead of KYPODB.

```json
{
  "sandbox": {
    "name": "kyponet-legacy",
    "document path": "",
    "teams": [
      "single user"
    ],
    "logicalRoles": [
      "none"
    ]
  },
  "networks": {
    "networks": [
      {
        "name": "net1",
        "ip": "10.0.1.0",
        "prefix": 24,
        "maxHosts": 1
      },
      {
        "name": "net2",
        "ip": "10.0.2.0",
        "prefix": 24,
        "maxHosts": 0
      },
      {
        "name": "net3",
        "ip": "10.0.3.0",
        "prefix": 24,
        "maxHosts": 1
      }
    ]
  },
  "routes": {
    "routes": [
      {
        "name": "",
        "lan1": "net1",
        "lan2": "net2"
      },
      {
        "name": "",
        "lan1": "net2",
        "lan2": "net3"
      }
    ]
  },
  "hosts": {
    "hosts": [
      {
        "name": "host1",
        "lan": "net1",
        "ip": "10.0.1.2",
        "physRole": "desktop"
      },
      {
        "name": "host2",
        "lan": "net3",
        "ip": "10.0.3.2",
        "physRole": "desktop"
      }
    ]
  },
  "linksProperties": {},
  "hostsAccess": {
    "teams": [
      {
        "name": "single user",
        "logicalRoles": [
          "none"
        ]
      }
    ]
  }
}
```

Run master executable on SMN. Following command will obtain configuration from
the configuration file saved in previous step, calculate routes for
interconnectivity and remotely execute client on the single LMN with its client
configuration.

```shell
kyponet-master --config configuration.json --client-type netns
```

Now there should be interconnectivity between all L3 switches and hosts. You
can access L3 switches by entering their respective netns. With following
commands you can ping net3 from net1.

```shell
ip netns exec kns-net1 ping 10.0.3.1
```

## Development and Testing

You can find more information about development and testing of specific
components in their respective directories.
