# Install AWS CLI Action

This is a simpl action that is designed to install the AWS cli tool.

## Install CLI

### install cli without logging in
```yaml
steps:
  - uses: VFGroup-VBIT/vbitdc-opf-actions/aws/install-cli-action@main
```

### install cli with login

```yaml
steps:
  - uses: VFGroup-VBIT/vbitdc-opf-actions/aws/install-cli-action@main
    with:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-region: eu-west-1
```
