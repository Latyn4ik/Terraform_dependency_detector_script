## Instruction for scripts:  remote-states-map-builder.py and services_dependency_map_builder.py


For remote-states-map-builder.py to work correctly, you need to execute the script in the root of the repository with an argument in which you specify the path to the folder with services for which you want to build dependencies, for example:

```
python3 tools/remote-states-map-builder.py env/qa
```

**env/qa** it is folder with all qa environments.

As a result, the script will create a **dependency.json** file in the **/tools** folder.



**services_dependency_map_builder.py** add a list of dependent services for each service in specified env.

Example of run command:
```
python3 tools/services_dependency_map_builder.py tools/dependency.json env/qa/ld2
```


For example, if msk (ld2 env) service have dependency on eks2_common (ld2 env) service, script will add **env/qa/ld2/msk** to **dependant_services** list
```
    "env/qa/ld2/eks/eks_common": {
        "path_in_bucket": "ld2/eks/eks_common.tfstate",
        "dependant_services": [
            "env/qa/ld2/msk",
            "env/qa/ld2/elasticache-redis-smpp",
            "env/qa/ld2/documentdb-mceclient",
            "env/qa/ld2/documentdb-frequencymgr",
            "env/qa/ld2/elasticache-redis-email-insight",
            "env/qa/ld2/s3-social",
            "env/qa/ld2/documentdb-mcecentral",
            "env/qa/ld2/cw-insights",
            "env/qa/ld2/eks/cluster2",
            "env/qa/ld2/eks/helm/cw-prometheus-ld2-eks2",
            "env/qa/ld2/cw-insights-eks2",
            "env/qa/ld2/documentdb-smpp",
            "env/qa/ld2/elasticache-redis-mce",
            "env/qa/ld2/elasticache-clustered-redis-send-engine",
            "env/qa/ld2/cw-prometheus-ld2-eks2",
            "env/qa/ld2/elasticache-redis-social"
        ],
        "bucket": "company-dev-campaign-terraform",
        "remote_state_config_file": "env/qa/ld2/terragrunt.hcl"
    },
```