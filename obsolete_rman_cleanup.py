# !/usr/bin/env python3
""" This script comes with no warranty use at your own risk
    It requires Rubrik cx_Oracle
    This script will remove an orphaned backup pieces from the backp path locations
"""

import cx_Oracle
from os import listdir, remove
from os.path import isfile, join

paths = ['/mnt/rubrik/rgrpoc1-ch0','/mnt/rubrik/rgrpoc1-ch1']
connect_string = 'system/rubrik123@ora-devops-lnx02.rangers.lab/rgrpoc1.rangers.lab'

file_pieces = []
for path in paths:
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for file in onlyfiles:
        file_pieces.append(join(path,file))

print('These are the files on disk:')
for file in file_pieces:
    print(file)

con = cx_Oracle.connect(connect_string)
dbs_cursor = con.cursor()

dbs_cursor.execute('select * from global_name')
print('Connected to database {0} version {1}'.format(dbs_cursor.fetchall()[0][0],con.version))

rman_pieces = []
backup_piece_cursor = con.cursor()
for path in paths:
    backup_piece_cursor.execute("select fname from v$backup_files where fname like '" + path + "/%'")
    results = backup_piece_cursor.fetchall()
    for r in results:
        rman_pieces.append(r[0])

con.close()

print('These are the files in the catalog:')
for p in rman_pieces:
    print(p)

print('Files no longer in the RMAN catalog. These will be removed')
orphans = set(file_pieces) - set(rman_pieces)

if orphans:
    for orphan in orphans:
        print(orphan)
    for orphan in orphans:
        remove(orphan)
else:
    print('No orphaned files found.')



