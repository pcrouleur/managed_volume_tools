import rubrik_cdm
import click
import os
import sh
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)
if not config['rubrik_cdm_node_ip']:
    config['rubrik_cdm_node_ip'] = None
rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'], config['rubrik_cdm_token'])


@click.command()
@click.argument('managed_volume_name')
def cli(managed_volume_name):
    print(managed_volume_name)
    managed_volume_info = get_managed_volume_info(managed_volume_name)
    pass


def get_managed_volume_info(managed_volume_name):
    # Get managed volume id
    managed_volume_id = rubrik.object_id(managed_volume_name, 'managed_volume')
    # Get the managed volume details
    managed_volume_info = rubrik.get('internal', '/managed_volume/{}'.format(managed_volume_id))
    return managed_volume_info


def print_mounts(name, channels):
    print("# Add these lines to /etc/fstab on linux hosts")
    for number, channel in enumerate(channels):
        print(
            "{}:{}  {}/{}-ch{}  nfs {} 0 0".format(
                channel['ipAddress'], channel['mountPoint'], config['nfs_mount_path'] , name, number, config['nfs_mount_options']))
    print()
    print("# Make the mount points.")
    for number, channel in enumerate(channels):
        print("mikdir -p {}/{}-ch{}".format(config['nfs_mount_path'], name, number))

    print()
    print("# Mount the NFS exports.")
    for number, channel in enumerate(channels):
        print("mount {}/{}-ch{}".format(config['nfs_mount_path'], name, number))
    print()


def check_mounts(name, channels):
    unmounted = None
    missing = None
    for number, channel in enumerate(channels):
        if not os.path.ismount("{}/{}-ch{}".format(config['nfs_mount_path'], name, number)):
            unmounted = True
            print("The mount point {}/{}-ch{} is not mounted on this host.".format(config['nfs_mount_path'], name, number))
            if not os.path.exists("{}/{}-ch{}".format(config['nfs_mount_path'], name, number)):
                missing = True
                print("The mount point {}/{}-ch{} does not exit on this host.".format(config['nfs_mount_path'], name, number))
    return unmounted, missing


def make_mounts(name, channels):
    for number, channel in enumerate(channels):
        try:
            sh.mkdir('-p', "{}/{}-ch{}".format(config['nfs_mount_path'], name, number))
        except ErrorReturnCode:
            print("There as an unknown error with the sh.mkdir command")


def mount_nfs(name, channels):
    for number, channel in enumerate(channels):
        try:
            sh.mount('-tnfs', '-o{}'.format(config['nfs_mount_options']),
                     "{}:{}".format(channel['ipAddress'], channel['mountPoint']),
                     "{}/{}-ch{}".format(config['nfs_mount_path'], name, number))
        except ErrorReturnCode:
            print("There as an unknown error with the sh.mount command")