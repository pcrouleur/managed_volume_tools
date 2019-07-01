# managed_volume_tools

This project provides a Python package that can be used to setup and manage Rubrik Managed Volume backups. 

It utilizes the Rubrik SDK for python. The scripts have been tested against Python 2.7.5 and Python 3.7.4

# :hammer: Installation

Extract managed_volume_tools.zip

`$ unzip managed_volume_tools.zip`

Change to the managed_volume_tools directory.

`$ cd managed_volume_tools`

Create a python virtual environment

```
$ virtualenv venv
$ . venv/bin/activate
```

Install the package

`$ pip install --editable .`

Now the commands should be available

`$ mv_info --help`

# :mag: Example

By default, the Rubrik SDK will attempt to read the the Rubrik Cluster credentials from the following environment variables:

* `rubrik_cdm_node_ip`
* `rubrik_cdm_username`
* `rubrik_cdm_password`

You can also set these values in config.json.

