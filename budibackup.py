import subprocess
import datetime
import os
import json

def execute(l):
    result = subprocess.run(l, stdout = subprocess.PIPE)
    result.stdout = result.stdout.decode('utf8').split('\n')
    return result

COUCH_CONTAINER_NAME = 'couchdb'
REDIS_CONTAINER_NAME = 'redis'
MINIO_CONTAINER_NAME = 'minio'

REMOTE_NAME = 'budibaseBackup'

COUCH_DATA_FOLDER = '/opt/couchdb/data/.'
REDIS_DATA_FOLDER = '/data'
MINIO_DATA_FOLDER = '/data'

ROOT_BACKUP_FOLDER = '/budidisk/docker/couchbackup/'

def get_containers():
    result = subprocess.run(['docker' , 'ps' , '--format', '\'{"ID":"{{ .ID }}", "Image": "{{ .Image }}", "Names":"{{ .Names }}"}\'' ],
                             stdout = subprocess.PIPE)
    stdout = result.stdout.decode('utf8')
    entries = stdout.replace('\'','').split('\n')
    containers = []
    for entry in entries:
        if entry != '':
            containers.append( json.loads(entry) )

    return containers

def get_budi_containers():
    containers = get_containers()
    c = {}
    for container in containers:
        name = container['Names']
        if COUCH_CONTAINER_NAME in name:
            c['couch'] = {'name' : name,
                          'abs_data' : name + ':' + COUCH_DATA_FOLDER,
                          'rel_data' : COUCH_DATA_FOLDER }

        elif REDIS_CONTAINER_NAME in name:
            c['redis'] = {'name' : name,
                          'abs_data' : name + ':' + REDIS_DATA_FOLDER,
                          'rel_data' : REDIS_DATA_FOLDER }

        elif MINIO_CONTAINER_NAME in name:
            c['minio'] = {'name' : name,
                          'abs_data' : name + ':' + MINIO_DATA_FOLDER,
                          'rel_data' : REDIS_DATA_FOLDER }

    return c

def copy_container_folder(container_name, source_path, destination_path):
    print('Copying %s from %s to %s' %(source_path, container_name, destination_path) )
    l = ['docker', 'cp', container_name + ':' + source_path, destination_path ]
    execute(l)

def create_backup_folder( str_format = '"%Y-%m-%d-%H-%M-%S"' ):
    now = datetime.datetime.now()
    rel_name = now.strftime("%Y-%m-%d-%H-%M-%S")
    abs_name = os.path.join( ROOT_BACKUP_FOLDER, rel_name )
    execute(['mkdir', '-p', abs_name])
    return abs_name

def zip_folder(folder, zip_file):
    print('Creating zip file:', zip_file, 'for folder ', folder)
    execute(['zip', '-r', zip_file, folder + '/'] )

def remove_folder(folder):
    execute(['rm', '-r', folder] )


containers = get_budi_containers()
folder = create_backup_folder()

for key, c in containers.items():
    backup_folder = os.path.join( folder, c['name'] )
    print('Copying ', c['rel_data'], 'to ', backup_folder)
    copy_container_folder( c['name'], c['rel_data'], backup_folder)

zip_name = folder + '.zip'
zip_folder(folder, zip_name)
print('Transferring to Google Drive')
execute(['rclone', 'copy', zip_name, REMOTE_NAME + ':/'])
print('Deleting foder', folder)
remove_folder(folder)
