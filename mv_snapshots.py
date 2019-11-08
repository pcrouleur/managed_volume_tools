import rubrik_cdm
import click
import json
import time as pytime
from datetime import datetime
from pytz import timezone
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)
if not config['rubrik_cdm_node_ip']:
    config['rubrik_cdm_node_ip'] = None
rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'], config['rubrik_cdm_token'])


@click.command()
@click.argument('managed_volume_name')
@click.option('--time', '-t', is_flag=False, help='Snapshot time')
@click.option('--host', '-h', is_flag=False, help='Host name pattern')
def cli(managed_volume_name, time, host):
    # Get the managed volume id using the managed volume name
    managed_volume_id = rubrik.object_id(managed_volume_name, 'managed_volume')
    print("Managed Volume: {}, Managed Volume ID: {}, Timestamp: {}".format(managed_volume_name, managed_volume_id, time))
    # Get the snapshot summary info for this managed volume
    snapshots = get_managed_volume_snapshots(managed_volume_id)
    # Convert input time to datetime object
    if time:
        target_datetime = datetime.strptime(time, '%m%d%Y%H%M%S')
        # Add the timezone localization
        local_timezone = timezone('America/New_York')
        target_datetime_timezone = local_timezone.localize(target_datetime)
    else:
        target_datetime_timezone = ''
    # Sort List - possibly unnecessary
    sorted_snapshots = sorted(snapshots, key=lambda k: k['datetime'])
    # If requested time is given get first snapshot after the requested time
    if target_datetime_timezone:
        for snap in sorted_snapshots:
            if snap['datetime'] > target_datetime_timezone:
                found_snap = snap
                break
    else:
        found_snap = sorted_snapshots[-1]
    print("Snapshot found. Date: {}, Snapshot ID: {}".format(found_snap['date'], found_snap['id']))
    # Export the snapshot
    # set host to all if not specified
    if not host:
        host = '*'
    # Build the config
    payload = {
        "hostPatterns": [host],
        "shareType": "NFS"
    }
    export = rubrik.post('internal', '/managed_volume/snapshot/{}/export'.format(found_snap['id']), payload)
    print("Export Status is: {}".format(export['status']))
    # If the status was not QUEUED then exit
    if export['status'] != 'QUEUED':
        print("Snapshot export operation failed with status {}".format(export['status']))
        exit(1)
    # Get the details of the managed volume snapshot export,
    # Check after 60 seconds and then ever 60 seconds for 5 minutes
    snap_export = ''
    for x in range(0, 5):
        pytime.sleep(60)
        mv_exports = rubrik.get('internal', '/managed_volume/snapshot/export?source_managed_volume_id={}'.format(managed_volume_id))
        for mv_export in mv_exports['data']:
            if mv_export['snapshotId'] == found_snap['id']:
                snap_export = mv_export
                print("Snapshot Channels to Mount: {}".format(snap_export['channels']))
                print("Snapshot export id used to unmount: {}".format(snap_export['id']))
                break
        if snap_export:
            break
        else:
            print("Waiting on export, check {}".format(x + 1))
    if not snap_export:
        print("Timeout: Export not found.")


def get_managed_volume_snapshots(managed_volume_id):
    # Get the managed volume details
    snap_time_ids = []
    for snap in rubrik.get('internal', '/managed_volume/{}/snapshot'.format(managed_volume_id))['data']:
        snap_time_id = {'date': snap['date'], 'id': snap['id'], 'datetime': rubrik_to_datetime(snap['date'])}
        snap_time_ids.append(snap_time_id)
    return snap_time_ids


def rubrik_to_datetime(time_string):
    return datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('UTC'))


if __name__ == "__main__":
    cli()