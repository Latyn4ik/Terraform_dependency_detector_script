import time, json, os, sys, boto3


def get_remote_states_keys(bucket, tfstate_key):
    remote_states_keys = []
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket, Key=tfstate_key)

        state = json.loads(response['Body'].read().decode())

        for resource in state['resources']:
            if resource['type'] == "terraform_remote_state":
                for instance in resource['instances']:
                    remote_states_keys.append((instance['attributes']['config']['value']['key']))
        return remote_states_keys
    except:
        print("S3 Key not found: " + str(tfstate_key))


def acquire_lock(lock_path):
    if not os.path.exists(lock_path):
        with open(lock_path, "w") as outfile:
             return True
    else:
        while os.path.exists(lock_path):
            time.sleep(1)
        with open(lock_path, "w") as outfile:
            return True


def release_lock(lock_path):
    if os.path.exists(lock_path):
        os.remove(lock_path)
        return True


def read_json(path):
    with open(path) as json_file:
        json_obj = json.load(json_file)
        return json_obj


def save_to_json(json_object, path_to_json):
        with open(path_to_json, "w") as outfile:
            json.dump(json_object, outfile)


def get_service_from_path(service_dict, absolute_path):
    for key in service_dict.keys():
        if absolute_path.endswith(key):
            return key

def add_dependency(remote_states_keys_list, dict_of_services):
    for remote_state_key in remote_states_keys_list:
        for key, value in dict_of_services.items():
            if remote_state_key == value["path_in_bucket"]:
                service_path = get_service_from_path(dict_of_services, os.getcwd())
                if service_path not in value["dependant_services"]: # check on duplicates
                    value["dependant_services"].append(service_path)
    return dict_of_services


def save_dependency_to_json(env_path, services_dict, dependency_file_abs_path):
    result = ""
    for service_path, value in services_dict.items():
        if env_path in service_path:
            start_path = os.getcwd()
            os.chdir(service_path)
            remote_states_keys = get_remote_states_keys(value["bucket"], value["path_in_bucket"])
            if remote_states_keys != None:
                result = add_dependency(remote_states_keys, services_dict)
                os.chdir(start_path) # go to repo root folder
                acquire_lock(start_path + '/' + lock_file)
                save_to_json(result, dependency_file_abs_path)
                release_lock(start_path + '/' + lock_file)
            else:
                os.chdir(start_path) # go to repo root folder



path_to_json_file = sys.argv[1]
path_to_env       = sys.argv[2]
lock_file         = "lock_file"
dependency_file_name = os.path.basename(path_to_json_file)
dependency_file_path = __file__[:__file__.rfind('/') + 1] + dependency_file_name


if os.path.isfile(path_to_json_file):
    service_map_dict = read_json(path_to_json_file)
    save_dependency_to_json(path_to_env, service_map_dict, dependency_file_path)       
else:
    print("\nERROR!!!")
    print("\n{0} not found!".format(dependency_file_name))
    print("Please read README.md in ./tools folder and run script remote-states-map-builder.py to create dependency.json")