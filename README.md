# P15: Hydergraph & Cultural Recommender System

## Mapping Culture Through Food, Heritage & AI

This project combines a sophisticated network analysis pipeline with an interactive web application. It analyzes co-occurrence networks of food, places, and monuments in Hyderabad and uses this data to power a smart recommendation system that suggests cultural attractions based on user experiences.

-----

## 📋 Project Architecture

The project consists of two main components:

1.  **The Data Pipeline (Hydergraph)**:

      * Collects entities and scrapes web content.
      * Builds **three types of co-occurrence networks**: Sentence-level, Paragraph-level, and Page-level.
      * Performs deep network analysis (centrality, density, clustering).

2.  **The Recommender System**:

      * An interactive Flask web interface.
      * Uses **7 advanced algorithms** (e.g., PageRank, Random Walk) to generate suggestions.
      * Integrates **Google's Gemini API** for natural language responses.

-----

## 🚀 Part 1: Data Pipeline Setup

To generate the network data required for the recommender, run the pipeline first.

### 1\. Installation

```bash
pip install -r requirements.txt
```

### 2\. Run the Pipeline

You can run the complete pipeline using the main runner:

```bash
python main_runner.py
```

Select **Option 1** to run the full process, which includes Entity Collection, Web Scraping, Network Building, and Analysis.

### 3\. Pipeline Outputs

After running, the system generates:

  * `sentence_network.pkl`/`.graphml`: Strongest direct associations.
  * `paragraph_network.pkl`/`.graphml`: Moderate associations.
  * `page_network.pkl`/`.graphml`: Broadest associations.

-----

## 🤖 Part 2: Recommender System Setup

Once the networks are built (specifically `sentence_network.graphml`), you can launch the web application.

### 1\. API Configuration (Optional)

To enable AI-powered natural language recommendations:

1.  Get a free API key from Google MakerSuite.
2.  Copy `.env.example` to `.env` and add: `GEMINI_API_KEY=your_key_here`.

### 2\. Launch the App

**Option A: Startup Script (Windows)**
Double-click `start_recommender.bat`.

**Option B: Manual Launch**

```bash
python -m spacy download en_core_web_sm
python recommender_app.py
```

Then open your browser to `http://localhost:5000`.

### 3\. Usage

1.  **Enter Experience**: Type a sentence (e.g., "Had haleem at Pista House, want to visit nearby heritage sites").
2.  **Select Algorithm**: Choose from 7 strategies (see guide below).
3.  **Get Suggestions**: View AI-curated results on the dashboard.

-----

## 🧠 Algorithm Guide

The recommender system offers different logic paths based on your needs:

| Algorithm | Best For | Description |
|-----------|----------|-------------|
| **Simple Co-occurrence** | Popularity | Most frequently associated places/items. |
| **PageRank** | Importance | Uses network centrality to find "must-visit" nodes. |
| **Inverse Frequency** | Discovery | Balances popularity to find unique "hidden gems". |
| **Random Walk** | Exploration | Generates serendipitous exploration paths. |
| **Guided Walk** | Planning | Creates logical paths between two specific locations. |
| **Exploratory Walk** | Adventure | Random exploration with "teleportation" mechanics. |
| **Guided Exploratory** | Smart Adventure | A mix of targeted planning and serendipity. |

-----

## 🔧 Detailed Customization

### External APIs

  * **Reddit (Scraping):** To scrape Reddit, add your client ID and secret in `web_scraper.py`.
  * **Gemini (NLP):** To generate conversational recommendations, add `GEMINI_API_KEY` to your `.env` file.

### Adding Entities

Edit `entity_collection.py` to add new food items, restaurants, or monuments to the search list.

### Adding Sources

Edit `web_scraper.py` to include new blog URLs or websites.

-----

## ⚠️ Troubleshooting

**"Graph file not found"**

  * Ensure `sentence_network.graphml` exists. If not, run the Data Pipeline (Option 1 in `main_runner.py`) to generate it.

**spaCy model error**

  * Run: `python -m spacy download en_core_web_sm`.

**Reddit scraping fails**

  * Verify your Reddit app credentials are set to "script" type and your account is in good standing.

**Port 5000 in use**

  * Edit `recommender_app.py` and change the port number in `app.run(port=5000)`.

-----

## 📄 License & Citation

This project is for educational purposes. Please acknowledge:

```
Hyderabad Cultural Network Project (2025)
P15: Hydergraph - Mapping Culture Through Food & Heritage
```
