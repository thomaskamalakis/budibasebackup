import budibackuplib as bb

containers = bb.get_budi_containers()
folder = bb.create_backup_folder()

for key, c in containers.items():
    backup_folder = os.path.join( folder, c['name'] )
    print('Copying ', c['rel_data'], 'to ', backup_folder)
    bb.copy_container_folder( c['name'], c['rel_data'], backup_folder)

zip_name = folder + '.zip'
bb.zip_folder(folder, zip_name)
print('Transferring to Google Drive')
bb.execute(['rclone', 'copy', zip_name, REMOTE_NAME + ':/'])
print('Deleting foder', folder)
bb.remove_folder(folder)
