# !/usr/bin/env python3
""" This script comes with no warranty use at your own risk
    It requires Rubrik_CDM
"""

import rubrik_cdm
import json
import urllib3
import base64

# import sh
#import os
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)


class ManagedVolume(rubrik_cdm.Connect):
    def __init__(self, name):
        #super().__init__(connect)
        self.name = name
        self.rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'])
        self.cluster = self.rubrik.get('v1', '/cluster/me')
        self.data = self.rubrik.get('internal', '/managed_volume?name={}'.format(self.name))
        try:
            self.data['data'][0]['name']
        except IndexError:
            self.data = None
        if self.data:
            self.data = self.data['data'][0]
            self.effectiveSlaDomainId = self.data['effectiveSlaDomainId']
            self.primaryClusterId = self.data['primaryClusterId']
            self.usedSize = self.data['usedSize']
            self.mainExport = self.data['mainExport']
            self.configuredSlaDomainId = self.data['configuredSlaDomainId']
            self.isWritable = self.data['isWritable']
            self.shareType = self.data['shareType']
            self.volumeSize = self.data['volumeSize']
            self.effectiveSlaDomainName = self.data['effectiveSlaDomainName']
            self.isDeleted = self.data['isDeleted']
            self.hostPatterns = self.data['hostPatterns']
            self.links = self.data['links']
            self.id = self.data['id']
            self.state = self.data['state']
            self.configuredSlaDomainName = self.data['configuredSlaDomainName']
            self.slaAssignment = self.data['slaAssignment']
            if 'applicationTag' in self.data:
                self.applicationTag = self.data['applicationTag']
            self.snapshotCount = self.data['snapshotCount']
            self.pendingSnapshotCount = self.data['pendingSnapshotCount']
            self.isRelic = self.data['isRelic']
            self.isActive = self.data['mainExport']['isActive']
            self.channels = self.data['mainExport']['channels']

    def cluster_info(self):
        self.cluster = self.rubrik.get('v1', '/cluster/me')
        return self

    def refresh(self):
        self.data = self.rubrik.get('internal', '/managed_volume?name={}'.format(self.name))
        try:
            self.data['data'][0]['name']
        except IndexError:
            self.data = None
            return None
        if self.data:
            self.data = self.data['data'][0]
            self.effectiveSlaDomainId = self.data['effectiveSlaDomainId']
            self.primaryClusterId = self.data['primaryClusterId']
            self.usedSize = self.data['usedSize']
            self.mainExport = self.data['mainExport']
            self.configuredSlaDomainId = self.data['configuredSlaDomainId']
            self.isWritable = self.data['isWritable']
            self.shareType = self.data['shareType']
            self.volumeSize = self.data['volumeSize']
            self.effectiveSlaDomainName = self.data['effectiveSlaDomainName']
            self.isDeleted = self.data['isDeleted']
            self.hostPatterns = self.data['hostPatterns']
            self.links = self.data['links']
            self.id = self.data['id']
            self.state = self.data['state']
            self.configuredSlaDomainName = self.data['configuredSlaDomainName']
            self.slaAssignment = self.data['slaAssignment']
            if 'applicationTag' in self.data:
                self.applicationTag = self.data['applicationTag']
            self.snapshotCount = self.data['snapshotCount']
            self.pendingSnapshotCount = self.data['pendingSnapshotCount']
            self.isRelic = self.data['isRelic']
            self.isActive = self.data['mainExport']['isActive']
            self.channels = self.data['mainExport']['channels']
        return self

    def print_mounts(self):
        print('#' * 80)
        print("# Add these lines to /etc/fstab on linux hosts")
        for number, channel in enumerate(self.channels):
            print(
                "{}:{}  {}/{}-ch{}  nfs {} 0 0".format(
                    channel['ipAddress'], channel['mountPoint'], config['nfs_mount_path'], self.name, number, config['nfs_mount_options']))
        print('#' * 80)
        print("# Make the mount points.")
        for number, channel in enumerate(self.channels):
            print("mikdir -p {}/{}-ch{}".format(config['nfs_mount_path'], self.name, number))

        print('#' * 80)
        print("# Mount the NFS exports.")
        for number, channel in enumerate(self.channels):
            print("mount {}k/{}-ch{}".format(config['nfs_mount_path'], self.name, number))
        print('#' * 80)

    def print_snapshot_cmds(self):
        print('#' * 80)
        user_pass = config['rubrik_cdm_username'] + ':' + config['rubrik_cdm_password']
        b_user_pass = user_pass.encode()
        enc_user_pass = base64.b64encode(b_user_pass).decode()
        print("# The begin snapshot ReST API command is:")
        print("curl -k -X POST -H 'Authorization: Basic {}' 'https://{}/api/internal/managed_volume/{}/begin_snapshot'".format(enc_user_pass, config['rubrik_cdm_node_ip'], self.id))
        print("# The end snapshot ReST API command is:")
        print("curl -k -X POST -H 'Authorization: Basic {}' 'https://{}/api/internal/managed_volume/{}/end_snapshot'".format(enc_user_pass, config['rubrik_cdm_node_ip'], self.id))
        print('#' * 80)

    def print_rman_channels(self):
        print("RMAN channels to use in backup scripts:")
        for number, channel in enumerate(self.channels):
            print(
                "allocate channel ch{} device type disk format '{}/{}-ch{}/%U';".format(number, config['nfs_mount_path'], self.name, number))
        print('#' * 80)

    def begin_snapshot(self):
        begin_snap = self.rubrik.begin_managed_volume_snapshot(self.name)
        return begin_snap

    def end_snapshot(self):
        end_snap = self.rubrik.end_managed_volume_snapshot(self.name)
        return end_snap


