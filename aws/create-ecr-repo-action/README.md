# Create ECR Repository Action

This action creates an ECR repository if it doesn't already exist, if the repo already exists this action does nothing.

## Create ECR Repo

```yaml
          
      - name: Create ECR Repositories
        uses: VFGroup-VBIT/vbitdc-opf-actions/aws/create-ecr-repo-action@main
        with:
            role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/Github-Runners-Access
            role-session-name: GitHub_to_AWS_via_FederatedOIDC_Run_ID_${{ github.run_id }} 
            aws-region: eu-west-1
            repo_names: '["login","assessment","content","profile","xplain"]'
            ecr_namespaces: '["stage"]'
            project_name: "private-vhub"
            additional_aws_account_ids: '["878202868047"]'
            tags: '[{"Key": "Project", "Value": "private-vhub"}, {"Key": "Environment", "Value": "prod"}, {"Key": "ManagedBy", "Value": "fathalla.ebrahem@vodafone.com"}, {"Key": "Confidentiality", "Value": "C2"}, {"Key": "TaggingVersion", "Value": "V2.4"}, {"Key": "SecurityZone", "Value": "A"}]'
```

When creating the repository it will automatically apply the lifecycle policy which is in the root directory in the project as defined [here](lifecycle_policy.json)
