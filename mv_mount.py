import rubrik_cdm
import click
import json
import os
import subprocess
import sys
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)
if not config['rubrik_cdm_node_ip']:
    config['rubrik_cdm_node_ip'] = None
rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'], config['rubrik_cdm_token'])


@click.command()
@click.argument('managed_volume_name')
@click.option('--mount', '-m', is_flag=True, help='Print full mount steps')
@click.option('--unmount', '-u', is_flag=True, help='Print managed volume state')
def cli(managed_volume_name, mount, unmount):
    managed_volume_info = get_managed_volume_info(managed_volume_name)
    mounted, mount_points_exist = check_mounts(managed_volume_name, managed_volume_info['mainExport']['channels'])
    if mount:
        print("Mounting NFS shares for managed volume '{}'.".format(managed_volume_name))
        if not mount_points_exist:
            make_mounts(managed_volume_name, managed_volume_info['mainExport']['channels'])
        if not mounted:
            mount_nfs(managed_volume_name, managed_volume_info['mainExport']['channels'])
    elif unmount:
        print("Unmounting NFS shares for managed volume '{}'.".format(managed_volume_name))
        unmount_nfs(managed_volume_name, managed_volume_info['mainExport']['channels'])
        remove_mounts(managed_volume_name, managed_volume_info['mainExport']['channels'])
    else:
        print("Channel information for managed volume '{}'.".format(managed_volume_name))
        print_mounts(managed_volume_name, managed_volume_info['mainExport']['channels'])


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
                channel['ipAddress'], channel['mountPoint'], config['nfs_mount_path'] , name, number,
                config['nfs_mount_options']))
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
    mounted = False
    mount_points_exist = False
    for number, channel in enumerate(channels):
        if os.path.ismount("{}/{}-ch{}".format(config['nfs_mount_path'], name, number)):
            mounted = True
            mount_points_exist = True
        else:
            if os.path.exists("{}/{}-ch{}".format(config['nfs_mount_path'], name, number)):
                mount_points_exist = True
    return mounted, mount_points_exist


def make_mounts(name, channels):
    uid = os.getuid()
    if uid == 0:
        for number, channel in enumerate(channels):
            try:
                return_code = subprocess.call("mkdir " + "-p {}/{}-ch{}".format(config['nfs_mount_path'],
                                                                                name, number), shell=True)
                if return_code != 0:
                    print("Child was terminated by signal", -return_code, file=sys.stderr)
                    return 1
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)
                return 1
    else:
        for number, channel in enumerate(channels):
            try:
                return_code = subprocess.call("sudo mkdir " + "-p {}/{}-ch{}".format(config['nfs_mount_path'],
                                                                                     name, number), shell=True)
                if return_code != 0:
                    print("Child was terminated by signal", -return_code, file=sys.stderr)
                    return 1
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)
                return 1


def mount_nfs(name, channels):
    uid = os.getuid()
    if uid == 0:
        for number, channel in enumerate(channels):
            try:
                retcode = subprocess.call("mount -t nfs -o {} ".format(config['nfs_mount_options']) +
                                          "{}:{} ".format(channel['ipAddress'], channel['mountPoint']) +
                                          "{}/{}-ch{}".format(config['nfs_mount_path'], name, number), shell=True)
                if retcode != 0:
                    print("Child was terminated by signal", -retcode, file=sys.stderr)
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)
    else:
        for number, channel in enumerate(channels):
            try:
                retcode = subprocess.call("sudo mount -t nfs -o {} ".format(config['nfs_mount_options']) +
                                          "{}:{} ".format(channel['ipAddress'], channel['mountPoint']) +
                                          "{}/{}-ch{}".format(config['nfs_mount_path'], name, number), shell=True)
                if retcode != 0:
                    print("Child was terminated by signal", -retcode, file=sys.stderr)
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)


def unmount_nfs(name, channels):
    uid = os.getuid()
    if uid == 0:
        for number, channel in enumerate(channels):
            try:
                return_code = subprocess.call("umount " +
                                              "{}/{}-ch{}".format(config['nfs_mount_path'], name, number), shell=True)
                if return_code != 0:
                    print("Child was terminated by signal", -return_code, file=sys.stderr)
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)
    else:
        for number, channel in enumerate(channels):
            try:
                return_code = subprocess.call("sudo umount " +
                                              "{}/{}-ch{}".format(config['nfs_mount_path'], name, number), shell=True)
                if return_code != 0:
                    print("Child was terminated by signal", -return_code, file=sys.stderr)
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)


def remove_mounts(name, channels):
    uid = os.getuid()
    if uid == 0:
        for number, channel in enumerate(channels):
            try:
                return_code = subprocess.call("rmdir {}/{}-ch{}".format(config['nfs_mount_path'],
                                                                        name, number), shell=True)
                if return_code != 0:
                    print("Child was terminated by signal", -return_code, file=sys.stderr)
                    return 1
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)
                return 1
    else:
        for number, channel in enumerate(channels):
            try:
                return_code = subprocess.call("sudo rmdir {}/{}-ch{}".format(config['nfs_mount_path'],
                                                                             name, number), shell=True)
                if return_code != 0:
                    print("Child was terminated by signal", -return_code, file=sys.stderr)
                    return 1
            except OSError as e:
                print("Execution failed:", e, file=sys.stderr)
                return 1


if __name__ == "__main__":
    cli()
