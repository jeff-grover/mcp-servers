#!/usr/bin/env python3
"""
Calcs API MCP Server

Provides access to the Calcs API for retail analytics calculations and test management.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any

import httpx
import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

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


class CalcsApiClient:
    """Client for interacting with the Calcs API."""
    
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
    
    async def get_tests(self, client: str = "") -> dict[str, Any]:
        """Get all tests."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
        
        try:
            response = await self.client.get(f"{self.base_url}/v1/tests/", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get tests failed: {e}")
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
    
    # Client endpoints
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
    
    # Results endpoints
    async def get_lift_explorer_results(self, lift_explorer_id: str, client: str = "") -> dict[str, Any]:
        """Get lift explorer results (JSON equivalent of .avro file)."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/results/lift-explorer/{lift_explorer_id}", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get lift explorer results failed: {e}")
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
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Get test results failed: {e}")
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
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"Download all test data failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Lift exploration endpoints
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
    
    # Sites endpoints
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
    
    # Jobs endpoints
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
    
    # Transactions endpoints
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
    
    # Rollout endpoints
    async def list_analyses(self, client: str = "") -> dict[str, Any]:
        """List all analyses for the current client."""
        headers = {}
        client_value = client or self.default_client
        if client_value:
            headers["client"] = client_value
            
        try:
            response = await self.client.get(f"{self.base_url}/v1/rollout/analyses", headers=headers)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            logger.error(f"List analyses failed: {e}")
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


# Initialize API client
def get_api_client() -> CalcsApiClient:
    """Initialize and return the API client."""
    token = os.getenv("CALCS_API_TOKEN")
    if not token:
        raise ValueError("CALCS_API_TOKEN environment variable is required")
    
    base_url = os.getenv("CALCS_API_BASE_URL", "https://staging-app.marketdial.dev/calcs")
    default_client = os.getenv("CALCS_DEFAULT_CLIENT", "")
    
    return CalcsApiClient(base_url, token, default_client)


# MCP Server setup
server = Server("calcs-api")
api_client = None  # Will be initialized in run() function


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="health_check",
            description="Check the health of the Calcs API connection",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_tests",
            description="Get all tests from the Calcs API",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_test_status", 
            description="Get the status of a specific test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "integer",
                        "description": "The ID of the test",
                    },
                    "client": {
                        "type": "string", 
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["test_id"],
            },
        ),
        # Client endpoints
        Tool(
            name="get_active_clients",
            description="Get all active clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_clients_jobs_summary",
            description="Get job information for all active clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for the range (YYYY-MM-DD format)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for the range (YYYY-MM-DD format)",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["start_date", "end_date"],
            },
        ),
        # Results endpoints
        Tool(
            name="get_lift_explorer_results",
            description="Get lift explorer results (JSON equivalent of .avro file contents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "lift_explorer_id": {
                        "type": "string",
                        "description": "The lift explorer ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["lift_explorer_id"],
            },
        ),
        Tool(
            name="get_site_pair_lift_manifest",
            description="Get site pair lift manifest (JSON equivalent of avro)",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "integer",
                        "description": "The test ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["test_id"],
            },
        ),
        Tool(
            name="get_prediction_table",
            description="Get prediction table (JSON equivalent of avro)",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "integer",
                        "description": "The test ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["test_id"],
            },
        ),
        Tool(
            name="get_customer_cross",
            description="Get customer cross data (JSON equivalent of avro)",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "integer",
                        "description": "The test ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["test_id"],
            },
        ),
        Tool(
            name="get_test_results",
            description="Get test results with filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "integer",
                        "description": "The test ID",
                    },
                    "filter_type": {
                        "type": "string",
                        "description": "Filter type (OVERALL, CUSTOMER_COHORT, CUSTOMER_SEGMENT, SITE_COHORT, SITE_PAIR, FINISHED_COHORT, SITE_TAG)",
                        "enum": ["OVERALL", "CUSTOMER_COHORT", "CUSTOMER_SEGMENT", "SITE_COHORT", "SITE_PAIR", "FINISHED_COHORT", "SITE_TAG"]
                    },
                    "filter_value": {
                        "type": "string",
                        "description": "Filter value (optional)",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["test_id", "filter_type"],
            },
        ),
        Tool(
            name="download_all_test_data",
            description="Download all chart data for test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "integer",
                        "description": "The test ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["test_id"],
            },
        ),
        # Lift exploration endpoints
        Tool(
            name="get_lift_explorer_ids",
            description="Get list of valid lift explorer IDs for client",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        # Sites endpoints
        Tool(
            name="get_site_tests",
            description="Get all tests where a site has treatment or control role",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_site_id": {
                        "type": "string",
                        "description": "The client site ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["client_site_id"],
            },
        ),
        # Jobs endpoints
        Tool(
            name="get_jobs_summary",
            description="Get count of running jobs and compute hours for date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for the range (YYYY-MM-DD format)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for the range (YYYY-MM-DD format)",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["start_date", "end_date"],
            },
        ),
        Tool(
            name="get_oldest_job_date",
            description="Get the date of the oldest job for client",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_newest_job_date",
            description="Get the date of the newest job for client",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        # Transactions endpoints
        Tool(
            name="describe_transactions",
            description="Get descriptive overview of the fact_transactions table",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        # Rollout endpoints
        Tool(
            name="list_analyses",
            description="List all analyses for the current client",
            inputSchema={
                "type": "object",
                "properties": {
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="create_analysis",
            description="Create a new analysis for the current client",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_data": {
                        "type": "object",
                        "description": "Analysis data object containing name, description, measurementLength, startDate, etc.",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_data"],
            },
        ),
        Tool(
            name="get_analysis",
            description="Get a specific analysis by ID for the current client",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "The analysis ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_id"],
            },
        ),
        Tool(
            name="update_analysis",
            description="Update an existing analysis for the current client",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "The analysis ID",
                    },
                    "analysis_data": {
                        "type": "object",
                        "description": "Updated analysis data object",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_id", "analysis_data"],
            },
        ),
        Tool(
            name="delete_analysis",
            description="Delete an analysis for the current client",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "The analysis ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_id"],
            },
        ),
        Tool(
            name="run_analysis",
            description="Run the rollout analysis for the specified analysis parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "The analysis ID",
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh the analysis (optional, default false)",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_id"],
            },
        ),
        Tool(
            name="start_analysis",
            description="Start analysis asynchronously and return immediately with progress tracking info",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "The analysis ID",
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh the analysis (optional, default false)",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_id"],
            },
        ),
        Tool(
            name="get_analysis_results",
            description="Get results of a completed analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "The analysis ID",
                    },
                    "client": {
                        "type": "string",
                        "description": "Client identifier (optional, uses default if not provided)",
                    }
                },
                "required": ["analysis_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        # Basic endpoints
        if name == "health_check":
            result = await api_client.health_check()
        elif name == "get_tests":
            client = arguments.get("client", "")
            result = await api_client.get_tests(client)
        elif name == "get_test_status":
            test_id = arguments["test_id"]
            client = arguments.get("client", "")
            result = await api_client.get_test_status(test_id, client)
        
        # Client endpoints
        elif name == "get_active_clients":
            client = arguments.get("client", "")
            result = await api_client.get_active_clients(client)
        elif name == "get_clients_jobs_summary":
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]
            client = arguments.get("client", "")
            result = await api_client.get_clients_jobs_summary(start_date, end_date, client)
        
        # Results endpoints
        elif name == "get_lift_explorer_results":
            lift_explorer_id = arguments["lift_explorer_id"]
            client = arguments.get("client", "")
            result = await api_client.get_lift_explorer_results(lift_explorer_id, client)
        elif name == "get_site_pair_lift_manifest":
            test_id = arguments["test_id"]
            client = arguments.get("client", "")
            result = await api_client.get_site_pair_lift_manifest(test_id, client)
        elif name == "get_prediction_table":
            test_id = arguments["test_id"]
            client = arguments.get("client", "")
            result = await api_client.get_prediction_table(test_id, client)
        elif name == "get_customer_cross":
            test_id = arguments["test_id"]
            client = arguments.get("client", "")
            result = await api_client.get_customer_cross(test_id, client)
        elif name == "get_test_results":
            test_id = arguments["test_id"]
            filter_type = arguments["filter_type"]
            filter_value = arguments.get("filter_value")
            client = arguments.get("client", "")
            result = await api_client.get_test_results(test_id, filter_type, filter_value, client)
        elif name == "download_all_test_data":
            test_id = arguments["test_id"]
            client = arguments.get("client", "")
            result = await api_client.download_all_test_data(test_id, client)
        
        # Lift exploration endpoints
        elif name == "get_lift_explorer_ids":
            client = arguments.get("client", "")
            result = await api_client.get_lift_explorer_ids(client)
        
        # Sites endpoints
        elif name == "get_site_tests":
            client_site_id = arguments["client_site_id"]
            client = arguments.get("client", "")
            result = await api_client.get_site_tests(client_site_id, client)
        
        # Jobs endpoints
        elif name == "get_jobs_summary":
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]
            client = arguments.get("client", "")
            result = await api_client.get_jobs_summary(start_date, end_date, client)
        elif name == "get_oldest_job_date":
            client = arguments.get("client", "")
            result = await api_client.get_oldest_job_date(client)
        elif name == "get_newest_job_date":
            client = arguments.get("client", "")
            result = await api_client.get_newest_job_date(client)
        
        # Transactions endpoints
        elif name == "describe_transactions":
            client = arguments.get("client", "")
            result = await api_client.describe_transactions(client)
        
        # Rollout endpoints
        elif name == "list_analyses":
            client = arguments.get("client", "")
            result = await api_client.list_analyses(client)
        elif name == "create_analysis":
            analysis_data = arguments["analysis_data"]
            client = arguments.get("client", "")
            result = await api_client.create_analysis(analysis_data, client)
        elif name == "get_analysis":
            analysis_id = arguments["analysis_id"]
            client = arguments.get("client", "")
            result = await api_client.get_analysis(analysis_id, client)
        elif name == "update_analysis":
            analysis_id = arguments["analysis_id"]
            analysis_data = arguments["analysis_data"]
            client = arguments.get("client", "")
            result = await api_client.update_analysis(analysis_id, analysis_data, client)
        elif name == "delete_analysis":
            analysis_id = arguments["analysis_id"]
            client = arguments.get("client", "")
            result = await api_client.delete_analysis(analysis_id, client)
        elif name == "run_analysis":
            analysis_id = arguments["analysis_id"]
            force_refresh = arguments.get("force_refresh", False)
            client = arguments.get("client", "")
            result = await api_client.run_analysis(analysis_id, force_refresh, client)
        elif name == "start_analysis":
            analysis_id = arguments["analysis_id"]
            force_refresh = arguments.get("force_refresh", False)
            client = arguments.get("client", "")
            result = await api_client.start_analysis(analysis_id, force_refresh, client)
        elif name == "get_analysis_results":
            analysis_id = arguments["analysis_id"]
            client = arguments.get("client", "")
            result = await api_client.get_analysis_results(analysis_id, client)
        
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def run():
    """Entry point for console script."""
    global api_client
    
    logger.info("Starting Calcs API MCP Server...")
    
    # Initialize API client
    try:
        api_client = get_api_client()
        logger.info(f"Base URL: {api_client.base_url}")
        logger.info(f"Default client: {api_client.default_client or 'None (must be specified per request)'}")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        sys.exit(1)
    
    # Note: API connection will be tested when the server starts serving requests
    
    # Create SSE transport
    sse_transport = SseServerTransport("/messages")
    
    # Create ASGI app
    async def app(scope, receive, send):
        if scope["type"] == "http":
            if scope["path"] == "/messages":
                if scope["method"] == "GET":
                    async with sse_transport.connect_sse(scope, receive, send) as streams:
                        await server.run(streams[0], streams[1], server.create_initialization_options())
                    return
                elif scope["method"] == "POST":
                    await sse_transport.handle_post_message(scope, receive, send)
                    return
        
        # 404 for other paths
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [[b"content-type", b"text/plain"]],
        })
        await send({
            "type": "http.response.body",
            "body": b"Not Found",
        })
    
    # Run the server
    uvicorn.run(app, host="localhost", port=8001)


async def main():
    """Main entry point for stdio mode (backwards compatibility)."""
    logger.info("Starting Calcs API MCP Server in stdio mode...")
    
    # Test API connection in background
    logger.info("Testing API connection...")
    asyncio.create_task(test_api_connection())
    
    logger.info(f"Base URL: {api_client.base_url}")
    logger.info(f"Default client: {api_client.default_client or 'None (must be specified per request)'}")
    
    # Start server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

async def test_api_connection():
    """Test API connection in background."""
    try:
        health_result = await api_client.health_check()
        if health_result["status"] == "error":
            logger.error(f"API health check failed: {health_result['error']}")
        else:
            logger.info("API connection successful")
    except Exception as e:
        logger.error(f"API health check error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # Run in stdio mode for backwards compatibility
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)
    else:
        # Run HTTP server by default
        try:
            run()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)