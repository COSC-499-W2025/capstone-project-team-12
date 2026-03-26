# Test File Documentations

## How to use

### CLI Usage

- The example projects are automatically mounted to the container during the build phase under `app/test_projects`. This will not affect the mounting of your own personal repos based on the path specified in the `.env` file

- Simply provide `app/test_projects/<testset>` as the path when prompted by new or incremental analysis workflow.

### Webapp GUI Usage

- Simply navigate to `utils/test_projects' in the file upload selection and upload any of the testsets as you would any other file.

## File Descriptions

- **incremental example** folder contains 2 zipped snapshots of this capstone repo intended to demonstrate incremental analysis capabilities

- **individual examples** folder contains a selection of sample projects to choose from consisting of large/collaborative and small/collaborative project examples to demonstrate system functionality with various projects.
If you choose more than one project from her in an analysis, use github details provided in [repo readme.md](../../README.md) for best results.

- **multiple_projects.zip** is zip of all the projects in the 'individual_projects' folder to demonstrate the system's ability to handle multiple projects at once. Primarily intended for use with the CLI since, unlike the Webapp it does not support multiple filepath as input.
