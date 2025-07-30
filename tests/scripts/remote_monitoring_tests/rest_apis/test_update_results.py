"""
Copyright (c) 2022, 2024 Red Hat, IBM Corporation and others.

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
import pytest
import sys
sys.path.append("../../")
from helpers.fixtures import *
from helpers.kruize import *
from helpers.utils import *
from jinja2 import Environment, FileSystemLoader

csvfile = "/tmp/update_results_test_data.csv"
csvfilen = "/tmp/update_results_namespace_test_data.csv"


# Interval end time that is acceptable is measurement_duration + or - 30s
# interval_start_time - "2022-01-23T18:25:43.511Z"
interval_end_times = [
    ("invalid_zero_diff", "2022-01-23T18:25:43.511Z"),
    ("invalid_minus_more_than_30s", "2022-01-23T18:40:12.511Z"),
    ("valid_minus_30s", "2022-01-23T18:40:13.511Z"),
    ("invalid_plus_more_than_30s", "2022-01-23T18:41:14.511Z"),
    ("valid_plus_30s", "2022-01-23T18:41:13.511Z")
]

missing_metrics = [
    ("Missing_metrics_single_res_single_container", "../json_files/missing_metrics_jsons/update_results_missing_metrics_single_container.json", "Out of a total of 1 records, 1 failed to save", "Performance profile: [Metric data is not present for container : tfb-server-0 for experiment: quarkus-resteasy-kruize-min-http-response-time-db"),
    ("Missing_metrics_single_res_all_containers", "../json_files/missing_metrics_jsons/update_results_missing_metrics_all_containers.json", "Out of a total of 1 records, 1 failed to save", "Performance profile: [Metric data is not present for container : tfb-server-0 for experiment: quarkus-resteasy-kruize-min-http-response-time-db. , Metric data is not present for container : tfb-server-1 for experiment: quarkus-resteasy-kruize-min-http-response-time-db"),
    ("Missing_metrics_bulk_res_single_container", "../json_files/missing_metrics_jsons/bulk_update_results_missing_metrics_single_container.json", "Out of a total of 100 records, 1 failed to save", "Performance profile: [Metric data is not present for container : tfb-server-1 for experiment: quarkus-resteasy-kruize-min-http-response-time-db"),
    ("Missing_metrics_bulk_res_few_containers", "../json_files/missing_metrics_jsons/bulk_update_results_missing_metrics_few_containers.json", "Out of a total of 100 records, 2 failed to save", "Performance profile: [Metric data is not present for container : tfb-server-1 for experiment: quarkus-resteasy-kruize-min-http-response-time-db"),
    ("Missing_metrics_bulk_res_few_containers_few_individual_metrics_missing", "../json_files/missing_metrics_jsons/bulk_update_results_missing_metrics_few_containers_few_individual_metrics_missing.json", "Out of a total of 100 records, 4 failed to save", "Metric data is not present for container")
]

missing_metrics_namespace = [
    ("Missing_metrics_single_res_single_namespace", "../json_files/missing_metrics_jsons/update_results_missing_metrics_single_namespace.json", "Out of a total of 1 records, 1 failed to save", "Performance profile: [Missing one of the following mandatory parameters for experiment - namespace-demo"),
]

@pytest.mark.negative
@pytest.mark.parametrize(
    "test_name, expected_status_code, version, experiment_name, interval_start_time, interval_end_time, kubernetes_obj_type, name, namespace, container_image_name, container_name, cpuRequest_name, cpuRequest_sum, cpuRequest_avg, cpuRequest_format, cpuLimit_name, cpuLimit_sum, cpuLimit_avg, cpuLimit_format, cpuUsage_name, cpuUsage_sum, cpuUsage_max, cpuUsage_avg, cpuUsage_min, cpuUsage_format, cpuThrottle_name, cpuThrottle_sum, cpuThrottle_max, cpuThrottle_avg, cpuThrottle_format, memoryRequest_name, memoryRequest_sum, memoryRequest_avg, memoryRequest_format, memoryLimit_name, memoryLimit_sum, memoryLimit_avg, memoryLimit_format, memoryUsage_name, memoryUsage_sum, memoryUsage_max, memoryUsage_avg, memoryUsage_min, memoryUsage_format, memoryRSS_name, memoryRSS_sum, memoryRSS_max, memoryRSS_avg, memoryRSS_min, memoryRSS_format",
    generate_test_data(csvfile, update_results_test_data, "update_results"))
def test_update_results_invalid_tests(test_name, expected_status_code, version, experiment_name, interval_start_time,
                                      interval_end_time, kubernetes_obj_type, name, namespace, container_image_name,
                                      container_name, cpuRequest_name, cpuRequest_sum, cpuRequest_avg,
                                      cpuRequest_format, cpuLimit_name, cpuLimit_sum, cpuLimit_avg, cpuLimit_format,
                                      cpuUsage_name, cpuUsage_sum, cpuUsage_max, cpuUsage_avg, cpuUsage_min,
                                      cpuUsage_format, cpuThrottle_name, cpuThrottle_sum, cpuThrottle_max,
                                      cpuThrottle_avg, cpuThrottle_format, memoryRequest_name, memoryRequest_sum,
                                      memoryRequest_avg, memoryRequest_format, memoryLimit_name, memoryLimit_sum,
                                      memoryLimit_avg, memoryLimit_format, memoryUsage_name, memoryUsage_sum,
                                      memoryUsage_max, memoryUsage_avg, memoryUsage_min, memoryUsage_format,
                                      memoryRSS_name, memoryRSS_sum, memoryRSS_max, memoryRSS_avg, memoryRSS_min,
                                      memoryRSS_format, cluster_type):
    print("\n*******************************************************")
    print("Test - ", test_name)
    print("*******************************************************\n")
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    print(data['message'])
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Create experiment using the specified json
    result_json_file = "../json_files/update_results_template.json"
    tmp_json_file = "/tmp/update_results_" + test_name + ".json"

    environment = Environment(loader=FileSystemLoader("../json_files/"))
    template = environment.get_template("update_results_template.json")

    if "null" in test_name:
        field = test_name.replace("null_", "")
        json_file = "../json_files/update_results_template.json"
        filename = "/tmp/update_results_template.json"

        strip_double_quotes_for_field(json_file, field, filename)
        environment = Environment(loader=FileSystemLoader("/tmp/"))
        template = environment.get_template("update_results_template.json")

    filename = f"/tmp/update_results_{test_name}.json"
    content = template.render(
        version=version,
        experiment_name=experiment_name,
        interval_start_time=interval_start_time,
        interval_end_time=interval_end_time,
        kubernetes_obj_type=kubernetes_obj_type,
        name=name,
        namespace=namespace,
        container_image_name=container_image_name,
        container_name=container_name,
        cpuRequest_name=cpuRequest_name,
        cpuRequest_sum=cpuRequest_sum,
        cpuRequest_avg=cpuRequest_avg,
        cpuRequest_format=cpuRequest_format,
        cpuLimit_name=cpuLimit_name,
        cpuLimit_sum=cpuLimit_sum,
        cpuLimit_avg=cpuLimit_avg,
        cpuLimit_format=cpuLimit_format,
        cpuUsage_name=cpuUsage_name,
        cpuUsage_sum=cpuUsage_sum,
        cpuUsage_max=cpuUsage_max,
        cpuUsage_avg=cpuUsage_avg,
        cpuUsage_min=cpuUsage_min,
        cpuUsage_format=cpuUsage_format,
        cpuThrottle_name=cpuThrottle_name,
        cpuThrottle_sum=cpuThrottle_sum,
        cpuThrottle_max=cpuThrottle_max,
        cpuThrottle_avg=cpuThrottle_avg,
        cpuThrottle_format=cpuThrottle_format,
        memoryRequest_name=memoryRequest_name,
        memoryRequest_sum=memoryRequest_sum,
        memoryRequest_avg=memoryRequest_avg,
        memoryRequest_format=memoryRequest_format,
        memoryLimit_name=memoryLimit_name,
        memoryLimit_sum=memoryLimit_sum,
        memoryLimit_avg=memoryLimit_avg,
        memoryLimit_format=memoryLimit_format,
        memoryUsage_name=memoryUsage_name,
        memoryUsage_sum=memoryUsage_sum,
        memoryUsage_max=memoryUsage_max,
        memoryUsage_avg=memoryUsage_avg,
        memoryUsage_min=memoryUsage_min,
        memoryUsage_format=memoryUsage_format,
        memoryRSS_name=memoryRSS_name,
        memoryRSS_sum=memoryRSS_sum,
        memoryRSS_max=memoryRSS_max,
        memoryRSS_avg=memoryRSS_avg,
        memoryRSS_min=memoryRSS_min,
        memoryRSS_format=memoryRSS_format
    )
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)

    response = update_results(tmp_json_file)

    data = response.json()
    print(data['message'])
    assert response.status_code == int(expected_status_code)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.negative
@pytest.mark.parametrize(
    "test_name, expected_status_code, version, experiment_name, interval_start_time, interval_end_time, namespace, namespaceCpuRequest_name, namespaceCpuRequest_sum, namespaceCpuRequest_format, namespaceCpuLimit_name, namespaceCpuLimit_sum, namespaceCpuLimit_format, namespaceCpuUsage_name, namespaceCpuUsage_min, namespaceCpuUsage_max, namespaceCpuUsage_avg, namespaceCpuUsage_format, namespaceCpuThrottle_name, namespaceCpuThrottle_min, namespaceCpuThrottle_max, namespaceCpuThrottle_avg, namespaceCpuThrottle_format, namespaceMemoryRequest_name, namespaceMemoryRequest_sum, namespaceMemoryRequest_format, namespaceMemoryLimit_name, namespaceMemoryLimit_sum, namespaceMemoryLimit_format, namespaceMemoryUsage_name, namespaceMemoryUsage_min, namespaceMemoryUsage_max, namespaceMemoryUsage_avg, namespaceMemoryUsage_format, namespaceMemoryRSS_name, namespaceMemoryRSS_min, namespaceMemoryRSS_max, namespaceMemoryRSS_avg, namespaceMemoryRSS_format, namespaceTotalPods_name, namespaceTotalPods_sum, namespaceRunningPods_name, namespaceRunningPods_sum",
    generate_test_data(csvfilen, update_results_namespace_test_data, "update_results"))
def test_update_results_invalid_namespace_tests(
    test_name, expected_status_code, version, experiment_name, interval_start_time, interval_end_time, namespace,
    namespaceCpuRequest_name, namespaceCpuRequest_sum, namespaceCpuRequest_format,
    namespaceCpuLimit_name, namespaceCpuLimit_sum, namespaceCpuLimit_format,
    namespaceCpuUsage_name, namespaceCpuUsage_min, namespaceCpuUsage_max, namespaceCpuUsage_avg, namespaceCpuUsage_format,
    namespaceCpuThrottle_name, namespaceCpuThrottle_min, namespaceCpuThrottle_max, namespaceCpuThrottle_avg, namespaceCpuThrottle_format,
    namespaceMemoryRequest_name, namespaceMemoryRequest_sum, namespaceMemoryRequest_format,
    namespaceMemoryLimit_name, namespaceMemoryLimit_sum, namespaceMemoryLimit_format,
    namespaceMemoryUsage_name, namespaceMemoryUsage_min, namespaceMemoryUsage_max, namespaceMemoryUsage_avg, namespaceMemoryUsage_format,
    namespaceMemoryRSS_name, namespaceMemoryRSS_min, namespaceMemoryRSS_max, namespaceMemoryRSS_avg, namespaceMemoryRSS_format,
    namespaceTotalPods_name, namespaceTotalPods_sum, namespaceRunningPods_name, namespaceRunningPods_sum, cluster_type):
    """
    This test function runs negative test scenarios for updating results for a namespace experiment.
    It creates a namespace experiment, then attempts to update it with invalid data.
    """
    print(f"\n*******************************************************")
    print(f"Test - {test_name}")
    print("*******************************************************\n")
    
    create_exp_json_file = "../json_files/create_exp_namespace.json"
    form_kruize_url(cluster_type)

    delete_experiment(create_exp_json_file)

    response = create_experiment(create_exp_json_file)
    data = response.json()
    print(f"Create Experiment Response: {data.get('message')}")
    assert response.status_code == SUCCESS_STATUS_CODE, "Experiment creation failed"
    assert data.get('status') == SUCCESS_STATUS, "Experiment status is not success"

    environment = Environment(loader=FileSystemLoader("../json_files/"))
    template = environment.get_template("update_results_template_namespace.json")
    
    content = template.render(
        version=version,
        experiment_name=experiment_name,
        interval_start_time=interval_start_time,
        interval_end_time=interval_end_time,
        namespace=namespace,
        namespaceCpuRequest_name=namespaceCpuRequest_name,
        namespaceCpuRequest_sum=namespaceCpuRequest_sum,
        namespaceCpuRequest_format=namespaceCpuRequest_format,
        namespaceCpuLimit_name=namespaceCpuLimit_name,
        namespaceCpuLimit_sum=namespaceCpuLimit_sum,
        namespaceCpuLimit_format=namespaceCpuLimit_format,
        namespaceCpuUsage_name=namespaceCpuUsage_name,
        namespaceCpuUsage_min=namespaceCpuUsage_min,
        namespaceCpuUsage_max=namespaceCpuUsage_max,
        namespaceCpuUsage_avg=namespaceCpuUsage_avg,
        namespaceCpuUsage_format=namespaceCpuUsage_format,
        namespaceCpuThrottle_name=namespaceCpuThrottle_name,
        namespaceCpuThrottle_min=namespaceCpuThrottle_min,
        namespaceCpuThrottle_max=namespaceCpuThrottle_max,
        namespaceCpuThrottle_avg=namespaceCpuThrottle_avg,
        namespaceCpuThrottle_format=namespaceCpuThrottle_format,
        namespaceMemoryRequest_name=namespaceMemoryRequest_name,
        namespaceMemoryRequest_sum=namespaceMemoryRequest_sum,
        namespaceMemoryRequest_format=namespaceMemoryRequest_format,
        namespaceMemoryLimit_name=namespaceMemoryLimit_name,
        namespaceMemoryLimit_sum=namespaceMemoryLimit_sum,
        namespaceMemoryLimit_format=namespaceMemoryLimit_format,
        namespaceMemoryUsage_name=namespaceMemoryUsage_name,
        namespaceMemoryUsage_min=namespaceMemoryUsage_min,
        namespaceMemoryUsage_max=namespaceMemoryUsage_max,
        namespaceMemoryUsage_avg=namespaceMemoryUsage_avg,
        namespaceMemoryUsage_format=namespaceMemoryUsage_format,
        namespaceMemoryRSS_name=namespaceMemoryRSS_name,
        namespaceMemoryRSS_min=namespaceMemoryRSS_min,
        namespaceMemoryRSS_max=namespaceMemoryRSS_max,
        namespaceMemoryRSS_avg=namespaceMemoryRSS_avg,
        namespaceMemoryRSS_format=namespaceMemoryRSS_format,
        namespaceTotalPods_name=namespaceTotalPods_name,
        namespaceTotalPods_sum=namespaceTotalPods_sum,
        namespaceRunningPods_name=namespaceRunningPods_name,
        namespaceRunningPods_sum=namespaceRunningPods_sum
    )
    tmp_json_file = f"/tmp/update_results_namespace_{test_name}.json"
    with open(tmp_json_file, mode="w", encoding="utf-8") as message:
        message.write(content)

    response = update_results(tmp_json_file)
    data = response.json()
    # print(data['message'])

    assert response.status_code == int(expected_status_code)
    actual_message = data.get('message')    
    response = delete_experiment(create_exp_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.negative
@pytest.mark.parametrize("test_name, result_json_file, expected_message, error_message", missing_metrics)
def test_update_results_with_missing_metrics_section(test_name, result_json_file, expected_message, error_message, cluster_type):
    """
    Test Description: This test validates update results for a valid experiment
                      by updating results with entire metrics section missing
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    print("**************************")
    print(data['message'])
    print("**************************")

    assert data['message'] == expected_message 

    msg_data=data['data']
    for d in msg_data:
        error_data=d["errors"]
        for err in error_data:
            actual_error_message = err["message"]
            if test_name == "Missing_metrics_bulk_res_few_containers" and d["interval_end_time"] == "2023-04-13T23:29:20.982Z":
                error_message = "Performance profile: [Metric data is not present for container : tfb-server-1 for experiment: quarkus-resteasy-kruize-min-http-response-time-db. , Metric data is not present for container : tfb-server-0 for experiment: quarkus-resteasy-kruize-min-http-response-time-db. ]"
            if test_name == "Missing_metrics_bulk_res_few_containers_few_individual_metrics_missing" and d["interval_end_time"] == "2023-04-13T23:44:20.982Z" or d["interval_end_time"] == "2023-04-13T23:59:20.982Z":
                error_message = "Performance profile: [Missing one of the following mandatory parameters for experiment - quarkus-resteasy-kruize-min-http-response-time-db : [cpuUsage, memoryUsage, memoryRSS]]"
            assert error_message in actual_error_message
    
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.negative
@pytest.mark.parametrize("test_name, result_json_file, expected_message, error_message", missing_metrics_namespace)
def test_update_results_with_missing_metrics_section_namespace(test_name, result_json_file, expected_message, error_message, cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment
                      by updating results with entire metrics section missing or individual metrics missing.
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    print("**************************")
    print(data['message'])
    print("**************************")

    assert data['message'] == expected_message

    msg_data=data['data']
    for d in msg_data:
        error_data=d["errors"]
        for err in error_data:
            actual_error_message = err["message"]
            assert error_message in actual_error_message
    
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)
    

