# GitLab CI Linter

This script is a robust tool for validating and linting GitLab CI/CD pipelines. It validates `.gitlab-ci.yml` files against a JSON schema, checks for logical errors across jobs and stages, and suggests improvements for performance and maintainability.

## Features

- **YAML Parsing**: Validates YAML syntax.
- **Schema Validation**: Ensures the pipeline structure adheres to GitLab CI/CD standards.
- **Include Resolution**: Recursively resolves and validates `include` directives.
- **Stage Validation**: Ensures all jobs reference valid stages.
- **Needs/Dependencies Validation**: Verifies `needs` and `dependencies` configurations.
- **Caching Recommendations**: Warns about jobs missing caching.
- **Cross-File Job Validation**: Ensures consistency across modular `.gitlab-ci.yml` files.
- **Logging**: Provides detailed logs for errors, warnings, and info messages.

## Requirements

- Python 3.6+
- Required Python Libraries:
  - `PyYAML`
  - `jsonschema`

Install the dependencies using:

```bash
pip install pyyaml jsonschema
```

## Installation

### Quick Installation for Linux OS

You can install the GitLab CI Linter using the following one-liner command:

```bash
curl -fsSL https://raw.githubusercontent.com/stefanhall2704/GitLabPipelineValidator/refs/heads/main/installer.sh | sudo bash
```

This command will:
- Install the linter script (`gitlab_ci_linter.py`) and schema (`schema.json`) to `/usr/local/lib/validate-pipeline-lib/`.
- Install the `validate-pipeline` executable script to `/usr/local/bin/`.

### Verify Installation

Run the following command to validate installation:

```bash
validate-pipeline
```

This will execute the linter in the current directory.

## Usage

### Command-Line Usage

1. Clone this repository or copy the script into your working directory.
2. Place the JSON schema file (`schema.json`) for GitLab CI/CD validation in the same directory.
3. Run the script from the command line:

```bash
python linter.py [DIRECTORY] [SCHEMA_PATH]
```

- **DIRECTORY**: The directory containing `.gitlab-ci.yml` files. Defaults to the current working directory.
- **SCHEMA_PATH**: Path to the JSON schema file. Defaults to `schema.json` in the current directory.

### Automated Validation Script

To simplify validation, create an executable script for automated usage:

1. Save the following script as `/usr/local/bin/validate-pipeline`:

```bash
#!/bin/bash

# Path to the linter script and schema
LINTER_SCRIPT="/usr/local/lib/validate-pipeline-lib/gitlab_ci_linter.py"
SCHEMA_FILE="/usr/local/lib/validate-pipeline-lib/schema.json"

# Ensure Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed. Exiting."
    exit 1
fi

# Ensure the linter script exists
if [[ ! -f "$LINTER_SCRIPT" ]]; then
    echo "Linter script not found at $LINTER_SCRIPT. Exiting."
    exit 1
fi

# Run the linter
python3 "$LINTER_SCRIPT" "$PWD" "$SCHEMA_FILE"
```

2. Make the script executable:

```bash
chmod +x /usr/local/bin/validate-pipeline
```

3. Store the linter script and schema file in `/usr/local/lib/validate-pipeline-lib/`.

4. Run the validator from any directory:

```bash
validate-pipeline
```

This will automatically validate all `.gitlab-ci.yml` files in the current directory using the linter.

## Example

```bash
python linter.py /path/to/gitlab-ci-files schema.json
```

Or use the automated script:

```bash
validate-pipeline
```

## Output

The script provides a detailed report:

- **Errors**: Critical issues preventing the pipeline from running.
- **Warnings**: Potential improvements or inefficiencies.
- **Info**: General feedback about valid configurations.

### Sample Output

```plaintext
2024-12-10 10:00:00 - INFO - File '/path/to/.gitlab-ci.yml' structure and stage references are valid.
2024-12-10 10:00:01 - WARNING - File '/path/to/another-file.gitlab-ci.yml': Job 'build' does not utilize caching. Consider adding a cache for efficiency.
2024-12-10 10:00:02 - ERROR - Validation Error in 'some-file.gitlab-ci.yml': Job 'deploy' references undefined stage 'production'.
```

## Extending the Script

### Adding New Checks
You can extend the script by adding new validation functions. For example:

1. Create a function like `validate_artifacts` to check for missing artifact configurations.
2. Call the new function in the `validate_file` method.

### Integrating into CI/CD
Integrate this linter into your CI/CD pipeline to automatically validate `.gitlab-ci.yml` files before merging changes.

```yaml
lint:
  script:
    - python linter.py . schema.json
  only:
    - merge_requests
```

## Contributing

Feel free to contribute to this project by submitting issues or pull requests. For major changes, please open an issue first to discuss your ideas.

