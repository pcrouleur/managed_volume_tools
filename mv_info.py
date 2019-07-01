import rubrik_cdm
import click
import json
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)


@click.command()
@click.argument('managed_volume')
@click.option('--full', '-f', is_flag=True, help='Print full mount steps')
@click.option('--state', '-s', is_flag=True, help='Print managed volume state')
def cli(managed_volume, full, state):
    managed_volume_info = get_managed_volume_info(managed_volume)
    if state:
        print_managed_volume_state(managed_volume_info)
    elif full:
        print_managed_volume_setup(managed_volume_info)
    else:
        print_managed_volume_info(managed_volume_info)


def get_managed_volume_info(managed_volume_name):
    rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'])
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
            print("mikdir -p {}/{}-ch{}".format(config['nfs_mount_path'], managed_volume_info['name'], number))

        print('-' * 50)
        print("# Mount the NFS exports.")
        for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
            print("mount {}k/{}-ch{}".format(config['nfs_mount_path'], managed_volume_info['name'], number))
        print('-' * 50)
        print("RMAN channels to use in backup scripts:")
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


if __name__ == "__main__":
    cli()