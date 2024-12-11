import os
import yaml
import json
import jsonschema
from jsonschema.exceptions import ValidationError
import sys
import logging

def setup_logger():
    """Setup logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

setup_logger()

def validate_job_stages(merged_data, stages, file_path):
    """
    Validate that all jobs reference a valid stage from the main file's 'stages'.
    """
    errors = []

    for job_name, job_config in merged_data.items():
        if not isinstance(job_config, dict):
            continue
        stage = job_config.get("stage")
        if stage and stage not in stages:
            errors.append(
                f"File '{file_path}': Job '{job_name}' references undefined stage '{stage}'."
            )

    return errors

def extract_stages_from_main(ci_files):
    """
    Extract the 'stages' section from the main .gitlab-ci.yml or .gitlab-ci.yaml file.
    """
    main_file = None
    for file in ci_files:
        if os.path.basename(file) in [".gitlab-ci.yml", ".gitlab-ci.yaml"]:
            main_file = file
            break

    if not main_file:
        logging.error("Main .gitlab-ci.yml or .gitlab-ci.yaml file not found.")
        sys.exit(1)

    yaml_data, _ = load_yaml(main_file)
    return yaml_data.get("stages", [])

def find_gitlab_ci_files(directory):
    """
    Find all .gitlab-ci.yml files in the given directory and its subdirectories.
    """
    ci_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".gitlab-ci.yml"):
                ci_files.append(os.path.join(root, file))
    return ci_files

def load_yaml(file_path):
    """
    Load a YAML file and return its parsed content and raw lines.
    """
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f), list(f.readlines())
    except yaml.YAMLError as e:
        logging.error(f"YAML Parsing Error in {file_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        sys.exit(1)

def resolve_includes(yaml_data, base_path, all_files, resolved_files=None):
    """
    Resolve and merge 'include' entries in the GitLab CI configuration.
    """
    if resolved_files is None:
        resolved_files = set()

    merged_data = yaml_data.copy()

    if "include" not in yaml_data:
        return merged_data

    includes = yaml_data.pop("include")
    if not isinstance(includes, list):
        includes = [includes]

    for include in includes:
        if "local" in include:
            local_path = os.path.abspath(os.path.join(base_path, include["local"]))
            if local_path in resolved_files:
                continue  # Skip already processed files
            resolved_files.add(local_path)

            if local_path not in all_files:
                logging.warning(f"Included file '{local_path}' not found.")
                continue

            included_data, _ = load_yaml(local_path)
            included_data = resolve_includes(included_data, os.path.dirname(local_path), all_files, resolved_files)
            merged_data.update(included_data)
        else:
            logging.warning(f"Unsupported include type in {include}. Only 'local' includes are supported.")

    return merged_data

def validate_needs_dependencies(data, all_defined_jobs, file_path):
    """
    Validate 'needs' and 'dependencies' fields for a single file.
    """
    defined_jobs = {key for key in data.keys() if key not in ["stages", "variables", "image", "default"]}
    errors = []

    for job_name, job_config in data.items():
        if not isinstance(job_config, dict):
            continue

        # Validate "needs"
        if "needs" in job_config:
            for needed_job in job_config["needs"]:
                if isinstance(needed_job, str):
                    # Basic syntax
                    if needed_job not in all_defined_jobs:
                        errors.append(
                            f"File '{file_path}': Job '{job_name}' references undefined job '{needed_job}' in 'needs'."
                        )
                elif isinstance(needed_job, dict):
                    # Advanced syntax
                    if "job" in needed_job and needed_job["job"] not in all_defined_jobs:
                        errors.append(
                            f"File '{file_path}': Job '{job_name}' references undefined job '{needed_job['job']}' in 'needs'."
                        )
                else:
                    errors.append(
                        f"File '{file_path}': Invalid 'needs' entry in job '{job_name}'. Expected string or dictionary."
                    )

        # Validate "dependencies"
        if "dependencies" in job_config:
            for dependency in job_config["dependencies"]:
                if dependency not in all_defined_jobs:
                    errors.append(
                        f"File '{file_path}': Job '{job_name}' references undefined job '{dependency}' in 'dependencies'."
                    )

    return errors

def validate_file(file_path, schema_path, all_defined_jobs, all_files, main_stages):
    """
    Validate a single .gitlab-ci.yml file against the schema and cross-references.
    """
    yaml_data, lines = load_yaml(file_path)

    # Resolve includes and merge configurations
    merged_data = resolve_includes(yaml_data, os.path.dirname(file_path), all_files)

    # Schema validation
    structure_valid = True
    try:
        with open(schema_path, 'r') as schema_file:
            schema = json.load(schema_file)
        jsonschema.validate(instance=merged_data, schema=schema)
    except ValidationError as e:
        logging.error(f"Validation Error in '{file_path}': {e.message}")
        structure_valid = False

    # Validate job stages against main file's stages
    stage_errors = validate_job_stages(merged_data, main_stages, file_path)

    # Report results
    if structure_valid and not stage_errors:
        logging.info(f"File '{file_path}' structure and stage references are valid.")
    else:
        if structure_valid:
            logging.warning(f"File '{file_path}' structure is valid but contains stage validation errors:")
        for error in stage_errors:
            logging.error(error)

def collect_all_jobs(ci_files):
    """
    Collect all job names from all .gitlab-ci.yml files for cross-reference validation.
    """
    all_jobs = set()
    for file_path in ci_files:
        yaml_data, _ = load_yaml(file_path)
        all_jobs.update(key for key in yaml_data.keys() if key not in ["stages", "variables", "image", "default"])
    return all_jobs

if __name__ == "__main__":
    # Default to current directory if no path is provided
    directory = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    schema_path = sys.argv[2] if len(sys.argv) > 2 else "schema.json"

    # Ensure directory exists
    if not os.path.isdir(directory):
        logging.error(f"Directory '{directory}' does not exist.")
        sys.exit(1)

    # Find all .gitlab-ci.yml files
    ci_files = find_gitlab_ci_files(directory)
    if not ci_files:
        logging.info(f"No .gitlab-ci.yml files found in directory '{directory}'.")
        sys.exit(0)

    # Extract stages from main .gitlab-ci.yml
    main_stages = extract_stages_from_main(ci_files)

    # Collect all job definitions across files
    all_defined_jobs = collect_all_jobs(ci_files)

    # Validate each file
    for ci_file in ci_files:
        validate_file(ci_file, schema_path, all_defined_jobs, ci_files, main_stages)

