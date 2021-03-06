﻿# managed_volume_tools

This project provides a Python package that can be used to setup and manage Rubrik Managed Volume backups. 

It utilizes the Rubrik SDK for python. The scripts have been tested against Python 2.7.5 and Python 3.7.4

Warning: this code is provided on a best effort basis and is not in any way officially supported or sanctioned by Rubrik. The code in this repository is provided as-is and the author accepts no liability for damages resulting from its use.

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
or
* `rubrik_cdm_node_ip`
* `rubrik_cdm_token`

| Note: The `rubrik_cdm_username` and `rubrik_cdm_password` must be supplied together and may not be provided if the `rubrik_cdm_token` variable is present|
| --- |

You can also set these values in the config.json. 

The modules mv_user.py and mv_migrate.py require that the `rubrik_cdm_username` be a user with admin privileges. 
For the module mv_info.py the `rubrik_cdm_username` can be either an admin user or a user with the managed_volume_admin or managed_volume_user role covering the managed volumes of interest.

You can also set a second user `mv_end_user_username` that the mv_info.py module will use in the snapshot commands.

Basic managed volume info:
`$ mv_info managed_volume_name`

Managed volume status:
`$ mv_info managed_volume_name --state`

Setup details for a managed volume:
`$ mv_info managed_volume_name --full`

To interactively add the managed_volume_user role to a user:
`$ mv_user username`

To create a new user and then interactively add the managed_volume_user role to a user:
`$ mv_user username --create`

To simply add Globall:All managed_volume_user role to a user:
`$ mv_user username --add_all`

To migrate a managed volume to a new managed volume:
`$ mv_migrate managed_volume_name`
That will rename the managed volume to the managed volume name + the `rename_postfix` value from the config.json file. 
It will then create a new managed volume with the same name, characteristics, and SLA as the original. 
The new managed volume will use the application tag `applicationTag` value from the config.json file.
