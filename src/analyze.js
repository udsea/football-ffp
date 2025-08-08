const { BedrockRuntimeClient, InvokeModelCommand } = require('@aws-sdk/client-bedrock-runtime');
const fs = require('fs').promises;
const path = require('path');
const VectorStore = require('./vector-store');
const { AWS_CONFIG } = require('./config');

class FFPAnalyzer {
  constructor() {
    this.bedrockClient = new BedrockRuntimeClient(AWS_CONFIG);
    this.vectorStore = new VectorStore();
  }

  async analyzeWithBedrock(prompt, data) {
    try {
      const command = new InvokeModelCommand({
        modelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
        body: JSON.stringify({
          anthropic_version: 'bedrock-2023-05-31',
          max_tokens: 2000,
          messages: [{
            role: 'user',
            content: `${prompt}\n\nData: ${JSON.stringify(data, null, 2)}`
          }]
        }),
        contentType: 'application/json',
        accept: 'application/json'
      });

      const response = await this.bedrockClient.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      return responseBody.content[0].text;
    } catch (error) {
      console.error('Error with Bedrock analysis:', error);
      throw error;
    }
  }

  async performFFPAnalysis() {
    try {
      const dataPath = path.join(__dirname, '../data/ffp_data_2023.json');
      const ffpData = JSON.parse(await fs.readFile(dataPath, 'utf8'));

      await this.vectorStore.indexFFPData(ffpData);

      const analyses = [];

      const overallAnalysis = await this.analyzeWithBedrock(
        'Analyze the Financial Fair Play compliance of these Premier League clubs for 2023. Identify which clubs are at risk of FFP violations and explain the key financial metrics that indicate compliance or non-compliance.',
        ffpData
      );

      analyses.push({
        type: 'overall_ffp_compliance',
        analysis: overallAnalysis
      });

      const riskAnalysis = await this.analyzeWithBedrock(
        'Rank these clubs by their FFP risk level (high, medium, low) and explain the financial indicators that contribute to each risk assessment. Focus on debt levels, wage-to-revenue ratios, and transfer spending patterns.',
        ffpData
      );

      analyses.push({
        type: 'risk_assessment',
        analysis: riskAnalysis
      });

      const comparisonAnalysis = await this.analyzeWithBedrock(
        'Compare the financial strategies of the Big 6 clubs versus Brighton. What makes Brighton\'s approach different, and how does their financial model compare in terms of sustainability?',
        ffpData
      );

      analyses.push({
        type: 'strategic_comparison',
        analysis: comparisonAnalysis
      });

      const outputPath = path.join(__dirname, '../data/ffp_analysis_2023.json');
      await fs.writeFile(outputPath, JSON.stringify({
        timestamp: new Date().toISOString(),
        analyses,
        raw_data: ffpData
      }, null, 2));

      console.log(`Analysis completed and saved to ${outputPath}`);
      return analyses;

    } catch (error) {
      console.error('Error performing FFP analysis:', error);
      throw error;
    }
  }

  async queryFFPData(question) {
    try {
      const similarClubs = await this.vectorStore.searchSimilar(question, 3);
      
      const context = similarClubs.map(club => 
        `${club.club}: ${JSON.stringify(club.metadata, null, 2)}`
      ).join('\n\n');

      const analysis = await this.analyzeWithBedrock(
        `Answer this question about Football Financial Fair Play: "${question}"\n\nUse this context about similar clubs:`,
        context
      );

      return {
        question,
        answer: analysis,
        relevant_clubs: similarClubs.map(c => c.club)
      };
    } catch (error) {
      console.error('Error querying FFP data:', error);
      throw error;
    }
  }
}

if (require.main === module) {
  const analyzer = new FFPAnalyzer();
  analyzer.performFFPAnalysis()
    .then(() => console.log('FFP analysis completed'))
    .catch(console.error);
}

module.exports = FFPAnalyzer;