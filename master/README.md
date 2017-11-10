# kyponet-master

Test:

```shell
python3 -m tox
```

Install:

```shell
pip install .
```

Run without actually configuring anything:

```shell
# generate client configuration from kypodb, either for single or multi lmn
kyponet-master --client-type dry-single-lmn
kyponet-master --client-type dry-multi-lmn
# or do the same from sandbox json
kyponet-master --client-type dry-single-lmn --config example_conf.json
kyponet-master --client-type dry-multi-lmn --config example_conf.json
```
