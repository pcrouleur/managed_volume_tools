import rubrik_cdm
import click
import json
import base64
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)
if not config['rubrik_cdm_node_ip']:
    config['rubrik_cdm_node_ip'] = None
rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'], config['rubrik_cdm_token'])


@click.command()
@click.argument('managed_volume_name')
@click.option('--full', '-f', is_flag=True, help='Print full mount steps')
@click.option('--state', '-s', is_flag=True, help='Print managed volume state')
def cli(managed_volume_name, full, state):
    managed_volume_info = get_managed_volume_info(managed_volume_name)
    if state:
        print_managed_volume_state(managed_volume_info)
    elif full:
        print_managed_volume_setup(managed_volume_info)
        if config['mv_end_user_username'] and config['mv_end_user_password']:
            print_managed_volume_snapshot(config['mv_end_user_username'], config['mv_end_user_password'], rubrik.node_ip, managed_volume_info['id'])
        else:
            print_managed_volume_snapshot(rubrik.username, rubrik.password, rubrik.node_ip, managed_volume_info['id'])
    else:
        print_managed_volume_info(managed_volume_info)


def get_managed_volume_info(managed_volume_name):
    # Get managed volume id
    managed_volume_id = rubrik.object_id(managed_volume_name, 'managed_volume')
    # Get the managed volume details
    managed_volume_info = rubrik.get('internal', '/managed_volume/{}'.format(managed_volume_id))
    return managed_volume_info


def print_managed_volume_info(managed_volume_info):
    print('-' * 50)
    print(managed_volume_info['id'])
    print('-' * 50)
    if managed_volume_info['state'] == 'Exported':
        for channel in managed_volume_info['mainExport']['channels']:
            print("{}:{}".format(channel['ipAddress'], channel['mountPoint']))
        print('-' * 50)
    else:
        print("The managed volume has not been exported yet")


def print_managed_volume_setup(managed_volume_info):
    print('-' * 50)
    print(managed_volume_info['id'])
    print('-' * 50)
    if managed_volume_info['state'] == 'Exported':
        print("# Add these lines to /etc/fstab on linux hosts")
        for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
            print("{}:{}  {}/{}-ch{}  nfs {} 0 0".format(
                channel['ipAddress'],
                channel['mountPoint'],
                config['nfs_mount_path'], managed_volume_info['name'], number, config['nfs_mount_options']))
        print('-' * 50)
        print("# Make the mount points.")
        for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
            print("mkdir -p {}/{}-ch{}".format(config['nfs_mount_path'], managed_volume_info['name'], number))

        print('-' * 50)
        print("# Mount the NFS exports.")
        for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
            print("mount {}/{}-ch{}".format(config['nfs_mount_path'], managed_volume_info['name'], number))
        print('-' * 50)
        print("# RMAN channels to use in backup scripts:")
        for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
            print(
                "allocate channel ch{} device type disk format '{}/{}-ch{}/%U';".format(number, config['nfs_mount_path'],
                                                                                        managed_volume_info['name'], number))
        print('-' * 50)
    else:
        print("The managed volume has not been exported yet")


def print_managed_volume_state(managed_volume_info):
    if managed_volume_info['isWritable']:
        snapshot_state = "Writable"
    else:
        snapshot_state = "Read Only"
    print("The current state of the {} managed volume is {} and the managed volume is {}".format(managed_volume_info['name'], managed_volume_info['state'], snapshot_state))


def print_managed_volume_snapshot(username, password, rubrik_ip, managed_volume_id):
    user_pass = username + ':' + password
    b_user_pass = user_pass.encode()
    enc_user_pass = base64.b64encode(b_user_pass).decode()
    print("# Rubrik user in snapshot command: {}".format(username))
    print("# This is set in the config.json file (mv_end_user_username,mv_end_user_password)")
    print("# The begin snapshot ReST API command is:")
    print(
        "curl -k -X POST -H 'Authorization: Basic {}' 'https://{}/api/internal/managed_volume/{}/begin_snapshot'".format(
            enc_user_pass, rubrik_ip, managed_volume_id))
    print("# The end snapshot ReST API command is:")
    print(
        "curl -k -X POST -H 'Authorization: Basic {}' 'https://{}/api/internal/managed_volume/{}/end_snapshot'".format(
            enc_user_pass, rubrik_ip, managed_volume_id))

if __name__ == "__main__":
    cli()
