"""
Copyright (c) 2024, 2024 Red Hat, IBM Corporation and others.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import copy
import json

import pytest
import sys
import time
import shutil
sys.path.append("../../")

from helpers.fixtures import *
from helpers.generate_rm_jsons import *
from helpers.kruize import *
from helpers.short_term_list_reco_json_schema import *
from helpers.list_reco_json_validate import *
from helpers.list_datasources_json_validate import *
from helpers.utils import *
from helpers.utils import benchmarks_install
from helpers.utils import clone_repo
from helpers.utils import apply_tfb_load
from helpers.utils import wait_for_container_to_complete
from helpers.utils import validate_local_monitoring_reco_json
from helpers.list_metadata_json_validate import *
from helpers.list_metadata_json_schema import *
from helpers.list_metadata_json_verbose_true_schema import *
from helpers.list_metadata_json_cluster_name_without_verbose_schema import *
from helpers.list_metric_profiles_validate import *
from helpers.list_metric_profiles_without_parameters_schema import *
from helpers.short_term_list_reco_json_schema import *
from helpers.list_reco_json_local_monitoring_schema import *
from helpers.list_reco_json_validate import *
from helpers.import_metadata_json_validate import *
from jinja2 import Environment, FileSystemLoader
from helpers.list_metadata_profiles_validate import *
from helpers.list_metadata_profiles_schema import *

metric_profile_dir = get_metric_profile_dir()
metadata_profile_dir = get_metadata_profile_dir()


@pytest.mark.test_e2e
@pytest.mark.test_e2e_pr_check
def test_list_recommendations_multiple_exps_for_datasource_workloads(cluster_type):
    """
    Test Description: This test validates list recommendations for multiple experiments posted using different json files
    """
    clone_repo("https://github.com/kruize/benchmarks")
    benchmarks_install(name="sysbench", manifests="sysbench.yaml")

    # list all datasources
    form_kruize_url(cluster_type)

    # Get the datasources name
    datasource_name = None
    response = list_datasources(datasource_name)

    list_datasources_json = response.json()

    assert response.status_code == SUCCESS_200_STATUS_CODE

    # Validate the json against the json schema
    errorMsg = validate_list_datasources_json(list_datasources_json, list_datasources_json_schema)
    assert errorMsg == ""

    # Install metadata profile
    metadata_profile_json_file = metadata_profile_dir / 'bulk_cluster_metadata_local_monitoring.json'
    json_data = json.load(open(metadata_profile_json_file))
    metadata_profile_name = json_data['metadata']['name']

    response = delete_metadata_profile(metadata_profile_name)
    print("delete metadata profile = ", response.status_code)

    # Create metadata profile using the specified json
    response = create_metadata_profile(metadata_profile_json_file)

    data = response.json()
    print(data['message'])

    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    assert data['message'] == CREATE_METADATA_PROFILE_SUCCESS_MSG % metadata_profile_name

    response = list_metadata_profiles(name=metadata_profile_name, logging=False)
    metadata_profile_json = response.json()

    assert response.status_code == SUCCESS_200_STATUS_CODE

    # Validate the json against the json schema
    errorMsg = validate_list_metadata_profiles_json(metadata_profile_json, list_metadata_profiles_schema)
    assert errorMsg == ""


    # Import datasource metadata
    input_json_file = "../json_files/import_metadata.json"

    response = delete_metadata(input_json_file)
    print("delete metadata = ", response.status_code)

    # Import metadata using the specified json
    response = import_metadata(input_json_file)
    metadata_json = response.json()

    # Validate the json against the json schema
    errorMsg = validate_import_metadata_json(metadata_json, import_metadata_json_schema)
    assert errorMsg == ""


    # Display metadata from prometheus-1 datasource
    json_data = json.load(open(input_json_file))
    datasource = json_data['datasource_name']

    response = list_metadata(datasource)

    list_metadata_json = response.json()
    assert response.status_code == SUCCESS_200_STATUS_CODE

    # Validate the json against the json schema
    errorMsg = validate_list_metadata_json(list_metadata_json, list_metadata_json_schema)
    assert errorMsg == ""


    # Display metadata for default namespace
    # Currently only default cluster is supported by Kruize
    cluster_name = "default"

    response = list_metadata(datasource=datasource, cluster_name=cluster_name, verbose="true")

    list_metadata_json = response.json()
    assert response.status_code == SUCCESS_200_STATUS_CODE

    # Validate the json against the json schema
    errorMsg = validate_list_metadata_json(list_metadata_json, list_metadata_json_verbose_true_schema)
    assert errorMsg == ""

    # Generate a temporary JSON filename
    tmp_container_exp_json_file = "/tmp/create_exp_sysbench" + ".json"
    tmp_namespace_exp_json_file = "/tmp/create_exp_default_ns" + ".json"
    print("tmp_json_file for container exp = ", tmp_container_exp_json_file)
    print("tmp_json_file for namespace exp = ", tmp_namespace_exp_json_file)

    # Load the Jinja2 template
    environment = Environment(loader=FileSystemLoader("../json_files/"))
    template = environment.get_template("create_exp_template.json")

    # Render the JSON content from the template

    container_exp_content = template.render(
       version="v2.0", experiment_name="monitor-sysbench", cluster_name="default", performance_profile="resource-optimization-local-monitoring",
       metadata_profile="cluster-metadata-local-monitoring", mode="monitor", target_cluster="local", datasource="prometheus-1",
       experiment_type="container", kubernetes_obj_type="deployment", name="sysbench", namespace="default", namespace_name=None,
       container_image_name="quay.io/kruizehub/sysbench", container_name="sysbench", measurement_duration="2min", threshold="0.1"
    )

    namespace_exp_content = template.render(
        version="v2.0", experiment_name="monitor-ns", cluster_name="default", performance_profile="resource-optimization-local-monitoring",
        metadata_profile="cluster-metadata-local-monitoring", mode="monitor", target_cluster="local", datasource="prometheus-1",
        experiment_type="namespace", kubernetes_obj_type=None, name=None, namespace=None, namespace_name="default",
        container_image_name=None, container_name=None, measurement_duration="2min", threshold="0.1"
    )

    # Convert rendered content to a dictionary
    container_exp_json_content = json.loads(container_exp_content)
    container_exp_json_content[0]["kubernetes_objects"][0].pop("namespaces")

    # Convert rendered content to a dictionary
    namespace_exp_json_content = json.loads(namespace_exp_content)
    namespace_exp_json_content[0]["kubernetes_objects"][0].pop("type")
    namespace_exp_json_content[0]["kubernetes_objects"][0].pop("name")
    namespace_exp_json_content[0]["kubernetes_objects"][0].pop("namespace")
    namespace_exp_json_content[0]["kubernetes_objects"][0].pop("containers")

    # Write the final JSON to the temp file
    with open(tmp_container_exp_json_file, mode="w", encoding="utf-8") as message:
        json.dump(container_exp_json_content, message, indent=4)

    with open(tmp_namespace_exp_json_file, mode="w", encoding="utf-8") as message:
        json.dump(namespace_exp_json_content, message, indent=4)

    # exp json file
    container_exp_json_file = tmp_container_exp_json_file
    namespace_exp_json_file = tmp_namespace_exp_json_file

    response = delete_experiment(container_exp_json_file, rm=False)
    print("delete sysbench container exp = ", response.status_code)

    response = delete_experiment(namespace_exp_json_file, rm=False)
    print("delete namespace exp = ", response.status_code)

    # Install default metric profile
    if cluster_type == "minikube":
        metric_profile_json_file = metric_profile_dir / 'resource_optimization_local_monitoring_norecordingrules.json'

    if cluster_type == "openshift":
        metric_profile_json_file = metric_profile_dir / 'resource_optimization_local_monitoring.json'

    response = delete_metric_profile(metric_profile_json_file)
    print("delete metric profile = ", response.status_code)

    # Create metric profile using the specified json
    response = create_metric_profile(metric_profile_json_file)

    data = response.json()
    print(data['message'])

    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    json_file = open(metric_profile_json_file, "r")
    input_json = json.loads(json_file.read())
    metric_profile_name = input_json['metadata']['name']
    assert data['message'] == CREATE_METRIC_PROFILE_SUCCESS_MSG % metric_profile_name

    response = list_metric_profiles(name=metric_profile_name, logging=False)
    metric_profile_json = response.json()

    assert response.status_code == SUCCESS_200_STATUS_CODE

    # Validate the json against the json schema
    errorMsg = validate_list_metric_profiles_json(metric_profile_json, list_metric_profiles_schema)
    assert errorMsg == ""


    # Create container experiments using the specified json
    response = create_experiment(container_exp_json_file)

    data = response.json()
    print(data['message'])

    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # create namespace experiment
    response = create_experiment(namespace_exp_json_file)

    data = response.json()
    print(data['message'])

    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Wait for the threshold for short term recommendations
    time.sleep(300)

    # generate recommendations
    json_file = open(container_exp_json_file, "r")
    input_json = json.loads(json_file.read())
    container_exp_name = input_json[0]['experiment_name']

    json_file = open(namespace_exp_json_file, "r")
    input_json = json.loads(json_file.read())
    namespace_exp_name = input_json[0]['experiment_name']


    response = generate_recommendations(container_exp_name)
    assert response.status_code == SUCCESS_STATUS_CODE

    # Invoke list recommendations for the specified experiment
    response = list_recommendations(container_exp_name)
    assert response.status_code == SUCCESS_200_STATUS_CODE
    list_reco_json = response.json()

    # Validate the json against the json schema
    errorMsg = validate_list_reco_json(list_reco_json, list_reco_json_local_monitoring_schema)
    assert errorMsg == ""

    # Validate the json values
    validate_local_monitoring_recommendation_data_present(list_reco_json)
    sysbench_exp_json = read_json_data_from_file(container_exp_json_file)
    validate_local_monitoring_reco_json(sysbench_exp_json[0], list_reco_json[0])

    response = generate_recommendations(container_exp_name)
    assert response.status_code == SUCCESS_STATUS_CODE


    response = generate_recommendations(namespace_exp_name)
    assert response.status_code == SUCCESS_STATUS_CODE

    # Invoke list recommendations for the specified experiment
    response = list_recommendations(namespace_exp_name)
    assert response.status_code == SUCCESS_200_STATUS_CODE
    list_reco_json = response.json()

    # Validate the json against the json schema
    errorMsg = validate_list_reco_json(list_reco_json, list_reco_namespace_json_local_monitoring_schema)
    assert errorMsg == ""

    # Validate the json values
    validate_local_monitoring_recommendation_data_present(list_reco_json)
    namespace_exp_json = read_json_data_from_file(namespace_exp_json_file)
    validate_local_monitoring_reco_json(namespace_exp_json[0], list_reco_json[0])


    # Delete sysbench container experiment
    response = delete_experiment(container_exp_json_file, rm=False)
    print("delete exp = ", response.status_code)
    assert response.status_code == SUCCESS_STATUS_CODE

    # Delete namespace experiment
    response = delete_experiment(namespace_exp_json_file, rm=False)
    print("delete exp = ", response.status_code)
    assert response.status_code == SUCCESS_STATUS_CODE

    # Delete Metric Profile
    response = delete_metric_profile(metric_profile_json_file)
    print("delete metric profile = ", response.status_code)
    assert response.status_code == SUCCESS_STATUS_CODE

    # Remove benchmarks directory
    shutil.rmtree("benchmarks")
