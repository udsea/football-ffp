import boto3
import json
from pathlib import Path
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET

class S3Uploader:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    
    def upload_file(self, file_path, s3_key):
        """Upload a file to S3"""
        try:
            with open(file_path, 'rb') as f:
                self.s3_client.upload_fileobj(
                    f, 
                    S3_BUCKET, 
                    s3_key,
                    ExtraArgs={'ContentType': 'application/json'}
                )
            
            print(f"Uploaded {file_path} to s3://{S3_BUCKET}/{s3_key}")
            return True
            
        except Exception as e:
            print(f"Error uploading {file_path}: {e}")
            return False
    
    def upload_ffp_data(self):
        """Upload FFP data and create manifest for QuickSight"""
        data_path = Path(__file__).parent.parent / "data" / "ffp_data_2023.json"
        s3_key = "raw-data/ffp_data_2023.json"
        
        try:
            # Check if data file exists
            if not data_path.exists():
                raise FileNotFoundError(f"Data file not found: {data_path}")
            
            # Upload main data file
            self.upload_file(data_path, s3_key)
            
            # Create and upload manifest for QuickSight
            manifest_data = {
                "fileLocations": [
                    {
                        "URIPrefixes": [f"s3://{S3_BUCKET}/raw-data/"]
                    }
                ],
                "globalUploadSettings": {
                    "format": "JSON"
                }
            }
            
            manifest_path = Path(__file__).parent.parent / "data" / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)
            
            self.upload_file(manifest_path, "manifest.json")
            
            print("FFP data and manifest uploaded successfully")
            return True
            
        except Exception as e:
            print(f"Error uploading FFP data: {e}")
            return False

if __name__ == "__main__":
    uploader = S3Uploader()
    uploader.upload_ffp_data()