require('dotenv').config();

const CLUBS = [
  { name: 'Manchester City', id: 'man-city' },
  { name: 'Manchester United', id: 'man-united' },
  { name: 'Arsenal', id: 'arsenal' },
  { name: 'Chelsea', id: 'chelsea' },
  { name: 'Liverpool', id: 'liverpool' },
  { name: 'Tottenham', id: 'tottenham' },
  { name: 'Brighton', id: 'brighton' }
];

const AWS_CONFIG = {
  region: process.env.AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
};

const S3_BUCKET = process.env.S3_BUCKET_NAME || 'football-ffp-data';

const FFP_METRICS = [
  'revenue',
  'wages',
  'transfer_spending',
  'net_spend',
  'profit_loss',
  'debt',
  'squad_cost'
];

module.exports = {
  CLUBS,
  AWS_CONFIG,
  S3_BUCKET,
  FFP_METRICS
};