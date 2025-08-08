import os
from dotenv import load_dotenv

load_dotenv()

CLUBS = [
    {"name": "Manchester City", "id": "man-city"},
    {"name": "Manchester United", "id": "man-united"},
    {"name": "Arsenal", "id": "arsenal"},
    {"name": "Chelsea", "id": "chelsea"},
    {"name": "Liverpool", "id": "liverpool"},
    {"name": "Tottenham", "id": "tottenham"},
    {"name": "Brighton", "id": "brighton"}
]

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "football-ffp-data")
OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT")
QUICKSIGHT_ACCOUNT_ID = os.getenv("QUICKSIGHT_ACCOUNT_ID")

FFP_METRICS = [
    "revenue",
    "wages", 
    "transfer_spending",
    "net_spend",
    "profit_loss",
    "debt",
    "squad_cost"
]