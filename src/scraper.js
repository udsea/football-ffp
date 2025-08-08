const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs').promises;
const path = require('path');
const { CLUBS } = require('./config');

class FFPDataScraper {
  constructor() {
    this.baseUrl = 'https://www.transfermarkt.com';
    this.headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    };
  }

  async scrapeClubFinancials(clubId) {
    try {
      console.log(`Scraping financial data for ${clubId}...`);
      
      const mockData = {
        club: clubId,
        year: 2023,
        revenue: Math.floor(Math.random() * 500 + 200) * 1000000,
        wages: Math.floor(Math.random() * 300 + 100) * 1000000,
        transfer_spending: Math.floor(Math.random() * 200 + 50) * 1000000,
        net_spend: Math.floor(Math.random() * 100 - 50) * 1000000,
        profit_loss: Math.floor(Math.random() * 100 - 50) * 1000000,
        debt: Math.floor(Math.random() * 400 + 100) * 1000000,
        squad_cost: Math.floor(Math.random() * 800 + 300) * 1000000,
        ffp_compliance: Math.random() > 0.3,
        scraped_at: new Date().toISOString()
      };

      await new Promise(resolve => setTimeout(resolve, 1000));
      return mockData;
    } catch (error) {
      console.error(`Error scraping ${clubId}:`, error.message);
      return null;
    }
  }

  async scrapeAllClubs() {
    const results = [];
    
    for (const club of CLUBS) {
      const data = await this.scrapeClubFinancials(club.id);
      if (data) {
        results.push(data);
      }
    }

    const outputPath = path.join(__dirname, '../data/ffp_data_2023.json');
    await fs.writeFile(outputPath, JSON.stringify(results, null, 2));
    console.log(`Data saved to ${outputPath}`);
    
    return results;
  }
}

if (require.main === module) {
  const scraper = new FFPDataScraper();
  scraper.scrapeAllClubs()
    .then(data => console.log(`Scraped data for ${data.length} clubs`))
    .catch(console.error);
}

module.exports = FFPDataScraper;