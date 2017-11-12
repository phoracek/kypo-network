# Networking Solution For KYPO2

Configure networking from SMN. `desired_configuration.json` contains sandbox
configuration with desired networking. The only requirement is to have hosts
in this configuration in the same order as in the actual single-LMN
configuration.

```shell
kyponet-master -c desired_configuration.json --client netns
```

Read [master](master/README.md) or [client-netns](client-netns/README.md)
documentation for more about deployment and testing.
