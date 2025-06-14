# Insight Agent with AutoGen

A powerful AI-driven insight generation system that analyzes e-commerce product performance data and provides actionable business insights using AutoGen multi-agent framework.

## 🚀 Features

- **Multi-Agent Analysis**: Uses AutoGen framework with specialized agents (Data Analyst, Insight Generator)
- **Smart Categorization**: Automatically categorizes insights (Top Performer, Conversion Concern, Low Engagement, etc.)
- **Priority-Based Insights**: Assigns priority levels (High, Medium, Low) based on business impact
- **Actionable Recommendations**: Provides specific action prompts for each insight
- **Flexible Data Input**: Supports both mock data and custom CSV uploads
- **RESTful API**: FastAPI-based endpoints for easy integration

## 📊 Insight Types Generated

1. **Top Performer** - Products with highest sales performance
2. **Conversion Concern** - High traffic but low conversion products
3. **Declining Performance** - Products showing negative sales momentum
4. **Low Engagement** - Products with minimal page views or interaction

## 🤖 AutoGen Agent Architecture

The system uses three specialized agents:

### 1. Coordinator (UserProxyAgent)
- Orchestrates the insight generation process
- Manages agent communication

### 2. Data Analyst (AssistantAgent)
- Analyzes product performance data
- Identifies patterns and trends
- Calculates key metrics

### 3. Insight Generator (AssistantAgent)
- Transforms analysis into human-readable insights
- Categorizes and prioritizes findings
- Generates actionable recommendations


## 🛠️ Setup Instructions

Choose one of the following setup methods:

### Option 1: Docker Setup (Recommended)

#### Prerequisites
- Docker and Docker Compose installed on your system

#### Steps
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd insight-agent
   ```

2. **Create environment file**
   Create a `.env` file in the project root with your credentials:
   ```bash
   model=gpt-4o
   api_key=your_azure_api_key_here
   api_type=azure
   base_url=https://your-resource-name.openai.azure.com/
   api_version=2023-07-01-preview
   ```

3. **Build and run with Docker**
   ```bash
   # Build the Docker image
   docker build -t insight-agent .
   
   # Run the container
   docker run -p 8000:8000 --name insight-agent-container insight-agent 
   ```

The API will be available at `http://localhost:8000`

### Option 2: Virtual Environment Setup

#### Prerequisites
- Python 3.12 installed on your system

#### Steps
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd insight-agent
   ```

2. **Create virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   Create a `.env` file in the project root with your credentials:
   ```bash
   model=gpt-4o
   api_key=your_azure_api_key_here
   api_type=azure
   base_url=https://your-resource-name.openai.azure.com/
   api_version=2023-07-01-preview
   ```

5. **Run the application**
   ```bash
   # Start the FastAPI server
   python main.py
   
   # Or use uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API will be available at `http://localhost:8000`

## 🔐 Environment Variables

**Important:** You need to provide your own Azure OpenAI credentials. Create a `.env` file with the following variables:

```bash
# Azure OpenAI Configuration
model=gpt-4o                                          # Your model deployment name
api_key=your_azure_openai_api_key                    # Your Azure OpenAI API key
api_type=azure                                        # Keep as 'azure'
base_url=https://your-resource-name.openai.azure.com/ # Your Azure OpenAI endpoint
api_version=2023-07-01-preview                        # API version (or latest available)
```

## 📡 API Endpoint

### ➤ `POST /generate-insights`

Analyzes product CSV data and generates categorized insights.

---

### 🔧 Request

- **Method:** `POST`  
- **URL:** `http://localhost:8000/generate-insights`  
- **Form fields:**
  - `file`: CSV file (optional if `use_mock_data=true`)
  - `use_mock_data`: `true` or `false`

---

### 🧪 Example (using cURL)

```bash
curl -X POST "http://localhost:8000/generate-insights" \
     -H "accept: application/json" \
     -F "use_mock_data=false" \
     -F "file=@/path/to/your/product_data.csv"
```
**Using default mock data**

```bash
# Test with mock data
curl -X POST "http://localhost:8000/generate-insights" \
     -H "Content-Type: application/json" \
     -d '{"use_mock_data": true}'
```
---

## 📬 Sample API Response

```json
{
  "insights": [
    {
      "product_id": "SKU014",
      "product_name": "Wireless Noise Cancelling Earbuds",
      "insight": "This product is a top performer with 280 sales in the last 30 days and a high conversion rate of 6.0%.",
      "type": "Top Performer",
      "priority": "High",
      "action_prompt": "Consider expanding marketing efforts to capitalize on strong performance and explore bundling with related electronics.",
      "metrics": {
        "sales_30d": 280,
        "sales_7d": 95,
        "conversion_rate": 6.0
      }
    },
    {
      "product_id": "SKU001",
      "product_name": "Blue Light Blocking Glasses",
      "insight": "High traffic (1100 views) but low conversion (4.6%) suggests potential issues with product appeal.",
      "type": "Conversion Concern",
      "priority": "High",
      "action_prompt": "Revise product descriptions, enhance images, and consider competitive pricing strategies.",
      "metrics": {
        "page_views": 1100,
        "conversion_rate": 4.6
      }
    },
    {
      "product_id": "SKU006",
      "product_name": "Minimalist Leather Wallet",
      "insight": "Low engagement with only 800 page views indicates potential market saturation.",
      "type": "Low Engagement",
      "priority": "Low",
      "action_prompt": "Explore new marketing channels and consider product differentiation strategies.",
      "metrics": {
        "page_views": 800,
        "sales_30d": 100
      }
    }
  ],
  "summary": "Analysis of 20 products revealed 6 key insights. Average conversion rate is 4.99% with total 30-day sales of 3125 units.",
  "total_insights": 6
}
