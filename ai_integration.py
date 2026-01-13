import requests
import json
import logging
from typing import Dict, List, Any, Optional
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AILayerIntegration:
    """
    Integration layer to receive data from your college's AI system
    and store it in the database for API consumption
    """
    
    def __init__(self, api_server_url: str = "http://localhost:8000"):
        self.api_server_url = api_server_url
    
    def receive_ai_data(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data received from AI layer and create/update API endpoint
        
        Expected AI response format:
        {
            "api_name": "cryptocurrency_prices",
            "description": "Real-time cryptocurrency prices and market data",
            "data": [
                {"symbol": "BTC", "price": 45000, "change_24h": 2.5},
                {"symbol": "ETH", "price": 3200, "change_24h": -1.2}
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "price": {"type": "number"},
                    "change_24h": {"type": "number"}
                }
            },
            "data_source": "AI Analysis of Multiple Sources",
            "update_frequency": "real-time"
        }
        """
        try:
            # Validate required fields
            required_fields = ['api_name', 'description', 'data', 'schema']
            for field in required_fields:
                if field not in ai_response:
                    raise ValueError(f"Missing required field: {field}")
            
            # Extract data from AI response
            api_name = ai_response['api_name']
            description = ai_response['description']
            data = ai_response['data']
            schema = ai_response['schema']
            data_source = ai_response.get('data_source', 'AI Layer')
            update_frequency = ai_response.get('update_frequency', 'daily')
            
            # Validate data is not empty
            if not data or not isinstance(data, list):
                raise ValueError("Data must be a non-empty list")
            
            # Create API request payload
            api_request = {
                "name": api_name,
                "description": description,
                "data": data,
                "schema": schema,
                "data_source": data_source,
                "update_frequency": update_frequency
            }
            
            # Send to API server
            response = requests.post(
                f"{self.api_server_url}/apis",
                json=api_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully processed AI data for API: {api_name}")
                return {
                    "status": "success",
                    "message": f"API '{api_name}' created/updated successfully",
                    "api_endpoint": result.get("endpoint"),
                    "records_processed": len(data)
                }
            else:
                logger.error(f"API server error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"API server error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error processing AI data: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def batch_receive_ai_data(self, ai_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple AI responses in batch"""
        results = []
        successful = 0
        failed = 0
        
        for ai_response in ai_responses:
            result = self.receive_ai_data(ai_response)
            results.append(result)
            
            if result["status"] == "success":
                successful += 1
            else:
                failed += 1
        
        return {
            "status": "completed",
            "total_processed": len(ai_responses),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def get_api_status(self, api_name: str) -> Dict[str, Any]:
        """Get status of a specific API"""
        try:
            response = requests.get(f"{self.api_server_url}/apis/{api_name}/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"API not found or server error: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def list_all_apis(self) -> Dict[str, Any]:
        """List all available APIs"""
        try:
            response = requests.get(f"{self.api_server_url}/apis")
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"Server error: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Example usage functions for testing
def simulate_ai_response_crypto():
    """Simulate AI response for cryptocurrency data"""
    return {
        "api_name": "cryptocurrency_prices",
        "description": "Real-time cryptocurrency prices and market data from AI analysis",
        "data": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price": 45000.50,
                "change_24h": 2.5,
                "market_cap": 850000000000,
                "volume_24h": 25000000000
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price": 3200.75,
                "change_24h": -1.2,
                "market_cap": 380000000000,
                "volume_24h": 15000000000
            },
            {
                "symbol": "BNB",
                "name": "Binance Coin",
                "price": 320.25,
                "change_24h": 0.8,
                "market_cap": 50000000000,
                "volume_24h": 2000000000
            }
        ],
        "schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Cryptocurrency symbol"},
                "name": {"type": "string", "description": "Full name"},
                "price": {"type": "number", "description": "Current price in USD"},
                "change_24h": {"type": "number", "description": "24h price change percentage"},
                "market_cap": {"type": "number", "description": "Market capitalization"},
                "volume_24h": {"type": "number", "description": "24h trading volume"}
            }
        },
        "data_source": "AI Analysis of CoinGecko, CoinMarketCap, Binance",
        "update_frequency": "real-time"
    }

def simulate_ai_response_news():
    """Simulate AI response for news data"""
    return {
        "api_name": "tech_news",
        "description": "Latest technology news aggregated and analyzed by AI",
        "data": [
            {
                "id": 1,
                "title": "AI Breakthrough in Natural Language Processing",
                "summary": "Researchers achieve new milestone in AI language understanding",
                "category": "Technology",
                "published_at": "2025-01-13T10:30:00Z",
                "source": "TechCrunch",
                "sentiment": "positive",
                "relevance_score": 0.95
            },
            {
                "id": 2,
                "title": "Quantum Computing Advances in 2025",
                "summary": "Major tech companies announce quantum computing breakthroughs",
                "category": "Technology",
                "published_at": "2025-01-13T09:15:00Z",
                "source": "Wired",
                "sentiment": "positive",
                "relevance_score": 0.88
            }
        ],
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Unique article ID"},
                "title": {"type": "string", "description": "Article title"},
                "summary": {"type": "string", "description": "AI-generated summary"},
                "category": {"type": "string", "description": "News category"},
                "published_at": {"type": "string", "description": "Publication timestamp"},
                "source": {"type": "string", "description": "News source"},
                "sentiment": {"type": "string", "description": "AI-analyzed sentiment"},
                "relevance_score": {"type": "number", "description": "AI relevance score"}
            }
        },
        "data_source": "AI Analysis of Multiple News Sources",
        "update_frequency": "hourly"
    }

# Global integration instance
ai_integration = AILayerIntegration()

if __name__ == "__main__":
    # Test the integration with sample data
    print("Testing AI Integration...")
    
    # Test crypto data
    crypto_result = ai_integration.receive_ai_data(simulate_ai_response_crypto())
    print("Crypto API Result:", crypto_result)
    
    # Test news data
    news_result = ai_integration.receive_ai_data(simulate_ai_response_news())
    print("News API Result:", news_result)
    
    # List all APIs
    apis_result = ai_integration.list_all_apis()
    print("All APIs:", apis_result)