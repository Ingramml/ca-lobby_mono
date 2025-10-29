# CA Lobby API Documentation

**API Version**: 1.0.0
**Last Updated**: September 29, 2025
**Phase**: 2e - API Design Specification Complete

## 🎯 **API Overview**

The CA Lobby API provides comprehensive access to California lobbying data with advanced search, analytics, and user management capabilities. Built with mobile-first principles and optimized for performance across all devices.

### **Current Implementation Status**
- ✅ **Phase 1.3**: Backend API implemented with Flask
- ✅ **Demo Mode**: 5 representative lobby records for testing
- ✅ **Authentication**: Clerk-based JWT authentication
- ✅ **Mobile Optimization**: Designed for mobile-first usage patterns

---

## 📋 **Quick Start**

### **Base URLs**
- **Production**: `https://ca-lobby-webapp.vercel.app/api/v1`
- **Development**: `http://localhost:5001/api/v1`

### **Authentication**
All API endpoints (except `/health`) require Clerk JWT authentication:

```javascript
// Example request with authentication
const response = await fetch('/api/v1/search?query=healthcare', {
  headers: {
    'Authorization': `Bearer ${clerkToken}`,
    'Content-Type': 'application/json'
  }
});
```

### **Basic Search Example**
```javascript
// Search for healthcare-related lobby activities
GET /api/v1/search?query=healthcare&category=healthcare&limit=10

// Example response
{
  "success": true,
  "data": [
    {
      "id": "1",
      "organization": "California Medical Association",
      "lobbyist": "John Smith",
      "amount": 125000,
      "date": "2024-09-15",
      "category": "healthcare",
      "description": "Healthcare legislation advocacy..."
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_results": 1
  }
}
```

---

## 🔍 **Core Endpoints**

### **Search Operations**
- `GET /search` - Advanced lobby data search with filtering
- `GET /search/suggestions` - Autocomplete suggestions

### **Analytics & Visualization**
- `GET /analytics/trends` - Time-series data for trend charts
- `GET /analytics/organizations` - Top organizations by spending
- `GET /analytics/categories` - Category breakdown for pie charts

### **User Management**
- `GET /user/searches` - Saved searches
- `POST /user/searches` - Save new search
- `GET /user/preferences` - User preferences
- `PUT /user/preferences` - Update preferences

### **System Monitoring**
- `GET /health` - System health check (no auth required)
- `GET /status` - Detailed system status
- `GET /cache/stats` - Cache performance metrics

### **Data Export**
- `POST /export/search` - Export search results (CSV, PDF, Excel)

---

## 📱 **Mobile Optimization Features**

### **Data Efficiency**
- **Compressed Responses**: JSON responses optimized for mobile bandwidth
- **Pagination**: Default 25 results per page, configurable 1-100
- **Selective Fields**: Request only needed data fields

### **Performance Optimization**
- **Caching Headers**: Appropriate cache-control for mobile networks
- **Response Compression**: GZIP compression enabled
- **Timeout Handling**: Graceful timeout handling for slow connections

### **Offline Support Patterns**
- **HTTP Caching**: Cacheable responses with appropriate headers
- **Error Recovery**: Detailed error codes for client-side retry logic
- **Progressive Loading**: Support for incremental data loading

---

## 📊 **Demo Data Reference**

### **Available Test Records (5 total)**
1. **California Medical Association** - John Smith - $125,000 (Healthcare)
2. **Tech Innovation Coalition** - Sarah Johnson - $89,000 (Technology)
3. **Environmental Defense Alliance** - Michael Chen - $67,500 (Environment)
4. **Education Reform Society** - Emily Rodriguez - $52,000 (Education)
5. **Small Business Coalition** - David Wilson - $43,200 (Business)

### **Test Search Queries**
- `query=healthcare` → Returns California Medical Association
- `query=technology` → Returns Tech Innovation Coalition
- `organization=Medical` → Returns California Medical Association
- `lobbyist=John Smith` → Returns California Medical Association
- `amount_min=50000&amount_max=100000` → Returns multiple records

---

## 🔧 **Integration Guide**

### **With Existing Frontend Components**

