import rubrik_cdm, argparse
import urllib3
urllib3.disable_warnings()

# Variables
rubrik_address = '172.21.8.51'
rubrik_user = 'admin'
rubrik_password = 'C0d34fun!'
subnet = None
nfs_mount_path = '/mnt/rubrik'
nfs_mount_options = 'rw,bg,hard,nointr,rsize=1048576,wsize=1048576,tcp,vers=3,timeo=600,actimeo=0,noatime'

# Get Arguments
parser = argparse.ArgumentParser(description='Get managed volume id and channels.')
parser.add_argument('managed_volume_name', type=str, help='Managed volume name')
parser.add_argument('-f', '--full', action='store_true', help='Print out full mount steps')
arguments = parser.parse_args()
managed_volume_name = arguments.managed_volume_name
full = arguments.full


# Get Rubrik connection
rubrik = rubrik_cdm.Connect(rubrik_address, rubrik_user, rubrik_password)
# Get managed volume id
managed_volume_id = rubrik.object_id(managed_volume_name, 'managed_volume')
# Get the managed volume details
managed_volume_info = rubrik.get('internal', '/managed_volume/{}'.format(managed_volume_id))

print('-' * 50)
print(managed_volume_info['id'])
print('-' * 50)
if managed_volume_info['state'] == 'Exported' and not full:
    for channel in managed_volume_info['mainExport']['channels']:
        print("{}:{}".format(channel['ipAddress'], channel['mountPoint']))
    print('-' * 50)
elif managed_volume_info['state'] == 'Exported' and full:
    print("# Add these lines to /etc/fstab on linux hosts")
    for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
        print("{}:{}  {}/{}-ch{}  nfs {} 0 0".format(
                channel['ipAddress'],
                channel['mountPoint'],
                nfs_mount_path, managed_volume_name, number, nfs_mount_options))
    print('-' * 50)
    print("# Make the mount points.")
    for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
        print("mikdir -p {}/{}-ch{}".format(nfs_mount_path, managed_volume_name, number))

    print('-' * 50)
    print("# Mount the NFS exports.")
    for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
        print("mount {}k/{}-ch{}".format(nfs_mount_path, managed_volume_name, number))
    print('-' * 50)
    print("RMAN channels to use in backup scripts:")
    for number, channel in enumerate(managed_volume_info['mainExport']['channels']):
        print(
            "allocate channel ch{} device type disk format '{}/{}-ch{}/%U';".format(number, nfs_mount_path,
                managed_volume_name, number))
    print('-' * 50)
else:
    print("The managed volume has not been exported yet")