class User(rubrik_cdm.Connect):
    def __init__(self, name):
        self.name = name
        self.rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'], enable_logging=False)
        self.cluster = self.rubrik.get('v1', '/cluster/me')
        self.data = self.rubrik.get('internal', '/user?username={}'.format(self.name))
        try:
            self.data[0]['id']
        except IndexError:
            self.data = None
        if self.data:
            self.id = self.data[0]['id']
            self.authDomainId = self.data[0]['authDomainId']
            self.username = self.data[0]['username']
            self.emailAddress = self.data[0]['emailAddress']
            self.organization_id = self.rubrik.get('internal', '/user/me/organization')['data'][0]['id']

    def list_managed_volumes(self):
        """ Gets the mv names of a list of managed volume ids

            Args:
            name: The list of managed volume full ids [(ManagedVolume:::cca84f33-4dd3-4cdb-9989-e1bee53be794),]

            Returns:
                    A list of managed volume user privileges.
        """
        role_mvs = self.rubrik.get('internal', "/authorization/role/managed_volume_user?principals={}".format(self.id))
        mvs = []
        for mv_id in role_mvs['data'][0]['privileges']['basic']:
            if mv_id == 'Global:::All':
                mvs.append(mv_id)
            else:
                mv = self.rubrik.get('internal', "/managed_volume/{}".format(mv_id))
                mvs.append(mv['name'])

        return [mvs, role_mvs['data'][0]['organizationId']]

    def add_privileges(self, managed_volumes):
        """ Adds a list of managed volume ids to a user's
                managed volume user role

                Args:
                managed_volumes: The list of managed volume full ids [(ManagedVolume:::cca84f33-4dd3-4cdb-9989-e1bee53be794),]

                Returns: 0
        """
        if not managed_volumes or managed_volumes == ['']:
            mv_list = ["Global:::All"]
            print("All managed volumes (Global:::All) will be added to the managed volume user role for {}".format(self.username))
        else:
            mv_list = []
            for mv_name in managed_volumes:
                try:
                    mv_list.append(self.rubrik.get('internal', "/managed_volume?name={}".format(mv_name))['data'][0]['id'])
                    print("Added managed volume {} to the managed volume user role for {}".format(mv_name, self.username))
                except(IndexError, TypeError):
                    print("The managed volume name {} does not exist and will be skipped ...".format(mv_name))
                    return 1

        auth_policy = {
            "principals": [
                self.id
            ],
            "privileges": {
                "basic": mv_list
            }
        }

        # Update the managed volume user role
        self.rubrik.post('internal', '/authorization/role/managed_volume_user', auth_policy)
        # Print out the confirmation
        print("Complete - managed volume user role has been updated for {}.\n".format(self.username))
        return 0

    def delete_privileges(self, managed_volumes):
        """ Deletes a list of managed volume ids from a user's
                managed volume user role

                Args:
                managed_volumes: The list of managed volume full ids [(ManagedVolume:::cca84f33-4dd3-4cdb-9989-e1bee53be794),]

                Returns: 0
        """
        if not managed_volumes:
            print("No managed volumes given to delete from the managed volume user role for {}.\n".format(self.username))
        else:
            mv_list = []
            for mv_name in managed_volumes:
                if mv_name == "Global:::All":
                    mv_list.append(mv_name)
                    print("Working on deleting {} from the managed volume user role for {}".format(mv_name, self.username))
                else:
                    try:
                        mv_list.append(self.rubrik.get('internal', "/managed_volume?name={}"
                                                       .format(mv_name))['data'][0]['id'])
                        print("Working on deleting managed volume {} from the managed volume user role for {}.".format(mv_name,
                                                                                                            self.username))
                    except(IndexError, TypeError):
                        print("The managed volume name {} does not exist and will be skipped ...".format(mv_name))

        organization_id = self.list_managed_volumes()[1]
        # Build the auth_policy data model to POST to the role
        auth_policy = {
            "principals": [
                self.id
            ],
            "privileges": {
                "basic": mv_list
            },
            "organizationId": organization_id
        }
        # Update the managed volume user role with the delete
        try:
            self.rubrik.delete('internal', '/authorization/role/managed_volume_user', config=auth_policy)
            print("Complete - managed volume user role has been updated for {}.\n".format(self.username))
        except():
            print("There was an error deleting the managed_volumes {} from the managed_volume_user role ..."
                  .format(managed_volumes))

        return 0

