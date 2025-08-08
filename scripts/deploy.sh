#!/bin/bash

set -e

PROJECT_NAME="football-ffp"
STACK_NAME="${PROJECT_NAME}-infrastructure"
REGION="us-east-1"

echo "Deploying Football FFP Analysis infrastructure..."

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file infrastructure/main.yaml \
  --stack-name $STACK_NAME \
  --parameter-overrides ProjectName=$PROJECT_NAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Get stack outputs
echo "Getting stack outputs..."
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
  --output text)

OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchEndpoint`].OutputValue' \
  --output text)

# Update .env file
echo "Updating .env file..."
cat > .env << EOF
AWS_REGION=$REGION
S3_BUCKET_NAME=$S3_BUCKET
OPENSEARCH_ENDPOINT=https://$OPENSEARCH_ENDPOINT
QUICKSIGHT_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
EOF

echo "Deployment complete!"
echo "S3 Bucket: $S3_BUCKET"
echo "OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
echo ""
echo "Next steps:"
echo "1. Run 'pip install -r requirements.txt' to install dependencies"
echo "2. Run 'python src/scraper.py' to collect data"
echo "3. Run 'python src/upload_s3.py' to upload to S3"
echo "4. Run 'python src/analyze.py' to perform FFP analysis"