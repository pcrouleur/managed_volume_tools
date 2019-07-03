import rubrik_cdm
import click
import json
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)
if not config['rubrik_cdm_node_ip']:
    config['rubrik_cdm_node_ip'] = None
rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'], config['rubrik_cdm_token'])


@click.command()
@click.argument('managed_volume_name')
def main(managed_volume_name):
    # Get managed volume id
    managed_volume_id = rubrik.object_id(managed_volume_name, 'managed_volume')
    # Get the managed volume details
    managed_volume_info = rubrik.get('internal', '/managed_volume/{}'.format(managed_volume_id))
    # Rename the current managed volume
    new_managed_volume_name = managed_volume_name + config['rename_postfix']
    print("Migrating managed volume '{}'. Previous backups will be available on '{}'.".format(managed_volume_name, new_managed_volume_name))
    payload = {"name": new_managed_volume_name}
    rubrik.patch('internal', '/managed_volume/{}'.format(managed_volume_id), payload)
    # Create a new v5 version of the managed volume
    payload = {
      "name": managed_volume_name,
      "applicationTag": config['applicationTag'],
      "numChannels": managed_volume_info['numChannels'],
      "volumeSize": managed_volume_info['volumeSize'],
      "exportConfig": {
        "hostPatterns": managed_volume_info['hostPatterns'],
        "shareType": "NFS"
      }
    }
    if config['subnet'] is not None and config['subnet'] != "":
        payload['subnet'] = config['subnet']
        payload['exportConfig']['subnet'] = config['subnet']
    version5_managed_volume = rubrik.post('internal', '/managed_volume', payload)
    # Set the same protection as the original managed volume
    if managed_volume_info['effectiveSlaDomainId'] != 'UNPROTECTED':
        payload = {
            "managedIds": [
                version5_managed_volume['id']
            ]
        }
        rubrik.post("internal", "/sla_domain/{}/assign".format(managed_volume_info['effectiveSlaDomainId']), payload)
    print("Complete: The managed volume '{}' was renamed to '{}' and a new v5 managed volume '{}' was created.".format(
        managed_volume_name, new_managed_volume_name, managed_volume_name))


if __name__ == "__main__":
    main()
