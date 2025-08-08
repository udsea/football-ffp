const { BedrockRuntimeClient, InvokeModelCommand } = require('@aws-sdk/client-bedrock-runtime');
const { Client } = require('@opensearch-project/opensearch');
const { AWS_CONFIG } = require('./config');

class VectorStore {
  constructor() {
    this.bedrockClient = new BedrockRuntimeClient(AWS_CONFIG);
    this.opensearchClient = new Client({
      node: process.env.OPENSEARCH_ENDPOINT,
      auth: {
        username: 'admin',
        password: 'admin'
      }
    });
    this.indexName = 'ffp-vectors';
  }

  async generateEmbedding(text) {
    try {
      const command = new InvokeModelCommand({
        modelId: 'amazon.titan-embed-text-v1',
        body: JSON.stringify({
          inputText: text
        }),
        contentType: 'application/json',
        accept: 'application/json'
      });

      const response = await this.bedrockClient.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      return responseBody.embedding;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw error;
    }
  }

  async createIndex() {
    try {
      const indexExists = await this.opensearchClient.indices.exists({
        index: this.indexName
      });

      if (!indexExists.body) {
        await this.opensearchClient.indices.create({
          index: this.indexName,
          body: {
            mappings: {
              properties: {
                club: { type: 'keyword' },
                year: { type: 'integer' },
                text_content: { type: 'text' },
                vector: {
                  type: 'knn_vector',
                  dimension: 1536,
                  method: {
                    name: 'hnsw',
                    space_type: 'cosinesimil'
                  }
                },
                metadata: { type: 'object' }
              }
            }
          }
        });
        console.log(`Created index: ${this.indexName}`);
      }
    } catch (error) {
      console.error('Error creating index:', error);
      throw error;
    }
  }

  async indexFFPData(ffpData) {
    try {
      await this.createIndex();

      for (const clubData of ffpData) {
        const textContent = this.createTextContent(clubData);
        const embedding = await this.generateEmbedding(textContent);

        await this.opensearchClient.index({
          index: this.indexName,
          body: {
            club: clubData.club,
            year: clubData.year,
            text_content: textContent,
            vector: embedding,
            metadata: clubData
          }
        });

        console.log(`Indexed data for ${clubData.club}`);
      }

      await this.opensearchClient.indices.refresh({
        index: this.indexName
      });

      console.log('All FFP data indexed successfully');
    } catch (error) {
      console.error('Error indexing FFP data:', error);
      throw error;
    }
  }

  createTextContent(clubData) {
    return `Club: ${clubData.club}
Year: ${clubData.year}
Revenue: £${(clubData.revenue / 1000000).toFixed(1)}M
Wages: £${(clubData.wages / 1000000).toFixed(1)}M
Transfer Spending: £${(clubData.transfer_spending / 1000000).toFixed(1)}M
Net Spend: £${(clubData.net_spend / 1000000).toFixed(1)}M
Profit/Loss: £${(clubData.profit_loss / 1000000).toFixed(1)}M
Debt: £${(clubData.debt / 1000000).toFixed(1)}M
Squad Cost: £${(clubData.squad_cost / 1000000).toFixed(1)}M
FFP Compliance: ${clubData.ffp_compliance ? 'Yes' : 'No'}`;
  }

  async searchSimilar(query, size = 5) {
    try {
      const queryEmbedding = await this.generateEmbedding(query);

      const response = await this.opensearchClient.search({
        index: this.indexName,
        body: {
          size,
          query: {
            knn: {
              vector: {
                vector: queryEmbedding,
                k: size
              }
            }
          }
        }
      });

      return response.body.hits.hits.map(hit => ({
        score: hit._score,
        club: hit._source.club,
        metadata: hit._source.metadata
      }));
    } catch (error) {
      console.error('Error searching vectors:', error);
      throw error;
    }
  }
}

module.exports = VectorStore;