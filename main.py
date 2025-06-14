import os
import json
import asyncio
import pandas as pd
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from pydantic import BaseModel
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from io import StringIO
from dotenv import load_dotenv
import os

load_dotenv() 

# Initialize FastAPI app
app = FastAPI(
    title="Fegmo Insight Agent",
    description="AI-powered e-commerce insights agent for product performance analysis",
    version="1.0.0"
)

# Configuration for LLM
config_list = [{
    "model": os.getenv("model"),
    "api_key": os.getenv("api_key"),
    "api_type": os.getenv("api_type"),
    "base_url": os.getenv("base_url"),
    "api_version": os.getenv("api_version"),
}]

llm_config = {
    "timeout": 120,
    "temperature": 0.0,
    "top_p": 1,
    "config_list": config_list,
}

# Response model
class InsightResponse(BaseModel):
    insights: List[Dict[str, Any]]
    summary: str
    total_insights: int

# Mock data generator
def generate_mock_data() -> pd.DataFrame:
    """Generate mock product data for testing"""
    products = [
        {"product_id": "SKU001", "product_name": "Blue Light Blocking Glasses", "category": "Accessories", 
         "sales_last_30_days": 160, "sales_last_7_days": 50, "page_views": 1100, "conversion_rate": 4.6},
        
        {"product_id": "SKU002", "product_name": "Magnetic Phone Mount", "category": "Electronics", 
         "sales_last_30_days": 190, "sales_last_7_days": 60, "page_views": 1250, "conversion_rate": 5.2},
        
        {"product_id": "SKU003", "product_name": "Charcoal Face Mask", "category": "Skincare", 
         "sales_last_30_days": 130, "sales_last_7_days": 35, "page_views": 870, "conversion_rate": 4.8},
        
        {"product_id": "SKU004", "product_name": "Herbal Sleep Gummies", "category": "Supplements", 
         "sales_last_30_days": 140, "sales_last_7_days": 45, "page_views": 920, "conversion_rate": 6.3},
        
        {"product_id": "SKU005", "product_name": "Wireless Charging Station", "category": "Electronics", 
         "sales_last_30_days": 250, "sales_last_7_days": 75, "page_views": 1350, "conversion_rate": 5.9},
        
        {"product_id": "SKU006", "product_name": "Minimalist Leather Wallet", "category": "Fashion", 
         "sales_last_30_days": 100, "sales_last_7_days": 30, "page_views": 800, "conversion_rate": 3.9},
        
        {"product_id": "SKU007", "product_name": "Acupressure Mat", "category": "Fitness", 
         "sales_last_30_days": 120, "sales_last_7_days": 40, "page_views": 890, "conversion_rate": 4.5},
        
        {"product_id": "SKU008", "product_name": "Coffee Frother Stick", "category": "Home & Kitchen", 
         "sales_last_30_days": 105, "sales_last_7_days": 28, "page_views": 700, "conversion_rate": 4.2},
        
        {"product_id": "SKU009", "product_name": "Electric Scalp Massager", "category": "Personal Care", 
         "sales_last_30_days": 150, "sales_last_7_days": 55, "page_views": 990, "conversion_rate": 5.7},
        
        {"product_id": "SKU010", "product_name": "Scented Soy Candles Set", "category": "Home & Garden", 
         "sales_last_30_days": 130, "sales_last_7_days": 38, "page_views": 880, "conversion_rate": 4.4},
        
        {"product_id": "SKU011", "product_name": "Digital Meat Thermometer", "category": "Kitchen Tools", 
         "sales_last_30_days": 90, "sales_last_7_days": 25, "page_views": 600, "conversion_rate": 3.8},
        
        {"product_id": "SKU012", "product_name": "Luxury Bamboo Sheets", "category": "Home & Living", 
         "sales_last_30_days": 240, "sales_last_7_days": 85, "page_views": 1200, "conversion_rate": 5.5},
        
        {"product_id": "SKU013", "product_name": "Reversible Yoga Pants", "category": "Fitness Apparel", 
         "sales_last_30_days": 150, "sales_last_7_days": 50, "page_views": 980, "conversion_rate": 4.9},
        
        {"product_id": "SKU014", "product_name": "Wireless Noise Cancelling Earbuds", "category": "Electronics", 
         "sales_last_30_days": 280, "sales_last_7_days": 95, "page_views": 1450, "conversion_rate": 6.0},
        
        {"product_id": "SKU015", "product_name": "Cold Brew Coffee Maker", "category": "Kitchen", 
         "sales_last_30_days": 160, "sales_last_7_days": 50, "page_views": 910, "conversion_rate": 4.6},
        
    ]
    
    return pd.DataFrame(products)