@pytest.mark.negative
def test_upload_namespace_results_for_container_experiment(cluster_type):
    """
    Test Description: This test validates that posting namespace results to a container-based
                      experiment fails with the expected error.
    """
    input_json_file = "../json_files/create_exp.json"
    result_json_file = "../json_files/update_results_namespace.json"

    create_exp = read_json_data_from_file(input_json_file)
    update_res = read_json_data_from_file(result_json_file)

    experiment_name = 'container_experiment'

    # Set the same experiment name
    create_exp[0]['experiment_name'] = experiment_name
    update_res[0]['experiment_name'] = experiment_name

    # Optional: Write back to file if functions expect file input
    write_json_data_to_file("/tmp/temp_create_exp.json", create_exp)
    write_json_data_to_file("/tmp/temp_update_results.json", update_res)

    form_kruize_url(cluster_type)
    
    response = delete_experiment("/tmp/temp_create_exp.json")
    print("delete exp = ", response.status_code)

    response = create_experiment("/tmp/temp_create_exp.json")

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    
    response = update_results("/tmp/temp_update_results.json")
    data = response.json()
    print(f"Update Results Response: {data}")

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    actual_error = data['data'][0]['errors'][0]['message']
    assert "Kubernetes Object Types MisMatched" in actual_error

    response = delete_experiment("/tmp/temp_create_exp.json")
    print("delete exp = ", response.status_code)

