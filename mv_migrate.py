import rubrik_cdm, argparse
import urllib3
urllib3.disable_warnings()
subnet = None

parser = argparse.ArgumentParser(description='Script to migrate managed volumes to v5.')
parser.add_argument('managed_volume_name', type=str, help='Managed volume to be migrated')
arguments = parser.parse_args()
managed_volume_name = arguments.managed_volume_name

# Get Rubrik connection
rubrik = rubrik_cdm.Connect('172.21.8.51', 'admin', 'C0d34fun!')
# Get managed volume id
managed_volume_id = rubrik.object_id(managed_volume_name, 'managed_volume')
# Get the managed volume details
managed_volume_info = rubrik.get('internal', '/managed_volume/{}'.format(managed_volume_id))
# Rename the current managed volume
new_managed_volume_name = managed_volume_name + '_v4'
print("Migrating managed volume '{}'. Previous backups will be available on '{}'.".format(managed_volume_name, new_managed_volume_name))
payload = {"name": new_managed_volume_name}
version4_managed_volume = rubrik.patch('internal', '/managed_volume/{}'.format(managed_volume_id), payload)
# Create a new v5 version of the managed volume
payload = {
  "name": managed_volume_name,
  "applicationTag": "Oracle",
  "numChannels": managed_volume_info['numChannels'],
  "subnet": subnet,
  "volumeSize": managed_volume_info['volumeSize'],
  "exportConfig": {
    "hostPatterns": managed_volume_info['hostPatterns'],
    "subnet": subnet,
    "shareType": "NFS"
  }
}
if subnet:
    payload['subnet'] = subnet
    payload['exportConfig']['subnet'] = subnet
version5_managed_volume = rubrik.post('internal', '/managed_volume', payload)
# Set the same protection as the original managed volume
if managed_volume_info['effectiveSlaDomainId'] != 'UNPROTECTED':
    payload = {
        "managedIds": [
            version5_managed_volume['id']
        ]
    }
    rubrik.post("internal", "/sla_domain/{}/assign".format(managed_volume_info['effectiveSlaDomainId']), payload)