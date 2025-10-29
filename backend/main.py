import os
import time
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CA Lobby Search API",
    description="California Lobby Data Search and Analytics API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "https://*.vercel.app",   # Vercel deployments
        "https://ca-lobby-deploy-*.vercel.app",  # Specific deployment pattern
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    timestamp: str
    uptime: float
    source: str = "FastAPI Backend"

class SystemStatusResponse(BaseModel):
    environment: str
    mock_data: bool
    debug: bool
    api_version: str
    database_connected: bool

class LobbyRecord(BaseModel):
    id: str
    organization: str
    lobbyist: str
    amount: float
    date: str
    category: str
    description: str
    issues: List[str]

class SearchResponse(BaseModel):
    data: List[LobbyRecord]
    pagination: Dict[str, Any]
    filters_applied: Dict[str, Any]
    total_results: int
    search_time_ms: float

class DataAccessResponse(BaseModel):
    status: str
    message: str
    available_modules: List[str]
    records_available: int

# Global variables for tracking
start_time = time.time()

# Sample mock data for testing
MOCK_LOBBY_DATA = [
    {
        "id": "1",
        "organization": "California Healthcare Association",
        "lobbyist": "John Smith",
        "amount": 250000.00,
        "date": "2025-09-15",
        "category": "healthcare",
        "description": "Healthcare policy advocacy and legislative support",
        "issues": ["AB-123", "SB-456", "Healthcare Reform"]
    },
    {
        "id": "2",
        "organization": "Tech Forward California",
        "lobbyist": "Sarah Johnson",
        "amount": 180000.00,
        "date": "2025-09-10",
        "category": "technology",
        "description": "Technology innovation and digital privacy legislation",
        "issues": ["AB-789", "Data Privacy", "AI Regulation"]
    },
    {
        "id": "3",
        "organization": "Environmental Defense Fund",
        "lobbyist": "Michael Chen",
        "amount": 320000.00,
        "date": "2025-09-05",
        "category": "environment",
        "description": "Climate change and environmental protection advocacy",
        "issues": ["SB-101", "Climate Action", "Renewable Energy"]
    },
    {
        "id": "4",
        "organization": "California Teachers Association",
        "lobbyist": "Lisa Rodriguez",
        "amount": 420000.00,
        "date": "2025-08-28",
        "category": "education",
        "description": "Education funding and teacher support legislation",
        "issues": ["AB-202", "Education Funding", "Teacher Rights"]
    },
    {
        "id": "5",
        "organization": "Financial Services Coalition",
        "lobbyist": "David Wilson",
        "amount": 150000.00,
        "date": "2025-08-20",
        "category": "finance",
        "description": "Banking and financial services regulation",
        "issues": ["SB-303", "Banking Reform", "Consumer Protection"]
    }
]

# API Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "CA Lobby Search API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    current_time = time.time()
    uptime = current_time - start_time

    return HealthResponse(
        status="healthy",
        message="API is operational",
        version="1.0.0",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(current_time)),
        uptime=round(uptime, 2),
        source="FastAPI Backend"
    )

@app.get("/api/status", response_model=SystemStatusResponse)
async def system_status():
    """System status information"""
    return SystemStatusResponse(
        environment=os.getenv("ENVIRONMENT", "development"),
        mock_data=True,  # Currently using mock data
        debug=os.getenv("DEBUG", "true").lower() == "true",
        api_version="1.0.0",
        database_connected=False  # Will be true when BigQuery is connected
    )

@app.get("/api/test-data-access", response_model=DataAccessResponse)
async def test_data_access():
    """Test data access capabilities"""
    return DataAccessResponse(
        status="operational",
        message="Mock data access is functioning",
        available_modules=["lobby_data", "search_engine", "analytics"],
        records_available=len(MOCK_LOBBY_DATA)
    )