#### **Search Component Integration**
```javascript
// Current search implementation in src/components/Search.js
import { apiCall, API_ENDPOINTS } from '../config/api';

const handleSearch = async () => {
  const searchParams = new URLSearchParams({
    q: query.trim(),
    organization: filters.organization || '',
    lobbyist: filters.lobbyist || '',
    category: filters.category === 'all' ? '' : filters.category || '',
    page: 1,
    limit: 25
  });

  const data = await apiCall(`${API_ENDPOINTS.search}?${searchParams}`);
  // Results integrated with Zustand search store
};
```

#### **Analytics Integration**
```javascript
// Integration with existing chart components
import { LobbyTrendsChart, OrganizationChart } from './charts';

// Charts automatically fetch data from analytics endpoints
<LobbyTrendsChart endpoint="/analytics/trends?timeframe=month" />
<OrganizationChart endpoint="/analytics/organizations?limit=10" />
```

#### **User Preferences Integration**
```javascript
// Integration with existing Zustand userStore
import { useUserStore } from '../stores';

const { preferences, updatePreferences } = useUserStore();

// Sync with API when preferences change
const syncPreferences = async (newPrefs) => {
  await apiCall('/user/preferences', {
    method: 'PUT',
    body: JSON.stringify(newPrefs)
  });
  updatePreferences(newPrefs);
};
```

---

## 🚨 **Error Handling**

### **Standard Error Response Format**
```json
{
  "error": "Description of the error",
  "code": "ERROR_CODE",
  "details": {
    "parameter": "field_name",
    "message": "Specific error details"
  },
  "timestamp": "2024-09-29T15:30:00Z"
}
```

### **Common Error Codes**
- `INVALID_PARAMETER` - Bad request parameter
- `UNAUTHORIZED` - Authentication required/failed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

### **Mobile Network Error Handling**
```javascript
// Recommended error handling for mobile networks
const apiCallWithRetry = async (url, options, retries = 3) => {
  try {
    return await apiCall(url, options);
  } catch (error) {
    if (error.code === 'NETWORK_ERROR' && retries > 0) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return apiCallWithRetry(url, options, retries - 1);
    }
    throw error;
  }
};
```

---

## 🔐 **Security**

### **Authentication Flow**
1. User authenticates with Clerk
2. Frontend receives JWT token
3. Token included in `Authorization: Bearer {token}` header
4. Backend validates token with Clerk

### **Rate Limiting**
- **Search Endpoints**: 100 requests per hour per user
- **Analytics Endpoints**: 50 requests per hour per user
- **Export Endpoints**: 10 requests per hour per user

### **Data Privacy**
- All lobby data is public information
- User preferences and saved searches are user-specific
- No personally identifiable information stored beyond Clerk user ID

---

## 📈 **Performance Monitoring**

### **Key Metrics**
- **Response Time**: Target <2 seconds for search endpoints
- **Cache Hit Rate**: Target >80% for analytics endpoints
- **Error Rate**: Target <1% for all endpoints
- **Mobile Performance**: Optimized for 3G/4G networks

### **Monitoring Endpoints**
- `/health` - Basic health check
- `/status` - Detailed component status
- `/cache/stats` - Cache performance metrics

---

## 🔗 **Related Documentation**

- **OpenAPI Specification**: [`ca-lobby-api-specification.yaml`](./ca-lobby-api-specification.yaml)
- **Frontend Integration**: [`../Phase2/Plans/PHASE_2E_API_DESIGN_SPECIFICATION.md`](../Phase2/Plans/PHASE_2E_API_DESIGN_SPECIFICATION.md)
- **Testing Guide**: [`../Testing/TEST_DATA_SEARCH_CASES.md`](../Testing/TEST_DATA_SEARCH_CASES.md)
- **Mobile Optimization**: [`../Phase2/Plans/PHASE_2D_MOBILE_FIRST_CSS_STRATEGY.md`](../Phase2/Plans/PHASE_2D_MOBILE_FIRST_CSS_STRATEGY.md)

---

**API Documentation Status**: ✅ Complete
**Implementation Ready**: Phase 1.3 backend integration
**Testing Ready**: Demo mode with 5 test records
**Mobile Optimized**: Full mobile-first design patterns