#!/usr/bin/env python3
"""
Unified Calcs API MCP Server

Comprehensive FastMCP implementation supporting both HTTP and SSE transports.
Provides access to the Calcs API for retail analytics calculations and test management.
Includes all 30+ tools with intelligent response size management.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Dict

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables from .env file in the project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Configure logging to stderr (stdout is reserved for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("calcs-api")

# Token size and filtering utilities
SAFE_TOKEN_LIMIT = 40000  # Conservative limit to prevent context overflow

def estimate_tokens(data: Any) -> int:
    """Estimate token count for data structure."""
    json_str = json.dumps(data, ensure_ascii=False)
    # Rough estimation: ~4 characters per token
    return len(json_str) // 4

def filter_json_by_keywords(data: Any, keywords: List[str]) -> Dict[str, Any]:
    """Filter JSON data to include only fields matching keywords."""
    if not keywords:
        return data
    
    def extract_matching_fields(obj: Any, path: str = "") -> Dict[str, Any]:
        """Recursively extract fields that match keywords."""
        result = {}
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if this field matches any keyword
                matches_keyword = any(keyword.lower() in key.lower() or keyword.lower() in current_path.lower() 
                                    for keyword in keywords)
                
                if matches_keyword:
                    result[current_path] = value
                elif isinstance(value, (dict, list)):
                    # Recursively search nested structures
                    nested_result = extract_matching_fields(value, current_path)
                    result.update(nested_result)
                    
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                item_path = f"{path}[{i}]" if path else f"[{i}]"
                nested_result = extract_matching_fields(item, item_path)
                result.update(nested_result)
                
        return result
    
    if isinstance(data, list):
        filtered_results = []
        for item in data:
            filtered_item = extract_matching_fields(item)
            if filtered_item:  # Only include items with matching fields
                filtered_results.append(filtered_item)
        return {
            "filtered_results": filtered_results,
            "total_records": len(data),
            "filtered_fields": keywords,
            "original_type": "list"
        }
    else:
        filtered_result = extract_matching_fields(data)
        return {
            "filtered_results": filtered_result,
            "filtered_fields": keywords,
            "original_type": "object"
        }

def check_response_size_and_filter(data: Any, keywords: List[str] = None) -> Dict[str, Any]:
    """Check if response is too large and apply filtering if needed."""
    estimated_tokens = estimate_tokens(data)
    
    if estimated_tokens <= SAFE_TOKEN_LIMIT:
        return {"status": "success", "data": data}
    
    if keywords:
        # Apply filtering and return filtered results
        filtered_data = filter_json_by_keywords(data, keywords)
        return {"status": "success", "data": filtered_data, "was_filtered": True}
    else:
        # Return error with suggestion to use filtering
        return {
            "status": "error",
            "error": f"Response too large (estimated {estimated_tokens:,} tokens > {SAFE_TOKEN_LIMIT:,} limit)",
            "suggestion": "Use the '_filtered' version of this tool with keywords parameter",
            "estimated_tokens": estimated_tokens,
            "total_records": len(data) if isinstance(data, list) else 1
        }

def smart_truncate_response(data: Any, keywords: List[str] = None) -> Dict[str, Any]:
    """Smart response size management with keyword filtering."""
    token_count = estimate_tokens(data)
    
    if token_count <= SAFE_TOKEN_LIMIT:
        return {
            "data": data,
            "truncated": False,
            "token_estimate": token_count,
            "total_records": len(data) if isinstance(data, list) else 1
        }
    
    # If keywords provided, try filtering first
    if keywords:
        logger.info(f"Large response ({token_count} tokens), applying keyword filter: {keywords}")
        filtered_data = filter_json_by_keywords(data, keywords)
        filtered_token_count = estimate_tokens(filtered_data)
        
        if filtered_token_count <= SAFE_TOKEN_LIMIT:
            return {
                "data": filtered_data,
                "truncated": False,
                "filtered": True,
                "token_estimate": filtered_token_count,
                "original_token_estimate": token_count,
                "filter_keywords": keywords
            }
    
    # Fallback: truncate for lists
    if isinstance(data, list):
        truncated_data = []
        current_tokens = 0
        
        for item in data:
            item_tokens = estimate_tokens(item)
            if current_tokens + item_tokens > SAFE_TOKEN_LIMIT:
                break
            truncated_data.append(item)
            current_tokens += item_tokens
        
        logger.warning(f"Response truncated: {len(truncated_data)}/{len(data)} records, {current_tokens} tokens")
        
        return {
            "data": truncated_data,
            "truncated": True,
            "token_estimate": current_tokens,
            "original_token_estimate": token_count,
            "total_records": len(data),
            "returned_records": len(truncated_data)
        }
    
    # For non-list data, return a summary
    logger.warning(f"Large non-list response ({token_count} tokens) - returning summary")
    return {
        "data": {"summary": "Response too large, use keyword filtering", "type": str(type(data).__name__)},
        "truncated": True,
        "token_estimate": token_count,
        "message": "Use filter_keywords parameter to get specific fields"
    }


class CalcsApiClient:
    """Complete client for interacting with the Calcs API."""
    
    def __init__(self, base_url: str, token: str, default_client: str = ""):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.default_client = default_client
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
    
    async def health_check(self) -> dict[str, Any]:
        """Check API health."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Test Management Methods
    async def get_tests(self, client: str = "") -> dict[str, Any]:
        """Get all tests."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
        
        try:
            response = await self.client.get(f"{self.base_url}/v1/tests/", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data)
        except Exception as e:
            logger.error(f"Get tests failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_tests_filtered(self, client: str = "", keywords: List[str] = None) -> dict[str, Any]:
        """Get all tests with keyword filtering for large responses."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
        
        try:
            response = await self.client.get(f"{self.base_url}/v1/tests/", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data, keywords or [])
        except Exception as e:
            logger.error(f"Get tests filtered failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_test_status(self, test_id: int, client: str = "") -> dict[str, Any]:
        """Get test status."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/tests/{test_id}/status", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get test status failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_active_clients(self, client: str = "") -> dict[str, Any]:
        """Get all active clients."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/clients/", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get active clients failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_site_tests(self, client_site_id: str, client: str = "") -> dict[str, Any]:
        """Get all tests where a site has treatment or control role."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/sites/{client_site_id}/tests", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get site tests failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def describe_transactions(self, client: str = "") -> dict[str, Any]:
        """Get descriptive overview of the fact_transactions table."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/transactions/describe", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Describe transactions failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Results & Analytics Methods
    async def get_lift_explorer_results(self, lift_explorer_id: str, client: str = "") -> dict[str, Any]:
        """Get lift explorer results (JSON equivalent of .avro file)."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/lift-explorer/{lift_explorer_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data)
        except Exception as e:
            logger.error(f"Get lift explorer results failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_lift_explorer_results_filtered(self, lift_explorer_id: str, client: str = "", keywords: List[str] = None) -> dict[str, Any]:
        """Get lift explorer results with keyword filtering for large responses."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/lift-explorer/{lift_explorer_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data, keywords or [])
        except Exception as e:
            logger.error(f"Get lift explorer results filtered failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_site_pair_lift_manifest(self, test_id: int, client: str = "") -> dict[str, Any]:
        """Get site pair lift manifest (JSON equivalent of avro)."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/test/{test_id}/site-pair-lift-manifest", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get site pair lift manifest failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_prediction_table(self, test_id: int, client: str = "") -> dict[str, Any]:
        """Get prediction table (JSON equivalent of avro)."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/test/{test_id}/prediction-table", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get prediction table failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_customer_cross(self, test_id: int, client: str = "") -> dict[str, Any]:
        """Get customer cross (JSON equivalent of avro)."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/test/{test_id}/customer-cross", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get customer cross failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_test_results(self, test_id: int, filter_type: str, filter_value: str = None, client: str = "") -> dict[str, Any]:
        """Get test results with filtering."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            params = {}
            if filter_value is not None:
                params["filter_value"] = filter_value
            response = await self.client.get(f"{self.base_url}/v1/results/test/{test_id}/{filter_type}", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data)
        except Exception as e:
            logger.error(f"Get test results failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_test_results_filtered(self, test_id: int, filter_type: str, filter_value: str = None, client: str = "", keywords: List[str] = None) -> dict[str, Any]:
        """Get test results with filtering and keyword filtering for large responses."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            params = {}
            if filter_value is not None:
                params["filter_value"] = filter_value
            response = await self.client.get(f"{self.base_url}/v1/results/test/{test_id}/{filter_type}", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data, keywords or [])
        except Exception as e:
            logger.error(f"Get test results filtered failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def download_all_test_data(self, test_id: int, client: str = "") -> dict[str, Any]:
        """Download all chart data for test."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/test-download-all/{test_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data)
        except Exception as e:
            logger.error(f"Download all test data failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def download_all_test_data_filtered(self, test_id: int, client: str = "", keywords: List[str] = None) -> dict[str, Any]:
        """Download all chart data for test with keyword filtering for large responses."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/test-download-all/{test_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data, keywords or [])
        except Exception as e:
            logger.error(f"Download all test data filtered failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_lift_explorer_ids(self, client: str = "") -> dict[str, Any]:
        """Get list of valid lift explorer IDs for client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/lift_explorations/", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get lift explorer IDs failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_clients_jobs_summary(self, start_date: str, end_date: str, client: str = "") -> dict[str, Any]:
        """Get job information for all active clients."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            params = {"start_date": start_date, "end_date": end_date}
            response = await self.client.get(f"{self.base_url}/v1/clients/jobs-summary", headers=headers, params=params)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get clients jobs summary failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Job & System Monitoring Methods
    async def get_jobs_summary(self, start_date: str, end_date: str, client: str = "") -> dict[str, Any]:
        """Get count of running jobs and compute hours for date range."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            params = {"start_date": start_date, "end_date": end_date}
            response = await self.client.get(f"{self.base_url}/v1/jobs/summary", headers=headers, params=params)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get jobs summary failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_oldest_job_date(self, client: str = "") -> dict[str, Any]:
        """Get the date of the oldest job for client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/jobs/oldest-job-date", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get oldest job date failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_newest_job_date(self, client: str = "") -> dict[str, Any]:
        """Get the date of the newest job for client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/jobs/newest-job-date", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get newest job date failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Analysis Management Methods
    async def list_analyses(self, client: str = "") -> dict[str, Any]:
        """List all analyses for the current client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/rollout/analyses", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data)
        except Exception as e:
            logger.error(f"List analyses failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_analyses_filtered(self, client: str = "", keywords: List[str] = None) -> dict[str, Any]:
        """List all analyses with keyword filtering for large responses."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/rollout/analyses", headers=headers)
            response.raise_for_status()
            data = response.json()
            return check_response_size_and_filter(data, keywords or [])
        except Exception as e:
            logger.error(f"List analyses filtered failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_analysis(self, analysis_data: dict, client: str = "") -> dict[str, Any]:
        """Create a new analysis for the current client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.post(f"{self.base_url}/v1/rollout/analyses", json=analysis_data, headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Create analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_analysis(self, analysis_id: str, client: str = "") -> dict[str, Any]:
        """Get a specific analysis by ID for the current client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/rollout/analyses/{analysis_id}", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def update_analysis(self, analysis_id: str, analysis_data: dict, client: str = "") -> dict[str, Any]:
        """Update an existing analysis for the current client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.put(f"{self.base_url}/v1/rollout/analyses/{analysis_id}", json=analysis_data, headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Update analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def delete_analysis(self, analysis_id: str, client: str = "") -> dict[str, Any]:
        """Delete an analysis for the current client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.delete(f"{self.base_url}/v1/rollout/analyses/{analysis_id}", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": "Analysis deleted successfully"}
        except Exception as e:
            logger.error(f"Delete analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_analysis(self, analysis_id: str, force_refresh: bool = False, client: str = "") -> dict[str, Any]:
        """Run the rollout analysis for the specified analysis parameters."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            params = {"force_refresh": force_refresh}
            response = await self.client.post(f"{self.base_url}/v1/rollout/analyses/{analysis_id}/run", headers=headers, params=params)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Run analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def start_analysis(self, analysis_id: str, force_refresh: bool = False, client: str = "") -> dict[str, Any]:
        """Start analysis asynchronously and return immediately with progress tracking info."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            params = {"force_refresh": force_refresh}
            response = await self.client.post(f"{self.base_url}/v1/rollout/analyses/{analysis_id}/start", headers=headers, params=params)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Start analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_analysis_results(self, analysis_id: str, client: str = "") -> dict[str, Any]:
        """Get results of a completed analysis."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/rollout/analyses/{analysis_id}/results", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get analysis results failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


def get_api_client() -> CalcsApiClient:
    """Get configured API client."""
    token = os.getenv("CALCS_API_TOKEN")
    if not token:
        raise ValueError("CALCS_API_TOKEN environment variable is required")
    
    base_url = os.getenv("CALCS_API_BASE_URL", "https://staging-app.marketdial.dev/calcs")
    default_client = os.getenv("CALCS_DEFAULT_CLIENT")
    
    return CalcsApiClient(
        base_url=base_url,
        token=token,
        default_client=default_client
    )

# Initialize FastMCP server
mcp = FastMCP("calcs-api")
api_client = None

# Test Management Tools
@mcp.tool()
async def health_check() -> str:
    """Check the health of the Calcs API connection."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.health_check()
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_tests(client: str = None, filter_keywords: List[str] = None) -> str:
    """Get all tests from the Calcs API with optional filtering."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    if filter_keywords:
        response = await api_client.get_tests_filtered(client or "", filter_keywords)
    else:
        response = await api_client.get_tests(client or "")
    
    if response["status"] == "error":
        return json.dumps(response, indent=2)
    
    # Apply smart truncation for FastMCP when no filtering was applied
    if not filter_keywords:
        managed_response = smart_truncate_response(response["data"], None)
        return json.dumps({
            "status": "success",
            "response_info": managed_response,
            "data": managed_response["data"]
        }, indent=2)
    
    # If filtering was applied at API level, return the already filtered response
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_test_status(test_id: int, client: str = None) -> str:
    """Get the status of a specific test."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_test_status(test_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_active_clients(client: str = None) -> str:
    """Get list of all active clients."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_active_clients(client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_site_tests(client_site_id: str, client: str = None) -> str:
    """Get all tests where a site has treatment or control role."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_site_tests(client_site_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def describe_transactions(client: str = None) -> str:
    """Get descriptive overview of the fact_transactions table."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.describe_transactions(client or "")
    return json.dumps(result, indent=2)

# Results & Analytics Tools
@mcp.tool()
async def get_test_results(test_id: int, filter_type: str, filter_value: str = None, client: str = None, filter_keywords: List[str] = None) -> str:
    """Get test results with advanced filtering (OVERALL, CUSTOMER_COHORT, CUSTOMER_SEGMENT, SITE_COHORT, SITE_PAIR, FINISHED_COHORT, SITE_TAG)."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    if filter_keywords:
        response = await api_client.get_test_results_filtered(test_id, filter_type, filter_value, client or "", filter_keywords)
    else:
        response = await api_client.get_test_results(test_id, filter_type, filter_value, client or "")
    
    if response["status"] == "error":
        return json.dumps(response, indent=2)
    
    # Apply smart truncation for FastMCP when no filtering was applied
    if not filter_keywords:
        managed_response = smart_truncate_response(response["data"], None)
        return json.dumps({
            "status": "success",
            "response_info": managed_response,
            "data": managed_response["data"]
        }, indent=2)
    
    # If filtering was applied at API level, return the already filtered response
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_lift_explorer_results(lift_explorer_id: str, client: str = None, filter_keywords: List[str] = None) -> str:
    """Get lift explorer results (JSON equivalent of .avro file contents)."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    if filter_keywords:
        response = await api_client.get_lift_explorer_results_filtered(lift_explorer_id, client or "", filter_keywords)
    else:
        response = await api_client.get_lift_explorer_results(lift_explorer_id, client or "")
    
    if response["status"] == "error":
        return json.dumps(response, indent=2)
    
    # Apply smart truncation for FastMCP when no filtering was applied
    if not filter_keywords:
        managed_response = smart_truncate_response(response["data"], None)
        return json.dumps({
            "status": "success",
            "response_info": managed_response,
            "data": managed_response["data"]
        }, indent=2)
    
    # If filtering was applied at API level, return the already filtered response
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_lift_explorer_ids(client: str = None) -> str:
    """Get list of valid lift explorer IDs for client."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_lift_explorer_ids(client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_site_pair_lift_manifest(test_id: int, client: str = None) -> str:
    """Get site pair lift manifest data."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_site_pair_lift_manifest(test_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_prediction_table(test_id: int, client: str = None) -> str:
    """Get prediction table data."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_prediction_table(test_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_customer_cross(test_id: int, client: str = None) -> str:
    """Get customer cross data."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_customer_cross(test_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def download_all_test_data(test_id: int, client: str = None, filter_keywords: List[str] = None) -> str:
    """Download comprehensive chart data for a test."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    if filter_keywords:
        response = await api_client.download_all_test_data_filtered(test_id, client or "", filter_keywords)
    else:
        response = await api_client.download_all_test_data(test_id, client or "")
    
    if response["status"] == "error":
        return json.dumps(response, indent=2)
    
    # Apply smart truncation for FastMCP when no filtering was applied
    if not filter_keywords:
        managed_response = smart_truncate_response(response["data"], None)
        return json.dumps({
            "status": "success",
            "response_info": managed_response,
            "data": managed_response["data"]
        }, indent=2)
    
    # If filtering was applied at API level, return the already filtered response
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_clients_jobs_summary(start_date: str, end_date: str, client: str = None) -> str:
    """Get job information for all active clients."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_clients_jobs_summary(start_date, end_date, client or "")
    return json.dumps(result, indent=2)

# Analysis Management Tools
@mcp.tool()
async def list_analyses(client: str = None, filter_keywords: List[str] = None) -> str:
    """List all analyses for the current client."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    if filter_keywords:
        response = await api_client.list_analyses_filtered(client or "", filter_keywords)
    else:
        response = await api_client.list_analyses(client or "")
    
    if response["status"] == "error":
        return json.dumps(response, indent=2)
    
    # Apply smart truncation for FastMCP when no filtering was applied
    if not filter_keywords:
        managed_response = smart_truncate_response(response["data"], None)
        return json.dumps({
            "status": "success",
            "response_info": managed_response,
            "data": managed_response["data"]
        }, indent=2)
    
    # If filtering was applied at API level, return the already filtered response
    return json.dumps(response, indent=2)

@mcp.tool()
async def create_analysis(analysis_data: dict, client: str = None) -> str:
    """Create a new rollout analysis."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.create_analysis(analysis_data, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_analysis(analysis_id: str, client: str = None) -> str:
    """Get a specific analysis by ID."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_analysis(analysis_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def update_analysis(analysis_id: str, analysis_data: dict, client: str = None) -> str:
    """Update an existing analysis."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.update_analysis(analysis_id, analysis_data, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def delete_analysis(analysis_id: str, client: str = None) -> str:
    """Delete an analysis."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.delete_analysis(analysis_id, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def run_analysis(analysis_id: str, force_refresh: bool = False, client: str = None) -> str:
    """Run rollout analysis synchronously."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.run_analysis(analysis_id, force_refresh, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def start_analysis(analysis_id: str, force_refresh: bool = False, client: str = None) -> str:
    """Start analysis asynchronously with progress tracking."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.start_analysis(analysis_id, force_refresh, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_analysis_results(analysis_id: str, client: str = None) -> str:
    """Get results of a completed analysis."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_analysis_results(analysis_id, client or "")
    return json.dumps(result, indent=2)

# Job & System Monitoring Tools
@mcp.tool()
async def get_jobs_summary(start_date: str, end_date: str, client: str = None) -> str:
    """Get count of running jobs and compute hours for date range."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_jobs_summary(start_date, end_date, client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_oldest_job_date(client: str = None) -> str:
    """Get the date of the oldest job for client."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_oldest_job_date(client or "")
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_newest_job_date(client: str = None) -> str:
    """Get the date of the newest job for client."""
    global api_client
    if not api_client:
        api_client = get_api_client()
    
    result = await api_client.get_newest_job_date(client or "")
    return json.dumps(result, indent=2)

def run_http():
    """Entry point for HTTP transport (default)."""
    global api_client
    
    logger.info("Starting Calcs API MCP Server (HTTP Transport)...")
    
    # Initialize API client
    try:
        api_client = get_api_client()
        logger.info(f"Base URL: {api_client.base_url}")
        logger.info(f"Default client: {api_client.default_client or 'None (must be specified per request)'}")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        sys.exit(1)
    
    # Run FastMCP server with HTTP transport for LM Studio compatibility
    mcp.run(transport="streamable-http", host="localhost", port=8002)

def run_sse():
    """Entry point for SSE transport (backward compatibility)."""
    global api_client
    
    logger.info("Starting Calcs API MCP Server (SSE Transport)...")
    
    # Initialize API client
    try:
        api_client = get_api_client()
        logger.info(f"Base URL: {api_client.base_url}")
        logger.info(f"Default client: {api_client.default_client or 'None (must be specified per request)'}")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        sys.exit(1)
    
    # Run FastMCP server with SSE transport for existing clients
    mcp.run(transport="sse", host="localhost", port=8001)

# Default entry point
def run():
    """Default entry point - uses HTTP transport."""
    run_http()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        run_sse()
    else:
        run_http()