# Analysis functions
def analyze_product_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze product performance and generate insights"""
    insights = []
    
    # Calculate additional metrics
    df['weekly_conversion_rate'] = (df['sales_last_7_days'] / df['page_views'] * 7) * 100
    df['sales_momentum'] = df['sales_last_7_days'] / (df['sales_last_30_days'] / 30 * 7)
    
    # Identify top performers
    top_performers = df.nlargest(3, 'sales_last_30_days')
    for _, product in top_performers.iterrows():
        insights.append({
            "product_id": product['product_id'],
            "product_name": product['product_name'],
            "insight": f"{product['product_name']} is a top performer with {product['sales_last_30_days']} sales in the last 30 days",
            "type": "Top Performer",
            "priority": "Medium",
            "metrics": {
                "sales_30d": int(product['sales_last_30_days']),
                "sales_7d": int(product['sales_last_7_days']),
                "conversion_rate": round(product['conversion_rate'], 2)
            }
        })
    
    # Identify conversion concerns (high traffic, low conversion)
    conversion_concerns = df[(df['page_views'] > df['page_views'].median()) & 
                          (df['conversion_rate'] < df['conversion_rate'].median())]
    
    for _, product in conversion_concerns.iterrows():
        insights.append({
            "product_id": product['product_id'],
            "product_name": product['product_name'],
            "insight": f"{product['product_name']} has high traffic ({int(product['page_views'])} views) but low conversion ({product['conversion_rate']}%)",
            "type": "Conversion Concern",
            "priority": "High",
            "action_prompt": "Consider improving product description, images, or pricing strategy",
            "metrics": {
                "page_views": int(product['page_views']),
                "conversion_rate": round(product['conversion_rate'], 2)
            }
        })
    
    # Identify declining products
    declining_products = df[df['sales_momentum'] < 0.7]
    for _, product in declining_products.iterrows():
        insights.append({
            "product_id": product['product_id'],
            "product_name": product['product_name'],
            "insight": f"{product['product_name']} shows declining sales momentum with recent weekly performance below average",
            "type": "Declining Performance",
            "priority": "Medium",
            "action_prompt": "Investigate reasons for decline and consider promotional activities",
            "metrics": {
                "sales_momentum": round(product['sales_momentum'], 2),
                "sales_7d": int(product['sales_last_7_days'])
            }
        })
    
    # Identify low engagement products
    low_engagement = df[df['page_views'] < df['page_views'].quantile(0.3)]
    for _, product in low_engagement.iterrows():
        insights.append({
            "product_id": product['product_id'],
            "product_name": product['product_name'],
            "insight": f"{product['product_name']} has low engagement with only {int(product['page_views'])} page views",
            "type": "Low Engagement",
            "priority": "Low",
            "action_prompt": "Improve SEO, social media presence, or consider advertising campaigns",
            "metrics": {
                "page_views": int(product['page_views']),
                "sales_30d": int(product['sales_last_30_days'])
            }
        })
    
    return {
        "insights": insights,
        "total_products": len(df),
        "avg_conversion_rate": round(df['conversion_rate'].mean(), 2),
        "total_sales_30d": int(df['sales_last_30_days'].sum())
    }

def create_insight_agents():
    """Create AutoGen agents for insight generation"""
    
    # Terminate condition
    def is_termination_msg(content):
        return content.get("content", "").strip().endswith("INSIGHT_ANALYSIS_COMPLETE")
    
    # Data Analyst Agent
    data_analyst_prompt = """
    You are a Data Analyst specializing in e-commerce product performance analysis.
    Your role is to:
    1. Analyze product performance data thoroughly
    2. Identify patterns and trends in sales, conversion rates, and engagement
    3. Calculate key metrics and performance indicators
    4. Provide detailed analysis to support insight generation
    
    Focus on finding actionable patterns that can help merchants improve their business performance.
    """
    
    # Insight Generator Agent
    insight_generator_prompt = """
    You are an Insight Generator that creates human-readable, actionable insights for e-commerce merchants.
    Your role is to:
    1. Transform data analysis into clear, actionable insights
    2. Categorize insights appropriately (Top Performer, Conversion Concern, Low Engagement, etc.)
    3. Assign priority levels (High, Medium, Low) based on business impact
    4. Provide specific action prompts for each insight
    5. Ensure insights are concise but comprehensive
    
    Format your final response as structured JSON with all insights.
    End your response with "INSIGHT_ANALYSIS_COMPLETE" when finished.
    """
    
    # User Proxy Agent
    user_proxy_prompt = """
    You are coordinating the insight generation process. 
    Work with the Data Analyst and Insight Generator to produce comprehensive product insights.
    """
    
    # Create agents
    user_proxy = UserProxyAgent(
        name="Coordinator",
        system_message=user_proxy_prompt,
        code_execution_config={"use_docker": False},
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
    )
    
    data_analyst = AssistantAgent(
        name="Data_Analyst",
        llm_config=llm_config,
        system_message=data_analyst_prompt,
        is_termination_msg=is_termination_msg,
    )
    
    insight_generator = AssistantAgent(
        name="Insight_Generator",
        llm_config=llm_config,
        system_message=insight_generator_prompt,
        is_termination_msg=is_termination_msg,
    )
    
    return user_proxy, data_analyst, insight_generator

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Fegmo Insight Agent API is running"}

@app.post("/generate-insights", response_model=InsightResponse)
async def generate_insights(
    use_mock_data: bool = Form(True),
    file: UploadFile = File(None)
):
    """Generate insights from uploaded CSV file or mock data"""
    try:
        # Step 1: Load data from file or mock
        if use_mock_data or file is None:
            df = generate_mock_data()
        else:
            contents = await file.read()
            df = pd.read_csv(StringIO(contents.decode("utf-8")))
        
        # Perform initial analysis
        analysis_results = analyze_product_performance(df)
        
        # Create AutoGen agents
        user_proxy, data_analyst, insight_generator = create_insight_agents()
        
        # Create group chat
        groupchat = GroupChat(
            agents=[user_proxy, data_analyst, insight_generator],
            messages=[],
            max_round=5,
        )
        
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config
        )
        
        # Prepare prompt for agents
        prompt = f"""
        Please analyze the following product performance data and generate actionable insights:
        
        Product Data Summary:
        - Total Products: {analysis_results['total_products']}
        - Average Conversion Rate: {analysis_results['avg_conversion_rate']}%
        - Total Sales (30 days): {analysis_results['total_sales_30d']}
        
        Detailed Product Data:
        {df.to_string(index=False)}
        
        Pre-generated Insights:
        {json.dumps(analysis_results['insights'], indent=2)}
        
        Please enhance these insights with more sophisticated analysis and ensure they are:
        1. Human-readable and actionable
        2. Properly categorized and prioritized
        3. Include specific action prompts
        4. Formatted as structured JSON
        
        Data Analyst: Start by analyzing the data patterns and trends.
        Insight Generator: Transform the analysis into polished insights and end with "INSIGHT_ANALYSIS_COMPLETE".
        """
        
        # Run the agent conversation
        chat_result = await asyncio.to_thread(
            user_proxy.initiate_chat,
            manager,
            message=prompt,
            clear_history=True
        )
        
        # Extract insights from the conversation
        final_insights = analysis_results['insights']  # Fallback to initial analysis
        
        # Try to extract enhanced insights from the last message
        if groupchat.messages:
            last_message = groupchat.messages[-1].get("content", "")
            try:
                # Look for JSON in the message
                import re
                json_match = re.search(r'\[.*\]', last_message, re.DOTALL)
                if json_match:
                    enhanced_insights = json.loads(json_match.group())
                    if isinstance(enhanced_insights, list) and len(enhanced_insights) > 0:
                        final_insights = enhanced_insights
            except:
                pass  # Use fallback insights
        
        # Generate summary
        summary = f"Analysis of {len(df)} products revealed {len(final_insights)} key insights. "
        summary += f"Average conversion rate is {analysis_results['avg_conversion_rate']}% with total 30-day sales of {analysis_results['total_sales_30d']} units."
        
        return InsightResponse(
            insights=final_insights,
            summary=summary,
            total_insights=len(final_insights)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Fegmo Insight Agent API - AI-Powered E-commerce Analytics",
        "version": "1.0.0",
        "endpoints": {
            "generate_insights": "/generate-insights",
            "description": "Generate actionable insights from product performance data"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)