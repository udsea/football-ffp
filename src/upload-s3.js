const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
const fs = require('fs').promises;
const path = require('path');
const { AWS_CONFIG, S3_BUCKET } = require('./config');

class S3Uploader {
  constructor() {
    this.s3Client = new S3Client(AWS_CONFIG);
  }

  async uploadFile(filePath, s3Key) {
    try {
      const fileContent = await fs.readFile(filePath);
      
      const command = new PutObjectCommand({
        Bucket: S3_BUCKET,
        Key: s3Key,
        Body: fileContent,
        ContentType: 'application/json'
      });

      const result = await this.s3Client.send(command);
      console.log(`Uploaded ${filePath} to s3://${S3_BUCKET}/${s3Key}`);
      return result;
    } catch (error) {
      console.error(`Error uploading ${filePath}:`, error);
      throw error;
    }
  }

  async uploadFFPData() {
    const dataPath = path.join(__dirname, '../data/ffp_data_2023.json');
    const s3Key = 'raw-data/ffp_data_2023.json';
    
    try {
      await fs.access(dataPath);
      await this.uploadFile(dataPath, s3Key);
      
      const manifestData = {
        fileLocations: [
          {
            URIPrefixes: [`s3://${S3_BUCKET}/raw-data/`]
          }
        ],
        globalUploadSettings: {
          format: 'JSON'
        }
      };
      
      const manifestPath = path.join(__dirname, '../data/manifest.json');
      await fs.writeFile(manifestPath, JSON.stringify(manifestData, null, 2));
      await this.uploadFile(manifestPath, 'manifest.json');
      
      console.log('FFP data and manifest uploaded successfully');
    } catch (error) {
      console.error('Error uploading FFP data:', error);
      throw error;
    }
  }
}

if (require.main === module) {
  const uploader = new S3Uploader();
  uploader.uploadFFPData()
    .then(() => console.log('Upload completed'))
    .catch(console.error);
}

module.exports = S3Uploader;