import subprocess
import datetime
import os
import json
from settings import *

def execute(l):
    result = subprocess.run(l, stdout = subprocess.PIPE)
    result.stdout = result.stdout.decode('utf8').split('\n')
    return result

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

def copy_folder_to_container(container_name, source_path, destination_path):
    l = ['docker', 'cp', source_path, container_name + ':' + destination_path ]
    print('Copying %s to container %s in %s' %(source_path, container_name, destination_path) )
    execute(l)

def change_folder_ownership(container_name, path, user, group):
    own_str = user + ':' + group
    print('Changing ownership of ', path, 'inside', container_name, 'to ', own_str )
    l = ['docker', 'exec', container_name, 'chown', '-R', own_str, path]
    execute(l)

def create_backup_folder( str_format = '"%Y-%m-%d-%H-%M-%S"' ):
    now = datetime.datetime.now()
    rel_name = now.strftime("%Y-%m-%d-%H-%M-%S")
    abs_name = os.path.join( ROOT_BACKUP_FOLDER, rel_name )
    execute(['mkdir', '-p', abs_name])
    return abs_name

def get_current_path():
    result = execute('pwd')
    return result.stdout[0]

def zip_folder(folder, zip_file):
    pwd = get_current_path()
    execute('cd', folder)
    print('Creating zip file:', zip_file, 'for folder ', folder)
    execute(['zip', '-r', zip_file, '.'] )
    execute('cd', pwd)
    
def remove_folder(folder):
    execute(['rm', '-r', folder] )
