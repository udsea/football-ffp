import boto3
import json
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, QUICKSIGHT_ACCOUNT_ID

class QuickSightSetup:
    def __init__(self):
        self.quicksight_client = boto3.client(
            'quicksight',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.account_id = QUICKSIGHT_ACCOUNT_ID
    
    def create_dataset(self):
        """Create QuickSight dataset"""
        try:
            response = self.quicksight_client.create_data_set(
                AwsAccountId=self.account_id,
                DataSetId='ffp-dataset',
                Name='Football FFP Analysis Dataset',
                PhysicalTableMap={
                    'ffp-table': {
                        'S3Source': {
                            'DataSourceArn': f'arn:aws:quicksight:{AWS_REGION}:{self.account_id}:datasource/football-ffp-datasource',
                            'InputColumns': [
                                {'Name': 'club', 'Type': 'STRING'},
                                {'Name': 'year', 'Type': 'INTEGER'},
                                {'Name': 'revenue', 'Type': 'DECIMAL'},
                                {'Name': 'wages', 'Type': 'DECIMAL'},
                                {'Name': 'transfer_spending', 'Type': 'DECIMAL'},
                                {'Name': 'net_spend', 'Type': 'DECIMAL'},
                                {'Name': 'profit_loss', 'Type': 'DECIMAL'},
                                {'Name': 'debt', 'Type': 'DECIMAL'},
                                {'Name': 'squad_cost', 'Type': 'DECIMAL'},
                                {'Name': 'ffp_compliance', 'Type': 'STRING'}
                            ]
                        }
                    }
                },
                ImportMode='SPICE'
            )
            
            print(f"Dataset created: {response['DataSetId']}")
            return response
            
        except Exception as e:
            print(f"Error creating dataset: {e}")
            raise
    
    def create_dashboard_config(self):
        """Create dashboard configuration"""
        dashboard_config = {
            'title': 'Football FFP Analysis Dashboard',
            'charts': [
                {
                    'title': 'Revenue vs Wages by Club',
                    'type': 'scatter',
                    'x_axis': 'revenue',
                    'y_axis': 'wages',
                    'color': 'ffp_compliance'
                },
                {
                    'title': 'FFP Compliance Status',
                    'type': 'pie',
                    'dimension': 'ffp_compliance'
                },
                {
                    'title': 'Transfer Spending Comparison',
                    'type': 'bar',
                    'x_axis': 'club',
                    'y_axis': 'transfer_spending'
                },
                {
                    'title': 'Debt Levels by Club',
                    'type': 'bar',
                    'x_axis': 'club',
                    'y_axis': 'debt'
                }
            ]
        }
        
        print("Dashboard configuration created:")
        print(json.dumps(dashboard_config, indent=2))
        return dashboard_config

if __name__ == "__main__":
    setup = QuickSightSetup()
    setup.create_dataset()
    setup.create_dashboard_config()
    print("QuickSight setup completed")