@app.get("/v1/search", response_model=SearchResponse)
async def search_lobby_data(
    query: Optional[str] = Query(None, description="Search term"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    organization: Optional[str] = Query(None, description="Organization filter"),
    lobbyist: Optional[str] = Query(None, description="Lobbyist filter"),
    category: Optional[str] = Query("all", description="Category filter"),
    amount_min: Optional[float] = Query(None, description="Minimum amount"),
    amount_max: Optional[float] = Query(None, description="Maximum amount"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Results per page")
):
    """Search lobby data with filters"""
    search_start_time = time.time()

    # Filter mock data based on parameters
    filtered_data = MOCK_LOBBY_DATA.copy()

    # Apply query filter (simple text search)
    if query:
        query_lower = query.lower()
        filtered_data = [
            record for record in filtered_data
            if (query_lower in record["organization"].lower() or
                query_lower in record["lobbyist"].lower() or
                query_lower in record["description"].lower() or
                any(query_lower in issue.lower() for issue in record["issues"]))
        ]

    # Apply category filter
    if category and category != "all":
        filtered_data = [
            record for record in filtered_data
            if record["category"] == category
        ]

    # Apply organization filter
    if organization:
        org_lower = organization.lower()
        filtered_data = [
            record for record in filtered_data
            if org_lower in record["organization"].lower()
        ]

    # Apply lobbyist filter
    if lobbyist:
        lobbyist_lower = lobbyist.lower()
        filtered_data = [
            record for record in filtered_data
            if lobbyist_lower in record["lobbyist"].lower()
        ]

    # Apply amount filters
    if amount_min is not None:
        filtered_data = [
            record for record in filtered_data
            if record["amount"] >= amount_min
        ]

    if amount_max is not None:
        filtered_data = [
            record for record in filtered_data
            if record["amount"] <= amount_max
        ]

    # Calculate pagination
    total_results = len(filtered_data)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_data = filtered_data[start_index:end_index]

    # Calculate search time
    search_time_ms = round((time.time() - search_start_time) * 1000, 2)

    return SearchResponse(
        data=[LobbyRecord(**record) for record in paginated_data],
        pagination={
            "current_page": page,
            "total_pages": (total_results + limit - 1) // limit,
            "total_results": total_results,
            "has_next": end_index < total_results,
            "has_previous": page > 1
        },
        filters_applied={
            "query": query,
            "category": category,
            "organization": organization,
            "lobbyist": lobbyist,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "date_from": date_from,
            "date_to": date_to
        },
        total_results=total_results,
        search_time_ms=search_time_ms
    )

@app.get("/v1/analytics/trends")
async def get_trends(
    timeframe: str = Query("month", description="Timeframe for trends"),
    category: Optional[str] = Query(None, description="Category filter")
):
    """Get lobby expenditure trends"""
    # Mock trend data
    trend_data = [
        {"date": "2025-09-01", "amount": 450000, "count": 12},
        {"date": "2025-09-08", "amount": 520000, "count": 15},
        {"date": "2025-09-15", "amount": 380000, "count": 10},
        {"date": "2025-09-22", "amount": 610000, "count": 18},
    ]

    return {
        "timeframe": timeframe,
        "data": trend_data
    }

@app.get("/v1/analytics/organizations")
async def get_organization_analytics(
    limit: int = Query(10, description="Number of top organizations"),
    timeframe: str = Query("year", description="Timeframe for analysis")
):
    """Get top organizations by spending"""
    # Mock organization data
    org_data = [
        {"organization": "California Healthcare Association", "total_amount": 250000, "transaction_count": 5, "percentage_of_total": 25.5},
        {"organization": "Environmental Defense Fund", "total_amount": 320000, "transaction_count": 8, "percentage_of_total": 32.6},
        {"organization": "California Teachers Association", "total_amount": 420000, "transaction_count": 12, "percentage_of_total": 42.9},
    ]

    return {
        "timeframe": timeframe,
        "data": org_data[:limit]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )