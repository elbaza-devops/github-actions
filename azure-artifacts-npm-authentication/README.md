# Azure Artifacts NPM Authentication Example

This directory contains resources and examples for authenticating and publishing npm packages to Azure Artifacts using GitHub Actions.

## Files

- `workflow-ex.yaml`: Example GitHub Actions workflow for authenticating to Azure Artifacts, installing dependencies, and publishing npm packages.
- `action.yaml`: Composite GitHub Action definition for Azure Artifacts npm authentication.

## Usage

1. **Configure Secrets**: Add your Azure DevOps Personal Access Token (PAT) as a secret named `AZURE_ARTIFACTS_PAT` in your GitHub repository.
2. **Update Workflow**: Modify `workflow-ex.yaml` as needed for your organization, project, and feed names.
3. **Run Workflow**: On push to the `main` branch, the workflow will authenticate, install dependencies, and publish your npm package to Azure Artifacts.

## References
- [Azure Artifacts Documentation](https://docs.microsoft.com/en-us/azure/devops/artifacts/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
