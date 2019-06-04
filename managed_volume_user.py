#!/usr/bin/env python3
""" This script comes with no warranty use at your own risk
    It requires Rubrik version 4.1
    This script will list the managed volumes under the managed volume user role.
    It will add (or delete) the entered managed volumes or all the managed
    volumes to the managed volume user role.
    It requires a .creds file in the same directory with a credential file of the format:
    {"name": "mycluster", "username": "admin", "password": "Secret123!"}
    This user should have admin privileges to make these changes. This is not the user we
    are adding the managed volume role to.
"""

import managed_volumes

def main():
    # Get the Rubrik user name from input
    while True:
        name = input('Enter User Name or (Q to Quit): ')
        if name ==  'q' or name == 'Q':
            exit(0)
        user = managed_volumes.User(name)
        if user:
            break
        else:
            print("Invalid User Name or User Name Does Not Exist ...\n")

    # Print the Rubrik user name and id
    try:
        user_id = user.id
        user_name = user.username
        print("The user name is {} and the user id is {}.\n".format(user_name,user_id))
    except (IndexError, TypeError):
        print("Invalid User Name")
        exit(1)

    # Process user choice and take action
    while True:
        action = input('List(L), Add(A) or Delete(D) Managed Volume access? (Q to Quit): ')
        if action == 'List' or action == 'list' or action == 'L' or action == 'l':
            role = 'managed_volume_user'
            roles, org_id = user.list_managed_volumes(role)
            if roles:
                print("The following objects are added to the {} role for the {} user: ".format(role, user_name))
                print(','.join(map(str, roles)) + "\n")
            else:
                print("There are no objects added to the {} role for the {} user.".format(role, user_name))
            role = 'managed_volume_admin'
            roles, org_id = user.list_managed_volumes(role)
            if roles:
                print("The following objects are added to the {} role for the {} user: ".format(role, user_name))
                print(','.join(map(str, roles)) + "\n")
            else:
                print("There are no objects added to the {} role for the {} user.".format(role, user_name))
        elif action == 'Add' or action == 'add' or action == 'A' or action == 'a':
            # Get the managed volume names to add to the role from input
            managed_volumes = input('Enter comma separated list of managed volumes to add (blank for all): ').split(',')
            user.add_privileges(managed_volumes)
        elif action == 'Delete' or action == 'delete' or action == 'D' or action == 'd':
            managed_volumes = input('Enter comma separated list of managed volumes to delete: ').split(',')
            user.delete_privileges(managed_volumes)
        elif action == 'q' or action == 'Q':
            exit(0)
        else:
            print("Invalid Response ...")


# Start program
if __name__ == "__main__":
    main()