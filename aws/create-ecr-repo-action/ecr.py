import boto3
import os
import json


def create_ecr_repositories(project_name, repo_names, ecr_namespaces, aws_region,account_id, tags, additional_aws_account_ids):
    ecr_client = boto3.client('ecr', region_name=aws_region)

    for repo_name in repo_names:
        full_repo_name = construct_full_repo_name(
            project_name, ecr_namespaces, repo_name)

        try:
            print(f"ECR repository '{full_repo_name}' creating...")
            response = ecr_client.create_repository(
                repositoryName=full_repo_name,
                tags=tags,  # Add tags during creation
                imageTagMutability='MUTABLE',
                imageScanningConfiguration={
                    'scanOnPush': True
                },
                encryptionConfiguration={
                    'encryptionType': 'KMS'
                }
            )
            repository_arn = response['repository']['repositoryArn']
            print(f"ECR repository '{full_repo_name}' created successfully.")

            # Attach the lifecycle policy if the file exists
            lifecycle_policy_filename = "lifecycle_policy.json"
            if os.path.exists(lifecycle_policy_filename):
                attach_lifecycle_policy(ecr_client, full_repo_name)

            attach_registry_policy(
                ecr_client, full_repo_name, account_id, additional_aws_account_ids)

        except ecr_client.exceptions.RepositoryAlreadyExistsException:
            print(f"ECR repository '{full_repo_name}' already exists.")

            # Retrieve the repository ARN since it's not available from create_repository
            response = ecr_client.describe_repositories(
                repositoryNames=[full_repo_name]
            )
            repository_arn = response['repositories'][0]['repositoryArn']
            
            # Update tags for the existing repository
            update_repository_tags(ecr_client, repository_arn, tags)

            # Attach the lifecycle policy if the file exists
            lifecycle_policy_filename = "lifecycle_policy.json"
            if os.path.exists(lifecycle_policy_filename):
                attach_lifecycle_policy(ecr_client, full_repo_name)

            attach_registry_policy(
                ecr_client, full_repo_name, account_id, additional_aws_account_ids)


def construct_full_repo_name(project_name, ecr_namespaces, repo_name):
    if project_name and ecr_namespaces:
        return f"{project_name}/{ecr_namespaces[0]}/{repo_name}"
    elif not project_name and ecr_namespaces:
        return f"{ecr_namespaces[0]}/{repo_name}"
    elif project_name and not ecr_namespaces:
        return f"{project_name}/{repo_name}"
    else:
        return repo_name


def attach_lifecycle_policy(ecr_client, repository_name):
    # Read the lifecycle policy from the file
    policy_filename = "lifecycle_policy.json"
    with open(policy_filename, 'r') as policy_file:
        lifecycle_policy = json.load(policy_file)

    # Attach the lifecycle policy to the ECR repository
    ecr_client.put_lifecycle_policy(
        repositoryName=repository_name,
        lifecyclePolicyText=json.dumps(lifecycle_policy, indent=2)
    )

    print(f"Lifecycle policy attached to '{repository_name}'.")


def attach_registry_policy(ecr_client, repository_name, account_id, additional_aws_account_ids):
    # Define the repository policy
    repository_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        f"arn:aws:iam::{account_id}:root"
                    ] + [f"arn:aws:iam::{aws_account_id}:root" for aws_account_id in additional_aws_account_ids]
                },
                "Action": [
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer"
                ],
            }
        ]
    }

    # Attach the repository policy
    response = ecr_client.set_repository_policy(
        repositoryName=repository_name,
        policyText=json.dumps(repository_policy, indent=2)
    )

    print(f"Repository policy attached to '{repository_name}'.")
    print("Response:", response)


def update_repository_tags(ecr_client, repository_arn, tags):
    # Use tag_resource to add or update tags
    ecr_client.tag_resource(
        resourceArn=repository_arn,
        tags=tags
    )
    print(f"Tags updated for repository ARN '{repository_arn}'.")


if __name__ == "__main__":
    # Read values from environment variables
    project_name = os.getenv("PROJECT_NAME", "")
    repo_names = json.loads(os.getenv("REPO_NAMES", "[]"))
    ecr_namespaces = json.loads(os.getenv("ECR_NAMESPACES", "[]"))
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    additional_aws_account_ids = json.loads(
        os.getenv("ADDITIONAL_AWS_ACCOUNT_IDS", "[]"))
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    tags = json.loads(os.getenv("TAGS", "[]"))
    create_ecr_repositories(project_name, repo_names,
                            ecr_namespaces, aws_region, account_id, tags, additional_aws_account_ids)
