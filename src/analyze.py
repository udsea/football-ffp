import boto3
import json
from pathlib import Path
from datetime import datetime
from vector_store import VectorStore
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

class FFPAnalyzer:
    def __init__(self):
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.vector_store = VectorStore()
    
    def analyze_with_bedrock(self, prompt, data):
        """Analyze data using Bedrock Claude"""
        try:
            full_prompt = f"{prompt}\n\nData: {json.dumps(data, indent=2)}"
            
            response = self.bedrock_client.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 2000,
                    'messages': [{
                        'role': 'user',
                        'content': full_prompt
                    }]
                }),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Error with Bedrock analysis: {e}")
            raise
    
    def perform_ffp_analysis(self):
        """Perform comprehensive FFP analysis"""
        try:
            # Load data
            data_path = Path(__file__).parent.parent / "data" / "ffp_data_2023.json"
            with open(data_path, 'r') as f:
                ffp_data = json.load(f)
            
            # Index data in vector store
            self.vector_store.index_ffp_data(ffp_data)
            
            analyses = []
            
            # Overall FFP compliance analysis
            print("Performing overall FFP compliance analysis...")
            overall_analysis = self.analyze_with_bedrock(
                "Analyze the Financial Fair Play compliance of these Premier League clubs for 2023. "
                "Identify which clubs are at risk of FFP violations and explain the key financial "
                "metrics that indicate compliance or non-compliance.",
                ffp_data
            )
            
            analyses.append({
                'type': 'overall_ffp_compliance',
                'analysis': overall_analysis
            })
            
            # Risk assessment
            print("Performing risk assessment...")
            risk_analysis = self.analyze_with_bedrock(
                "Rank these clubs by their FFP risk level (high, medium, low) and explain the "
                "financial indicators that contribute to each risk assessment. Focus on debt levels, "
                "wage-to-revenue ratios, and transfer spending patterns.",
                ffp_data
            )
            
            analyses.append({
                'type': 'risk_assessment', 
                'analysis': risk_analysis
            })
            
            # Strategic comparison
            print("Performing strategic comparison...")
            comparison_analysis = self.analyze_with_bedrock(
                "Compare the financial strategies of the Big 6 clubs versus Brighton. "
                "What makes Brighton's approach different, and how does their financial model "
                "compare in terms of sustainability?",
                ffp_data
            )
            
            analyses.append({
                'type': 'strategic_comparison',
                'analysis': comparison_analysis
            })
            
            # Save results
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'analyses': analyses,
                'raw_data': ffp_data
            }
            
            output_path = Path(__file__).parent.parent / "data" / "ffp_analysis_2023.json"
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"Analysis completed and saved to {output_path}")
            return analyses
            
        except Exception as e:
            print(f"Error performing FFP analysis: {e}")
            raise
    
    def query_ffp_data(self, question):
        """Query FFP data using vector similarity"""
        try:
            similar_clubs = self.vector_store.search_similar(question, 3)
            
            context = "\n\n".join([
                f"{club['club']}: {json.dumps(club['metadata'], indent=2)}"
                for club in similar_clubs
            ])
            
            analysis = self.analyze_with_bedrock(
                f'Answer this question about Football Financial Fair Play: "{question}"\n\n'
                f'Use this context about similar clubs:',
                context
            )
            
            return {
                'question': question,
                'answer': analysis,
                'relevant_clubs': [club['club'] for club in similar_clubs]
            }
            
        except Exception as e:
            print(f"Error querying FFP data: {e}")
            raise

if __name__ == "__main__":
    analyzer = FFPAnalyzer()
    analyzer.perform_ffp_analysis()
    print("FFP analysis completed")