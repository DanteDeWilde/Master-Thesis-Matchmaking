# League of Legends Match Data Crawler  

## Note  
This project is designed for research and educational purposes. When using this tool, ensure compliance with Riot Games' [API Terms of Service](https://developer.riotgames.com/policies.html).  

---

## Introduction  
The **League of Legends Match Data Crawler** is a Python-based tool for automated collection of in-game match data.

## Project Overview
- **Scrape match data through Riot Games’ public APIs.**
- **Extract player, team and match statistics.**
- **Store structured data in three separate csv files for analysis.**

### Key Features  
- **Region-specific crawlers** (NA, EU, Asia, SEA)  
- **Modular design** to eliminate code duplication  
- **Progress tracking** of competitive tiers  and divisions 
- **Structured output** in CSV files for easy analysis  

---

## Development Setup  

### Prerequisites  
- Python 3.8+  
- Libraries: `requests`, `json`, `os`  

### Running the Crawlers  
1. **Configure API Keys**  
   Replace the placeholder API key in `crawler_base.py` with your Riot Games personal key (non-expiring).  

2. **Execute a Region-Specific Crawler**  
 
3. **Output:**
   Csv files saved in data_[region]/[filename].
