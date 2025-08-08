import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, OPENSEARCH_ENDPOINT

class VectorStore:
    def __init__(self):
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Extract hostname from OPENSEARCH_ENDPOINT
        if OPENSEARCH_ENDPOINT:
            host = OPENSEARCH_ENDPOINT.replace('https://', '').replace('http://', '')
            self.opensearch_client = OpenSearch(
                hosts=[{'host': host, 'port': 443}],
                http_auth=('admin', 'admin'),
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )
        else:
            self.opensearch_client = None
            
        self.index_name = 'ffp-vectors'
    
    def generate_embedding(self, text):
        """Generate embedding using Bedrock Titan"""
        try:
            response = self.bedrock_client.invoke_model(
                modelId='amazon.titan-embed-text-v1',
                body=json.dumps({
                    'inputText': text
                }),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def create_index(self):
        """Create OpenSearch index for vectors"""
        if not self.opensearch_client:
            print("OpenSearch client not initialized")
            return False
            
        try:
            if not self.opensearch_client.indices.exists(index=self.index_name):
                index_body = {
                    'mappings': {
                        'properties': {
                            'club': {'type': 'keyword'},
                            'year': {'type': 'integer'},
                            'text_content': {'type': 'text'},
                            'vector': {
                                'type': 'knn_vector',
                                'dimension': 1536,
                                'method': {
                                    'name': 'hnsw',
                                    'space_type': 'cosinesimil'
                                }
                            },
                            'metadata': {'type': 'object'}
                        }
                    }
                }
                
                self.opensearch_client.indices.create(
                    index=self.index_name,
                    body=index_body
                )
                print(f"Created index: {self.index_name}")
            
            return True
            
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    def create_text_content(self, club_data):
        """Create text content for embedding"""
        return f"""Club: {club_data['club']}
Year: {club_data['year']}
Revenue: £{club_data['revenue'] / 1_000_000:.1f}M
Wages: £{club_data['wages'] / 1_000_000:.1f}M
Transfer Spending: £{club_data['transfer_spending'] / 1_000_000:.1f}M
Net Spend: £{club_data['net_spend'] / 1_000_000:.1f}M
Profit/Loss: £{club_data['profit_loss'] / 1_000_000:.1f}M
Debt: £{club_data['debt'] / 1_000_000:.1f}M
Squad Cost: £{club_data['squad_cost'] / 1_000_000:.1f}M
FFP Compliance: {'Yes' if club_data['ffp_compliance'] else 'No'}"""
    
    def index_ffp_data(self, ffp_data):
        """Index FFP data with embeddings"""
        if not self.opensearch_client:
            print("OpenSearch client not initialized - skipping vector indexing")
            return False
            
        try:
            self.create_index()
            
            for club_data in ffp_data:
                text_content = self.create_text_content(club_data)
                embedding = self.generate_embedding(text_content)
                
                doc_body = {
                    'club': club_data['club'],
                    'year': club_data['year'],
                    'text_content': text_content,
                    'vector': embedding,
                    'metadata': club_data
                }
                
                self.opensearch_client.index(
                    index=self.index_name,
                    body=doc_body
                )
                
                print(f"Indexed data for {club_data['club']}")
            
            # Refresh index
            self.opensearch_client.indices.refresh(index=self.index_name)
            print("All FFP data indexed successfully")
            return True
            
        except Exception as e:
            print(f"Error indexing FFP data: {e}")
            return False
    
    def search_similar(self, query, size=5):
        """Search for similar clubs using vector similarity"""
        if not self.opensearch_client:
            print("OpenSearch client not initialized")
            return []
            
        try:
            query_embedding = self.generate_embedding(query)
            
            search_body = {
                'size': size,
                'query': {
                    'knn': {
                        'vector': {
                            'vector': query_embedding,
                            'k': size
                        }
                    }
                }
            }
            
            response = self.opensearch_client.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'score': hit['_score'],
                    'club': hit['_source']['club'],
                    'metadata': hit['_source']['metadata']
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []