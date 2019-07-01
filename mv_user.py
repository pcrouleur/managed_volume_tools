
""" This script comes with no warranty use at your own risk
    This script will list the managed volumes under the managed volume user role.
    It will add (or delete) the entered managed volumes or all the managed
    volumes to the managed volume user role.
    This user should have admin privileges to make these changes. This is not the user we
    are adding the managed volume role to.
"""
import rubrik_cdm
import click
import json
import urllib3
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)
rubrik = rubrik_cdm.Connect(config['rubrik_cdm_node_ip'], config['rubrik_cdm_username'], config['rubrik_cdm_password'])


@click.command()
@click.argument('user_name')
@click.option('--add_all', '-a', is_flag=True, help='Add Global:All managed_volume_user to user.')
@click.option('--create', '-c', is_flag=True, help='Create the user.')
def cli(user_name, add_all, create):
    print("Getting information for user '{}'.".format(user_name))
    user = rubrik.get('internal', '/user?username={}'.format(user_name))
    if user:
        user = user[0]
        print("Found user '{}' with id '{}'".format(user['username'], user['id']))
        if create:
            print("User already exists. Cannot create new user with same name.")
            exit(1)
    elif create:
        print("User not found. Creating new user: '{}".format(user_name))
        user = create_user(user_name)
        #print(user)
        #user = rubrik.get('internal', '/user?username={}'.format(user_name))[0]
    else:
        print("Invalid User Name or User Name '{}' Does Not Exist On This Cluster...\n".format(user_name))
        while True:
            user_name = click.prompt('Please enter a user name', type=str)
            user = rubrik.get('internal', '/user?username={}'.format(user_name))
            if user:
                user = user[0]
                print("Found user '{}' with id '{}'".format(user['username'], user['id']))
                break
            else:
                print("Invalid User Name or User Name Does Not Exist ...\n")
    if add_all:
        managed_volumes = ["Global:::All"]
        add_privileges(user, managed_volumes)
    else:
        while True:
            action = click.prompt('List(L), Add(A) or Delete(D) Managed Volume access (q or Q to quit)', type=str)
            if action == 'List' or action == 'list' or action == 'L' or action == 'l':
                role = 'managed_volume_user'
                roles, org_id = list_managed_volumes(user)
                if roles:
                    print("The following objects are added to the {} role for the {} user: ".format(role, user_name))
                    print(','.join(map(str, roles)) + "\n")
                else:
                    print("There are no objects added to the {} role for the {} user.".format(role, user_name))
            elif action == 'Add' or action == 'add' or action == 'A' or action == 'a':
                # Get the managed volume names to add to the role from input
                managed_volumes = click.prompt("Enter comma separated list of managed volumes to add or 'all' for Global:::All", type=str).split(',')
                if managed_volumes[0] == 'q' or managed_volumes[0] == 'Q':
                    exit(0)
                add_privileges(user, managed_volumes)
            elif action == 'Delete' or action == 'delete' or action == 'D' or action == 'd':
                managed_volumes = click.prompt('Enter comma separated list of managed volumes to delete', type=str).split(',')
                if managed_volumes[0] == 'q' or managed_volumes[0] == 'Q':
                    exit(0)
                delete_privileges(user, managed_volumes)
            elif action == 'q' or action == 'Q':
                exit(0)
            else:
                print("Invalid Response ...")


def create_user(user_name):
    password = click.prompt('Please enter a password', type=str, confirmation_prompt=True)
    if len(password) < 8:
        print("Password is too short")
        password = click.prompt('Please enter a password', type=str, confirmation_prompt=True)
    print("User '{}' with password '{}' will be created".format(user_name, password))
    user = rubrik.create_user(user_name, password)
    print(user)
    if not user['id']:
        print(user['errorType'])
    return user


def list_managed_volumes(user):
    """ Gets the mv names of a list of managed volume ids

    Args:
    user: The user parameter  dictionary as returned from a get on the user

    Returns:
            A list of managed volume user privileges.
    """
    role_mvs = rubrik.get('internal', "/authorization/role/managed_volume_user?principals={}".format(user['id']))
    mvs = []
    for mv_id in role_mvs['data'][0]['privileges']['basic']:
        if mv_id == 'Global:::All':
            mvs.append(mv_id)
        else:
            mv = rubrik.get('internal', "/managed_volume/{}".format(mv_id))
            mvs.append(mv['name'])

    return [mvs, role_mvs['data'][0]['organizationId']]


def add_privileges(user, managed_volumes):
    """ Adds a list of managed volume ids to a user's
            managed volume user role

            Args:
            user: The user parameter  dictionary as returned from a get on the user
            managed_volumes: The list of managed volume full ids [(ManagedVolume:::cca84f33-4dd3-4cdb-9989-e1bee53be794),]

            Returns: 0
    """
    if  managed_volumes == ['All'] or managed_volumes == ['all'] or managed_volumes == ['ALL'] or managed_volumes == ["Global:::All"]:
        mv_list = ["Global:::All"]
        print("All managed volumes (Global:::All) will be added to the managed volume user role for {}".format(user['username']))
    else:
        mv_list = []
        for mv_name in managed_volumes:
            try:
                mv_list.append(rubrik.get('internal', "/managed_volume?name={}".format(mv_name))['data'][0]['id'])
                print("Added managed volume {} to the managed volume user role for {}".format(mv_name, user['username']))
            except(IndexError, TypeError):
                print("The managed volume name {} does not exist and will be skipped ...".format(mv_name))
                return 1

    auth_policy = {
        "principals": [
            user['id']
        ],
        "privileges": {
            "basic": mv_list
        }
    }

    # Update the managed volume user role
    rubrik.post('internal', '/authorization/role/managed_volume_user', auth_policy)
    # Print out the confirmation
    print("Complete - managed volume user role has been updated for {}.\n".format(user['username']))
    return 0


def delete_privileges(user, managed_volumes):
    """ Deletes a list of managed volume ids from a user's
            managed volume user role

            Args:
            user: The user parameter  dictionary as returned from a get on the user
            managed_volumes: The list of managed volume full ids [(ManagedVolume:::cca84f33-4dd3-4cdb-9989-e1bee53be794),]

            Returns: 0
    """
    if not managed_volumes:
        print("No managed volumes given to delete from the managed volume user role for {}.\n".format(user['username']))
    else:
        mv_list = []
        for mv_name in managed_volumes:
            if mv_name == "Global:::All":
                mv_list.append(mv_name)
                print("Working on deleting {} from the managed volume user role for {}".format(mv_name, user['username']))
            else:
                try:
                    mv_list.append(rubrik.get('internal', "/managed_volume?name={}"
                                                   .format(mv_name))['data'][0]['id'])
                    print("Working on deleting managed volume {} from the managed volume user role for {}.".format(mv_name, user['username']))
                except(IndexError, TypeError):
                    print("The managed volume name {} does not exist and will be skipped ...".format(mv_name))

    organization_id = list_managed_volumes(user)[1]
    # Build the auth_policy data model to POST to the role
    auth_policy = {
        "principals": [
            user['id']
        ],
        "privileges": {
            "basic": mv_list
        },
        "organizationId": organization_id
    }
    # Update the managed volume user role with the delete
    try:
        rubrik.delete('internal', '/authorization/role/managed_volume_user', config=auth_policy)
        print("Complete - managed volume user role has been updated for {}.\n".format(user['username']))
    except():
        print("There was an error deleting the managed_volumes {} from the managed_volume_user role ..."
              .format(managed_volumes))

    return 0


if __name__ == "__main__":
    cli()
