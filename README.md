# This is demo project how to deploy a lambda function by Terraform

### How to pakage this application.

1. You should create a virtualenv for Python. I'm using Python 3.6
2. Build the source code to create a zip file. 
```
./build.sh
```

### How to deploy application to Lambda.

1. Install Terraform.
2. Configure AWS creadential. 
3. Run Terraform command to deploy

```
terraform init
terraform apply
```

### How to verify the application.

1. Upload the text file to S3.
2. Check the S3 output bucket.
3. Access Athena to query the data.