# @pytest.mark.negative
def test_upload_container_results_for_namespace_experiment(cluster_type):
    """
    Test Description: This test validates that posting container results to a namespace-based
                      experiment fails with the expected error.
    """
    input_json_file = "../json_files/create_exp_namespace.json"
    result_json_file = "../json_files/update_results.json"

    create_exp = read_json_data_from_file(input_json_file)
    update_res = read_json_data_from_file(result_json_file)

    experiment_name = 'namespace_experiment'

    # Set the same experiment name
    create_exp[0]['experiment_name'] = experiment_name
    update_res[0]['experiment_name'] = experiment_name

    # Write back to file if functions expect file input
    write_json_data_to_file("/tmp/temp_create_exp.json", create_exp)
    write_json_data_to_file("/tmp/temp_update_results.json", update_res)

    form_kruize_url(cluster_type)
    
    response = delete_experiment("/tmp/temp_create_exp.json")
    print("delete exp = ", response.status_code)

    response = create_experiment("/tmp/temp_create_exp.json")
    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    
    response = update_results("/tmp/temp_update_results.json")
    data = response.json()
    print(f"Update Results Response: {data}")

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    ## add assertion for error message

    response = delete_experiment("/tmp/temp_create_exp.json")
    print("delete exp = ", response.status_code)

