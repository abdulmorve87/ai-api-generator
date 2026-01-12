
def load_mock_response():
    """Load mock API response data"""
    return {
        "endpoint": "https://api.yourdomain.com/v1/indian-ipos",
        "method": "GET",
        "authentication": "API Key required in header: X-API-Key",
        "rate_limit": "100 requests per hour",
        "response_structure": {
            "status": "success",
            "data": [
                {
                    "company_name": "Tata Technologies Ltd",
                    "listing_date": "2024-11-30",
                    "issue_price": 500,
                    "current_price": 1150,
                    "grey_market_premium": 230,
                    "grey_market_history": [
                        {"date": "2024-11-15", "premium": 180},
                        {"date": "2024-11-20", "premium": 210},
                        {"date": "2024-11-25", "premium": 230}
                    ],
                    "subscription_status": "Oversubscribed 69.43x",
                    "lot_size": 25
                },
                {
                    "company_name": "Ideaforge Technology Ltd",
                    "listing_date": "2024-12-10",
                    "issue_price": 672,
                    "current_price": 890,
                    "grey_market_premium": 125,
                    "grey_market_history": [
                        {"date": "2024-12-01", "premium": 90},
                        {"date": "2024-12-05", "premium": 110},
                        {"date": "2024-12-08", "premium": 125}
                    ],
                    "subscription_status": "Oversubscribed 45.67x",
                    "lot_size": 20
                }
            ],
            "timestamp": "2025-01-12T10:30:00Z",
            "total_results": 2
        },
        "example_curl": """curl -X GET "https://api.yourdomain.com/v1/indian-ipos" \\
  -H "X-API-Key: your_api_key_here" \\
  -H "Content-Type: application/json" """,
        "python_example": """import requests

url = "https://api.yourdomain.com/v1/indian-ipos"
headers = {
    "X-API-Key": "your_api_key_here",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)""",
        "query_parameters": {
            "limit": "Number of results to return (default: 10)",
            "offset": "Pagination offset (default: 0)",
            "sort_by": "Sort field (options: listing_date, grey_market_premium)",
            "order": "Sort order (options: asc, desc)"
        }
    }