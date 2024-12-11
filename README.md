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

## Usage

1. Clone this repository or copy the script into your working directory.
2. Place the JSON schema file (`schema.json`) for GitLab CI/CD validation in the same directory.
3. Run the script from the command line:

```bash
python linter.py [DIRECTORY] [SCHEMA_PATH]
```

- **DIRECTORY**: The directory containing `.gitlab-ci.yml` files. Defaults to the current working directory.
- **SCHEMA_PATH**: Path to the JSON schema file. Defaults to `schema.json` in the current directory.

## Example

```bash
python linter.py /path/to/gitlab-ci-files schema.json
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

## License

This project is licensed under the MIT License.