@pytest.mark.negative
def test_upload_bulk_namespace_results_for_container_experiment(cluster_type):
    """
    Test Description: This test validates that posting a mix of namespace and container results
                      to a container-based experiment fails for the namespace results.
    """
    input_json_file = "../json_files/create_exp.json"
    result_json_file = "../json_files/mixed_bulk_results_container.json" 

    form_kruize_url(cluster_type)
    
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    response = create_experiment(input_json_file)
    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    
    response = update_results(result_json_file)
    data = response.json()
    print(f"Update Results Response: {data}")

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert "failed to save" in data['message']
    
    error_found = False
    for result in data.get('data', []):
        if result.get('errors'):
            for error in result['errors']:
                if "Kubernetes Object Names MisMatched" in error.get('message', ''):
                    error_found = True
                    break
        if error_found:
            break
    
    assert error_found, KUBERNETES_MISMATCH
    
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

# @pytest.mark.negative
def test_upload_bulk_container_results_for_namespace_experiment(cluster_type):
    """
    Test Description: This test validates that posting a mix of container and namespace results
                      to a namespace-based experiment fails for the container results.
    """
    input_json_file = "../json_files/create_exp_namespace.json"
    result_json_file = "../json_files/mixed_bulk_results_namespace.json"

    form_kruize_url(cluster_type)
    
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    response = create_experiment(input_json_file)
    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    
    response = update_results(result_json_file)
    data = response.json()
    print(f"Update Results Response: {data}")

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert "failed to save" in data['message']
    
    error_found = False
    for result in data.get('data', []):
        if result.get('errors'):
            for error in result['errors']:
                if "Missing one of the following mandatory parameters for experiment" in error.get('message', ''):
                    error_found = True
                    break
        if error_found:
            break
            
    assert error_found, MISSING_MANDATORY_PARAMETERS

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.negative
def test_update_results_with_zero_metric_values_fails(cluster_type):
    """
    Test Description: This test validates that updating results fails when all metric values are zero.
    """
    input_json_file = "../json_files/create_exp_namespace.json"
    tmp_json_file = "/tmp/update_results_zero_metrics_namespace.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    response = create_experiment(input_json_file)
    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    environment = Environment(loader=FileSystemLoader("../json_files/"))
    template = environment.get_template("update_results_template_namespace.json")

    template_vars = {
        "version": "v2.0",
        "experiment_name": "namespace-demo",
        "interval_start_time": "2022-01-23T18:25:43.511Z",
        "interval_end_time": "2022-01-23T18:40:43.570Z",
        "namespace": "default",
        "namespaceCpuRequest_name": "namespaceCpuRequest", "namespaceCpuRequest_sum": 0.0, "namespaceCpuRequest_format": "cores",
        "namespaceCpuLimit_name": "namespaceCpuLimit", "namespaceCpuLimit_sum": 0.0, "namespaceCpuLimit_format": "cores",
        "namespaceCpuUsage_name": "namespaceCpuUsage", "namespaceCpuUsage_min": 0.0, "namespaceCpuUsage_max": 0.0, "namespaceCpuUsage_avg": 0.0, "namespaceCpuUsage_format": "cores",
        "namespaceCpuThrottle_name": "namespaceCpuThrottle", "namespaceCpuThrottle_min": 0.0, "namespaceCpuThrottle_max": 0.0, "namespaceCpuThrottle_avg": 0.0, "namespaceCpuThrottle_format": "cores",
        "namespaceMemoryRequest_name": "namespaceMemoryRequest", "namespaceMemoryRequest_sum": 0.0, "namespaceMemoryRequest_format": "MiB",
        "namespaceMemoryLimit_name": "namespaceMemoryLimit", "namespaceMemoryLimit_sum": 0.0, "namespaceMemoryLimit_format": "MiB",
        "namespaceMemoryUsage_name": "namespaceMemoryUsage", "namespaceMemoryUsage_min": 0.0, "namespaceMemoryUsage_max": 0.0, "namespaceMemoryUsage_avg": 0.0, "namespaceMemoryUsage_format": "MiB",
        "namespaceMemoryRSS_name": "namespaceMemoryRSS", "namespaceMemoryRSS_min": 0.0, "namespaceMemoryRSS_max": 0.0, "namespaceMemoryRSS_avg": 0.0, "namespaceMemoryRSS_format": "MiB",
        "namespaceTotalPods_name": "namespaceTotalPods", "namespaceTotalPods_sum": 0,
        "namespaceRunningPods_name": "namespaceRunningPods", "namespaceRunningPods_sum": 0
    }
    
    content = template.render(**template_vars)
    
    with open(tmp_json_file, mode="w", encoding="utf-8") as message:
        message.write(content)

    response = update_results(tmp_json_file)
    data = response.json()
    print(f"Update Results Response: {data.get('message')}")
    
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert "Cannot process results with all zero metric values" in data['data'][0]['errors'][0]['message']

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
def test_update_valid_results_after_create_exp(cluster_type):
    """
    Test Description: This test validates update results for a valid experiment
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/update_results.json"
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
def test_update_valid_results_after_create_namespace_exp(cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/update_results_namespace.json"
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
def test_update_multiple_valid_results_single_json_after_create_exp(cluster_type):
    """
    Test Description: This test validates update results for a valid experiment by posting multiple results
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/multiple_results_single_exp.json"
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
def test_update_multiple_valid_results_single_json_after_create_namespace_exp(cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment by posting multiple results
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/multiple_results_single_exp_namespace.json"
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
def test_update_multiple_valid_results_after_create_exp(cluster_type):
    """
    Test Description: This test validates update results for a valid experiment
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    # Update results for the experiment
    num_res = 5
    find_start_ts = "2022-01-23T18:25:43.511Z"
    find_end_ts = "2022-01-23T18:40:43.570Z"

    result_json_file = "../json_files/update_results.json"
    filename = "/tmp/result.json"
    for i in range(num_res):

        with open(result_json_file, 'r') as file:
            data = file.read()

        if i == 0:
            start_ts = get_datetime()
        else:
            start_ts = end_ts

        print("start_ts = ", start_ts)
        data = data.replace(find_start_ts, start_ts)

        end_ts = increment_timestamp_by_given_mins(start_ts, 15)
        print("end_ts = ", end_ts)
        data = data.replace(find_end_ts, end_ts)

        with open(filename, 'w') as file:
            file.write(data)

        response = update_results(filename, False)

        data = response.json()
        print("message = ", data['message'])

        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
def test_update_multiple_valid_results_after_create_namespace_exp(cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    # Update results for the experiment
    num_res = 5
    find_start_ts = "2022-01-23T18:25:43.511Z"
    find_end_ts = "2022-01-23T18:40:43.570Z"

    result_json_file = "../json_files/update_results_namespace.json"
    filename = "/tmp/result.json"
    for i in range(num_res):

        with open(result_json_file, 'r') as file:
            data = file.read()

        if i == 0:
            start_ts = get_datetime()
        else:
            start_ts = end_ts

        print("start_ts = ", start_ts)
        data = data.replace(find_start_ts, start_ts)

        end_ts = increment_timestamp_by_given_mins(start_ts, 15)
        print("end_ts = ", end_ts)
        data = data.replace(find_end_ts, end_ts)

        with open(filename, 'w') as file:
            file.write(data)

        response = update_results(filename, False)

        data = response.json()
        print("message = ", data['message'])

        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.sanity
@pytest.mark.parametrize("format_type", ["cores", "m"])
def test_update_multiple_valid_results_with_supported_cpu_format_types(format_type, cluster_type):
    """
    Test Description: This test validates update results for a valid experiment
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    # Update results for the experiment
    num_res = 96
    find_start_ts = "2022-01-23T18:25:43.511Z"
    find_end_ts = "2022-01-23T18:40:43.570Z"

    cpu_format = "cores"

    result_json_file = "../json_files/update_results.json"
    filename = "/tmp/result.json"
    for i in range(num_res):

        with open(result_json_file, 'r') as file:
            data = file.read()

        if i == 0:
            start_ts = get_datetime()
        else:
            start_ts = end_ts

        print("start_ts = ", start_ts)
        data = data.replace(find_start_ts, start_ts)

        end_ts = increment_timestamp_by_given_mins(start_ts, 15)
        print("end_ts = ", end_ts)
        data = data.replace(find_end_ts, end_ts)

        data = data.replace(cpu_format, format_type)

        with open(filename, 'w') as file:
            file.write(data)

        response = update_results(filename, False)

        data = response.json()
        print("message = ", data['message'])

        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS


@pytest.mark.sanity
@pytest.mark.parametrize("format_type", ["cores", "m"])
def test_update_multiple_valid_results_for_namespace_experiment_with_supported_cpu_format_types(format_type, cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    # Update results for the experiment
    num_res = 96
    find_start_ts = "2022-01-23T18:25:43.511Z"
    find_end_ts = "2022-01-23T18:40:43.570Z"

    cpu_format = "cores"

    result_json_file = "../json_files/update_results_namespace.json"
    filename = "/tmp/result.json"
    for i in range(num_res):

        with open(result_json_file, 'r') as file:
            data = file.read()

        if i == 0:
            start_ts = get_datetime()
        else:
            start_ts = end_ts

        print("start_ts = ", start_ts)
        data = data.replace(find_start_ts, start_ts)

        end_ts = increment_timestamp_by_given_mins(start_ts, 15)
        print("end_ts = ", end_ts)
        data = data.replace(find_end_ts, end_ts)

        data = data.replace(cpu_format, format_type)

        with open(filename, 'w') as file:
            file.write(data)

        response = update_results(filename, False)

        data = response.json()
        print("message = ", data['message'])

        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG
        assert data['status'] == SUCCESS_STATUS

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
@pytest.mark.parametrize("format_type", ["bytes", "Bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "kB", "KB", "MB", "GB", "TB", "PB", "EB", "K", "k", "M", "G", "T", "P", "E"])
def test_update_multiple_valid_results_with_supported_mem_format_types(format_type, cluster_type):
    """
    Test Description: This test validates update results for a valid experiment
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    # Update results for the experiment
    num_res = 96
    find_start_ts = "2022-01-23T18:25:43.511Z"
    find_end_ts = "2022-01-23T18:40:43.570Z"

    memory_format = "MiB"

    result_json_file = "../json_files/update_results.json"
    filename = "/tmp/result.json"
    for i in range(num_res):

        with open(result_json_file, 'r') as file:
            data = file.read()

        if i == 0:
            start_ts = get_datetime()
        else:
            start_ts = end_ts

        print("start_ts = ", start_ts)
        data = data.replace(find_start_ts, start_ts)

        end_ts = increment_timestamp_by_given_mins(start_ts, 15)
        print("end_ts = ", end_ts)
        data = data.replace(find_end_ts, end_ts)

        data = data.replace(memory_format, format_type)

        with open(filename, 'w') as file:
            file.write(data)

        response = update_results(filename, False)

        data = response.json()
        print("message = ", data['message'])

        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
@pytest.mark.parametrize("format_type", ["bytes", "Bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "kB", "KB", "MB", "GB", "TB", "PB", "EB", "K", "k", "M", "G", "T", "P", "E"])
def test_update_multiple_valid_results_for_namespace_experiment_with_supported_mem_format_types(format_type, cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS

    # Update results for the experiment
    num_res = 96
    find_start_ts = "2022-01-23T18:25:43.511Z"
    find_end_ts = "2022-01-23T18:40:43.570Z"

    memory_format = "MiB"

    result_json_file = "../json_files/update_results_namespace.json"
    filename = "/tmp/result.json"
    for i in range(num_res):

        with open(result_json_file, 'r') as file:
            data = file.read()

        if i == 0:
            start_ts = get_datetime()
        else:
            start_ts = end_ts

        print("start_ts = ", start_ts)
        data = data.replace(find_start_ts, start_ts)

        end_ts = increment_timestamp_by_given_mins(start_ts, 15)
        print("end_ts = ", end_ts)
        data = data.replace(find_end_ts, end_ts)

        data = data.replace(memory_format, format_type)

        with open(filename, 'w') as file:
            file.write(data)

        response = update_results(filename, False)

        data = response.json()
        print("message = ", data['message'])

        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
def test_update_results_multiple_exps_from_same_json_file(cluster_type):
    """
    Test Description: This test validates the response status code of updateResults API by posting
    results of multiple experiments in the same json file.
    """
    input_json_file = "../json_files/create_multiple_exps.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    print("message = ", data['message'])
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == CREATE_EXP_BULK_ERROR_MSG

    # Update results for the experiment
    result_json_file = "../json_files/multiple_exps_results.json"
    response = update_results(result_json_file)

    data = response.json()
    print("message = ", data['message'])

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == THREE_FAILED_RECORDS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
def test_update_results_multiple_exps_multiple_containers_from_same_json_file(cluster_type):
    """
    Test Description: This test validates the response status code of updateResults API by posting
    results of multiple experiments with multiple containers in the same json file.
    """
    input_json_file = "../json_files/create_multiple_exps_multiple_containers.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    print("message = ", data['message'])
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == CREATE_EXP_BULK_ERROR_MSG

    # Update results for the experiment
    result_json_file = "../json_files/multiple_exps_multiple_containers_results.json"
    response = update_results(result_json_file)

    data = response.json()
    print("message = ", data['message'])

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == THREE_FAILED_RECORDS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
def test_update_results_for_containers_not_present(cluster_type):
    """
    Test Description: This test validates the response status code of updateResults API by posting
    results of multiple experiments with multiple containers in the same json file.
    """
    input_json_file = "../json_files/create_multiple_exps.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    print("message = ", data['message'])
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == CREATE_EXP_BULK_ERROR_MSG

    # Update results for the experiment
    result_json_file = "../json_files/multiple_exps_multiple_containers_results.json"
    response = update_results(result_json_file)

    data = response.json()
    print("message = ", data['message'])
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == THREE_FAILED_RECORDS_MSG


@pytest.mark.sanity
def test_update_results_multiple_exps_from_diff_json_files(cluster_type):
    """
    Test Description: This test validates the updation of results for multiple experiments using different json files
    """

    input_json_file = "../json_files/create_exp.json"
    result_json_file = "../json_files/update_results.json"

    find = []
    json_data = json.load(open(input_json_file))

    find.append(json_data[0]['experiment_name'])
    find.append(json_data[0]["kubernetes_objects"][0]['name'])
    find.append(json_data[0]["kubernetes_objects"][0]['namespace'])

    form_kruize_url(cluster_type)

    # Create experiment using the specified json
    num_exps = 10
    for i in range(num_exps):
        json_file = "/tmp/create_exp.json"
        generate_json(find, input_json_file, json_file, i)

        response = delete_experiment(json_file)
        print("delete exp = ", response.status_code)

        response = create_experiment(json_file)

        data = response.json()
        print("message = ", data['message'])
        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == CREATE_EXP_SUCCESS_MSG

        # Update results for the experiment
        json_file = "/tmp/update_results.json"
        generate_json(find, result_json_file, json_file, i)
        response = update_results(json_file)

        data = response.json()
        print("message = ", data['message'])
        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

        response = delete_experiment(json_file)
        print("delete exp = ", response.status_code)


# @pytest.mark.negative
def test_update_valid_results_without_create_exp(cluster_type):
    """
    Test Description: This test validates the behavior of updateResults API by posting results for a non-existing experiment
    """
    input_json_file = "../json_files/create_exp.json"
    json_data = json.load(open(input_json_file))

    experiment_name = json_data[0]['experiment_name']
    print("experiment_name = ", experiment_name)

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    result_json_file = "../json_files/update_results.json"
    response = update_results(result_json_file)

    data = response.json()
    print("message = ", data['message'])

    EXP_NAME_NOT_FOUND_MSG = UPDATE_RECOMMENDATIONS_EXPERIMENT_NOT_FOUND + experiment_name
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == FAILED_RECORDS_MSG
    assert data['data'][0]['errors'][0]['message'] == EXP_NAME_NOT_FOUND_MSG


@pytest.mark.sanity
def test_update_results_with_same_result(cluster_type):
    """
    Test Description: This test validates update results for a valid experiment
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/update_results.json"
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    # Post the same result again
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS

    exp_json_data = read_json_data_from_file(input_json_file)
    experiment_name = exp_json_data[0]['experiment_name']

    result_json_data = read_json_data_from_file(result_json_file)
    interval_end_time = result_json_data[0]['interval_end_time']
    interval_start_time = result_json_data[0]['interval_start_time']

    print(DUPLICATE_RECORDS_MSG)
    print(data['data'][0]['errors'][0]['message'])
    assert data['message'] == FAILED_RECORDS_MSG
    assert data['data'][0]['errors'][0]['message'] == DUPLICATE_RECORDS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
def test_update_results_with_same_result_for_namespace_experiment(cluster_type):
    """
    Test Description: This test validates update results for a valid namespace experiment
                        by posting the same results twice.
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/update_results_namespace.json"
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG

    # Post the same result again
    response = update_results(result_json_file)

    data = response.json()
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS

    exp_json_data = read_json_data_from_file(input_json_file)
    experiment_name = exp_json_data[0]['experiment_name']

    result_json_data = read_json_data_from_file(result_json_file)
    interval_end_time = result_json_data[0]['interval_end_time']
    interval_start_time = result_json_data[0]['interval_start_time']

    print(DUPLICATE_RECORDS_MSG)
    print(data['data'][0]['errors'][0]['message'])
    assert data['message'] == FAILED_RECORDS_MSG
    assert data['data'][0]['errors'][0]['message'] == DUPLICATE_RECORDS_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
@pytest.mark.parametrize("test_name, interval_end_time", interval_end_times)
def test_update_results_with_valid_and_invalid_interval_duration(test_name, interval_end_time, cluster_type):
    """
    Test Description: This test validates update results by posting results with interval time difference that is not valid for
    the given measurement duration
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/update_results.json"

    json_data = read_json_data_from_file(result_json_file)
    json_data[0]['interval_end_time'] = interval_end_time
    json_file = "/tmp/update_results.json"

    write_json_data_to_file(json_file, json_data)

    response = update_results(json_file)

    data = response.json()
    if test_name == "valid_plus_30s" or test_name == "valid_minus_30s":
        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG
    elif test_name == "invalid_zero_diff":
        assert response.status_code == ERROR_STATUS_CODE
        assert data['status'] == ERROR_STATUS
        assert data['message'] == FAILED_RECORDS_MSG
        assert data['data'][0]['errors'][0]['message'] == UPDATE_RESULTS_DATE_PRECEDE_ERROR_MSG
    else:
        assert response.status_code == ERROR_STATUS_CODE
        assert data['status'] == ERROR_STATUS
        assert data['message'] == FAILED_RECORDS_MSG
        assert data['data'][0]['errors'][0]['message'] == INVALID_INTERVAL_DURATION_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)


@pytest.mark.sanity
@pytest.mark.parametrize("test_name, interval_end_time", interval_end_times)
def test_update_results_with_valid_and_invalid_interval_duration_for_namespace_experiment(test_name, interval_end_time, cluster_type):
    """
    Test Description: This test validates update results by posting results with interval time difference that is not valid for
    the given measurement duration
    """
    input_json_file = "../json_files/create_exp_namespace.json"

    form_kruize_url(cluster_type)

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # Update results for the experiment
    result_json_file = "../json_files/update_results_namespace.json"

    json_data = read_json_data_from_file(result_json_file)
    json_data[0]['interval_end_time'] = interval_end_time
    json_file = "/tmp/update_results_namespace.json"

    write_json_data_to_file(json_file, json_data)

    response = update_results(json_file)

    data = response.json()
    if test_name == "valid_plus_30s" or test_name == "valid_minus_30s":
        assert response.status_code == SUCCESS_STATUS_CODE
        assert data['status'] == SUCCESS_STATUS
        assert data['message'] == UPDATE_RESULTS_SUCCESS_MSG
    elif test_name == "invalid_zero_diff":
        assert response.status_code == ERROR_STATUS_CODE
        assert data['status'] == ERROR_STATUS
        assert data['message'] == FAILED_RECORDS_MSG
        assert data['data'][0]['errors'][0]['message'] == UPDATE_RESULTS_DATE_PRECEDE_ERROR_MSG
    else:
        assert response.status_code == ERROR_STATUS_CODE
        assert data['status'] == ERROR_STATUS
        assert data['message'] == FAILED_RECORDS_MSG
        assert data['data'][0]['errors'][0]['message'] == INVALID_INTERVAL_DURATION_MSG

    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

@pytest.mark.negative
def test_update_results__duplicate_records_with_single_exp_multiple_results(cluster_type):
    """
    Test Description: This test validates update results with some duplicate results records for a single experiment
    """
    input_json_file = "../json_files/create_exp.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)

    # Create experiment using the specified json
    response = create_experiment(input_json_file)

    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG

    # add results for the experiment
    result_json_file = "../json_files/multiple_duplicate_results_single_exp.json"
    response = update_results(result_json_file)

    # Get the experiment name
    json_data = json.load(open(input_json_file))
    experiment_name = json_data[0]['experiment_name']

    data = response.json()

    # Asserting message and httpcode for each error object
    for item in data['data']:
        for error in item['errors']:
            assert error['message'] == DUPLICATE_RECORDS_MSG
            assert error['httpcode'] == ERROR_409_STATUS_CODE

    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert data['message'] == UPDATE_RESULTS_FAILED_RECORDS_MSG

    # assign params to be passed in listExp
    results = "true"
    recommendations = "false"
    latest = "false"
    response = list_experiments(results, recommendations, latest, experiment_name, True)

    list_exp_json = response.json()
    assert response.status_code == SUCCESS_200_STATUS_CODE

    # Validate the json against the json schema
    # TODO: add list_exp_json_schema

    result_json_arr = read_json_data_from_file(result_json_file)
    expected_results_count = len(result_json_arr) - DUPLICATE_RECORDS_COUNT
    validate_list_exp_results_count(expected_results_count, list_exp_json[0])

    # Delete the experiment
    response = delete_experiment(input_json_file)
    print("delete exp = ", response.status_code)



@pytest.mark.negative
def test_update_results_with_missing_metrics_and_generate_recommendations(cluster_type):
    """
    Test Description: This test validates updating results with missing metrics and then generating recommendations.
    Expected: Update results should fail, and thus no recommendations should be generated.
    """
    input_json_file = "../json_files/create_exp_namespace.json"
    missing_metrics_json_file = "../json_files/missing_metrics_jsons/update_results_missing_metrics_single_namespace.json"

    form_kruize_url(cluster_type)
    response = delete_experiment(input_json_file)
    print(f"Delete experiment response: {response.status_code}")

    # Create experiment
    response = create_experiment(input_json_file)
    data = response.json()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert data['status'] == SUCCESS_STATUS
    assert data['message'] == CREATE_EXP_SUCCESS_MSG
    experiment_name = json.load(open(input_json_file))[0]['experiment_name'].strip()

    # Update results with missing metrics
    response = update_results(missing_metrics_json_file)
    data = response.json()
    assert response.status_code == ERROR_STATUS_CODE
    assert data['status'] == ERROR_STATUS
    assert "Performance profile: [Missing one of the following mandatory parameters for experiment - namespace-demo" in data['data'][0]['errors'][0]['message']

    # Try to generate recommendations (should not be present)
    recommendations_response = generate_recommendations(experiment_name=experiment_name)
    recommendations_data = recommendations_response.json()

    assert recommendations_response.status_code == ERROR_STATUS_CODE
    assert recommendations_data["status"] == ERROR_STATUS
    assert "message" in recommendations_data
    assert experiment_name in recommendations_data["message"]

    response = delete_experiment(input_json_file)
    print(f"Delete experiment response: {response.status_code}")
