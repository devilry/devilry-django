def add_custom_templates_directory(templates_setting, directory_path):
    dirs = templates_setting[0].get('DIRS', [])
    if 'directory_path' in dirs:
        return
    dirs.append(directory_path)
