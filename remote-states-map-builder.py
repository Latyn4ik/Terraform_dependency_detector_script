import json, re, os, sys


def get_path_to_terragrunt_file(root, substring):
    objs = []
    file = 'terragrunt.hcl'
    for rootdir, dirnames, files in os.walk(root):
        if '.terra' not in rootdir and 'temp' not in rootdir:
            if file in files:
                filepath = os.path.join(rootdir, file)
                with open(filepath, 'r') as f:
                    file_content = f.read()
                    if substring in file_content:
                        objs.append(rootdir)
    return objs


def read_file(filepath):
    with open(filepath, 'r') as f:
        file_content = f.read().split("\n")
    return file_content


def get_filepath_by_filename(_path, filename):
    filepath_obj = {}
    for path, directories, files in os.walk(_path):
        if '.terra' not in path and 'temp' not in path:
            if filename in files:
                filepath = os.path.join(path, filename)
                filepath_obj = {'service_folder': _path,
                                'remote_state_config_file': filepath}
                break
    return filepath_obj


def filter_filepaths(file_content, include_value, exclude_value):
    value = ""
    for line in file_content:
        if include_value in line and not exclude_value in line:
            value = re.findall(r'"(.*?)"', line)[0]
    return value


def get_filepaths(services_obj, filename):
    srvs_obj = []
    for service_folder, value in services_obj.items():
        srv_obj = get_filepath_by_filename(service_folder, filename)
        if srv_obj:
            srvs_obj.append(srv_obj)
    return srvs_obj


def read_files(remote_state_config_files, include_value, exclude_value):
    fps = []
    for remote_state_config_file in remote_state_config_files:
        file_content = read_file(
            remote_state_config_file['remote_state_config_file'])
        value = filter_filepaths(file_content, include_value, exclude_value)
        if value:
            fps.append(remote_state_config_file)
    return fps


def read_terragrunt_files(filepaths, include_value, exclude_value):
    fps = []
    for filepath in filepaths:
        file_content = read_file(filepath)
        value = filter_filepaths(file_content, include_value, exclude_value)
        if value:
            fps.append(filepath)
    return fps


def get_bucket_name(filepath, include, exclude):
    file_content = read_file(filepath)
    return filter_filepaths(file_content, include, exclude)


def get_buckets_names(filepaths, include, exclude):
    for filepath in filepaths:
        bucket_name = get_bucket_name(
            filepath['remote_state_config_file'], include, exclude)
        filepath['bucket'] = bucket_name
    return filepaths


def get_state_path(filepaths, include, exclude):
    for filepath in filepaths:
        path_in_bucket = get_bucket_name(
            filepath['remote_state_config_file'], include, exclude)
        filepath['path_in_bucket'] = path_in_bucket
    return filepaths


def get_filepaths_by_filename(root, filename):
    filepaths = set()
    for path, directories, files in os.walk(root):
        if '.terra' not in path and 'temp' not in path:
            if filename in files:
                filepaths.add(os.path.join(path, filename))
    return filepaths


def get_folder(filepaths):
    folder_filepath = []
    for filepath in filepaths:
        dir = os.path.dirname(filepath)
        folder_filepath.append(
            {'service_folder': dir, 'remote_state_config_file': filepath})
    return folder_filepath


def save_json(data, filename):
    with open(filename, "w") as outfile:
        outfile.write(data)


root_dir = sys.argv[1]
path = 'tools/dependency.json'
backend = "backend.tf"
substing = "../templates/"
terragrunt = "terragrunt.hcl"
services_obj = {}


services = get_path_to_terragrunt_file(root_dir, substing)

for service in services:
    services_obj[service] = {"path_in_bucket": "", "dependant_services": [], "bucket": "", "remote_state_config_file": ""}


remote_state_config_files = get_filepaths(services_obj, backend)
backend_services = read_files(remote_state_config_files, "bucket", "#")
backend_services = get_buckets_names(backend_services, 'bucket', '#')
backend_services = get_state_path(backend_services, 'key', '#')

filepaths = get_filepaths_by_filename(root_dir, terragrunt)

terragrunt_services = read_terragrunt_files(
    filepaths, '/${path_relative_to_include()}.tfstate"', "#")

terragrunt_services = get_folder(terragrunt_services)
terragrunt_services = get_buckets_names(terragrunt_services, 'bucket', '#')
terragrunt_services = get_state_path(terragrunt_services, 'key', '#')


for backend_service in backend_services:
    for service_folder,  value in services_obj.items():
        if backend_service['service_folder'] == service_folder:
            value['bucket'] = backend_service['bucket']
            value['path_in_bucket'] = backend_service['path_in_bucket']
            value['remote_state_config_file'] = backend_service['remote_state_config_file']


for service_folder,  value in services_obj.items():
    if value['path_in_bucket'] == '':
        for terragrunt_service in terragrunt_services:
            if terragrunt_service['service_folder'] in service_folder:
                service_relative_path = service_folder.split(
                    terragrunt_service['service_folder'] + '/')[-1]
                value['path_in_bucket'] = terragrunt_service['path_in_bucket'].replace(
                    '${path_relative_to_include()}', service_relative_path)
                value['bucket'] = terragrunt_service['bucket']
                value['remote_state_config_file'] = terragrunt_service['remote_state_config_file']


result = json.dumps(services_obj, indent=2)
save_json(result, path)