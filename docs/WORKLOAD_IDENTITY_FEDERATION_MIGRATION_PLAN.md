# Workload Identity Federation Migration Plan

## Executive Summary
Migration plan for transitioning CA Lobby's BigQuery authentication from service account keys to Workload Identity Federation (WIF) for improved security and credential management.

## Current State
- Using service account JSON key files for BigQuery API authentication
- Keys stored as environment variables or in secure configuration
- Manual key rotation required
- Risk of key exposure through logs, version control, or compromised systems

## Target State
- Workload Identity Federation configured for automatic credential management
- No long-lived service account keys
- Token-based authentication with automatic refresh
- Identity provider integration (GitHub Actions, Cloud Run, or external IdP)

## Benefits
- **Enhanced Security**: Eliminates long-lived credentials
- **Reduced Risk**: No keys to leak or compromise
- **Automated Management**: No manual key rotation needed
- **Audit Trail**: Better tracking of authentication events
- **Compliance**: Meets enterprise security standards

---

## Migration Phases

### Phase 1: Assessment & Planning (Week 1)

#### 1.1 Inventory Current Usage
- [ ] List all services currently using service account keys
- [ ] Document which BigQuery datasets/tables each service accesses
- [ ] Identify the deployment environment(s):
  - Google Cloud (Cloud Run, GKE, Compute Engine)
  - External cloud provider (AWS, Azure)
  - GitHub Actions
  - Local development
  - Other CI/CD pipelines

#### 1.2 Determine Identity Provider
Choose based on deployment environment:

**Option A: Google Cloud Workload Identity** (if running on GCP)
- For Cloud Run, GKE, Cloud Functions
- Native integration, simplest setup

**Option B: GitHub Actions OIDC** (if using GitHub Actions)
- For CI/CD pipelines
- No secrets stored in GitHub

**Option C: External Identity Provider Federation** (if running on AWS/Azure/other)
- For applications running outside Google Cloud
- Requires OIDC-compliant identity provider

#### 1.3 Define Service Accounts & Permissions
- [ ] Audit current service account IAM roles
- [ ] Document required BigQuery permissions per service
- [ ] Plan for least-privilege access model
- [ ] Create new service accounts if needed (separate per environment)

---

### Phase 2: Infrastructure Setup (Week 2)

#### 2.1 Create Workload Identity Pool

```bash
# Set project variables
export PROJECT_ID="your-gcp-project-id"
export POOL_ID="ca-lobby-pool"
export POOL_DISPLAY_NAME="CA Lobby Workload Identity Pool"

# Create workload identity pool
gcloud iam workload-identity-pools create ${POOL_ID} \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="${POOL_DISPLAY_NAME}"
```

#### 2.2 Configure Identity Provider

**For GitHub Actions:**
```bash
export PROVIDER_ID="github-provider"
export GITHUB_ORG="your-github-org"
export GITHUB_REPO="ca-lobby_mono"

# Create provider
gcloud iam workload-identity-pools providers create-oidc ${PROVIDER_ID} \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

**For Cloud Run:**
```bash
# Cloud Run uses built-in workload identity
# Attach service account to Cloud Run service
gcloud run services update YOUR_SERVICE_NAME \
  --service-account=YOUR_SERVICE_ACCOUNT@${PROJECT_ID}.iam.gserviceaccount.com
```

**For AWS/Azure (example for AWS):**
```bash
export PROVIDER_ID="aws-provider"
export AWS_ACCOUNT_ID="your-aws-account-id"

gcloud iam workload-identity-pools providers create-aws ${PROVIDER_ID} \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --account-id="${AWS_ACCOUNT_ID}"
```

#### 2.3 Grant Service Account Access

```bash
export SERVICE_ACCOUNT_EMAIL="bigquery-access@${PROJECT_ID}.iam.gserviceaccount.com"

# For GitHub Actions - grant specific repo access
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT_EMAIL} \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"

# Ensure service account has BigQuery permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/bigquery.jobUser"
```

---

### Phase 3: Code Implementation (Week 2-3)

#### 3.1 Update Backend Dependencies

**Python (FastAPI/Django):**
```bash
# Update requirements.txt
pip install google-auth google-cloud-bigquery
```

**Node.js:**
```bash
npm install @google-cloud/bigquery google-auth-library
```

#### 3.2 Implement Authentication Logic

**Python Example:**
```python
# backend/services/bigquery_client.py
from google.auth import identity_pool
from google.cloud import bigquery
import os

def get_bigquery_client_wif():
    """
    Create BigQuery client using Workload Identity Federation
    """
    # For GitHub Actions or external workloads
    if os.getenv('WORKLOAD_IDENTITY_PROVIDER'):
        credentials = identity_pool.Credentials.from_info(
            info={
                "type": "external_account",
                "audience": f"//iam.googleapis.com/projects/{PROJECT_NUMBER}/locations/global/workloadIdentityPools/{POOL_ID}/providers/{PROVIDER_ID}",
                "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
                "token_url": "https://sts.googleapis.com/v1/token",
                "service_account_impersonation_url": f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{SERVICE_ACCOUNT_EMAIL}:generateAccessToken",
            }
        )
    else:
        # For Cloud Run/GKE - uses Application Default Credentials
        from google.auth import default
        credentials, project = default()

    return bigquery.Client(credentials=credentials, project=PROJECT_ID)

def get_bigquery_client_legacy():
    """
    Legacy method using service account key (for comparison)
    """
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)
```

**Node.js Example:**
```javascript
// backend/services/bigqueryClient.js
const { BigQuery } = require('@google-cloud/bigquery');
const { GoogleAuth } = require('google-auth-library');

async function getBigQueryClientWIF() {
  // For Cloud Run/GKE - automatically uses workload identity
  const bigquery = new BigQuery({
    projectId: process.env.GCP_PROJECT_ID
  });

  return bigquery;
}

async function getBigQueryClientExternal() {
  // For external workloads (GitHub Actions, AWS, etc.)
  const auth = new GoogleAuth({
    scopes: ['https://www.googleapis.com/auth/bigquery']
  });

  const client = await auth.getClient();
  const bigquery = new BigQuery({
    projectId: process.env.GCP_PROJECT_ID,
    authClient: client
  });

  return bigquery;
}
```

#### 3.3 Update Configuration

**Environment Variables (Before):**
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=your-project-id
```

**Environment Variables (After):**
```bash
# For Cloud Run/GKE (no additional env vars needed)
GCP_PROJECT_ID=your-project-id

# For GitHub Actions
WORKLOAD_IDENTITY_PROVIDER=projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID
SERVICE_ACCOUNT_EMAIL=bigquery-access@PROJECT_ID.iam.gserviceaccount.com
GCP_PROJECT_ID=your-project-id
```

#### 3.4 Update GitHub Actions Workflow (if applicable)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # Required for OIDC

    steps:
      - uses: actions/checkout@v3

      - id: auth
        name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1

      - name: Run BigQuery operations
        run: |
          # Your BigQuery commands here
          python scripts/run_bigquery_analysis.py
```

---

### Phase 4: Testing & Validation (Week 3)

#### 4.1 Create Test Environment
- [ ] Set up separate test workload identity pool
- [ ] Configure test service account with limited permissions
- [ ] Deploy test version of application

#### 4.2 Test Authentication Flow
```python
# tests/test_bigquery_wif.py
import pytest
from backend.services.bigquery_client import get_bigquery_client_wif

def test_workload_identity_authentication():
    """Test WIF authentication succeeds"""
    client = get_bigquery_client_wif()
    assert client is not None

def test_bigquery_query_execution():
    """Test actual BigQuery query with WIF credentials"""
    client = get_bigquery_client_wif()

    query = """
        SELECT COUNT(*) as count
        FROM `your-project.your_dataset.your_table`
        LIMIT 1
    """

    query_job = client.query(query)
    results = list(query_job.result())

    assert len(results) > 0
    assert results[0].count >= 0

def test_permission_boundaries():
    """Test that service account only has required permissions"""
    client = get_bigquery_client_wif()

    # Should succeed - read access
    query = "SELECT 1"
    client.query(query).result()

    # Should fail - no delete permission
    with pytest.raises(Exception):
        client.delete_table("your-project.your_dataset.test_table")
```

#### 4.3 Validation Checklist
- [ ] Authentication succeeds in all environments
- [ ] BigQuery queries execute successfully
- [ ] No service account keys in environment variables
- [ ] Logs show proper authentication method
- [ ] IAM permissions are correctly scoped
- [ ] Token refresh works automatically
- [ ] Error handling works for auth failures

---

### Phase 5: Deployment & Migration (Week 4)

#### 5.1 Phased Rollout Strategy

**Option A: Blue-Green Deployment**
1. Deploy new version with WIF to staging
2. Run parallel with key-based version
3. Validate metrics and logs
4. Switch traffic to WIF version
5. Keep key-based version as rollback

**Option B: Canary Deployment**
1. Deploy WIF to 10% of traffic
2. Monitor error rates and latency
3. Gradually increase to 50%, then 100%
4. Roll back if issues detected

#### 5.2 Deployment Steps

**For Cloud Run:**
```bash
# Deploy new revision with workload identity
gcloud run deploy ca-lobby-backend \
  --image=gcr.io/${PROJECT_ID}/ca-lobby-backend:latest \
  --service-account=${SERVICE_ACCOUNT_EMAIL} \
  --region=us-central1 \
  --platform=managed
```

**For GitHub Actions:**
```bash
# Update GitHub secrets
gh secret set WIF_PROVIDER --body "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID"
gh secret set WIF_SERVICE_ACCOUNT --body "bigquery-access@PROJECT_ID.iam.gserviceaccount.com"

# Remove old secret
gh secret delete GCP_SERVICE_ACCOUNT_KEY
```

#### 5.3 Monitor Migration
- [ ] Set up monitoring dashboards
- [ ] Track authentication success/failure rates
- [ ] Monitor BigQuery API latency
- [ ] Watch for IAM permission errors
- [ ] Check application logs for auth issues

---

### Phase 6: Cleanup & Documentation (Week 4-5)

#### 6.1 Remove Service Account Keys
```bash
# List all keys for service account
gcloud iam service-accounts keys list \
  --iam-account=${SERVICE_ACCOUNT_EMAIL}

# Delete each key (DO NOT delete Google-managed keys)
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=${SERVICE_ACCOUNT_EMAIL}
```

#### 6.2 Update Documentation
- [ ] Update deployment documentation
- [ ] Document workload identity configuration
- [ ] Update runbooks for troubleshooting
- [ ] Create onboarding guide for new developers
- [ ] Document rollback procedures

#### 6.3 Security Hardening
- [ ] Enable Cloud Audit Logs for IAM
- [ ] Set up alerts for unusual authentication patterns
- [ ] Review service account IAM bindings
- [ ] Implement conditional IAM policies (if needed)
- [ ] Document least-privilege access model

#### 6.4 Remove Legacy Code
```python
# Remove legacy authentication methods
# Delete get_bigquery_client_legacy() function
# Remove GOOGLE_APPLICATION_CREDENTIALS from env configs
# Delete service account key files from secure storage
```

---

## Environment-Specific Configurations

### Development Environment
**Option 1: Use gcloud CLI credentials**
```bash
gcloud auth application-default login
```

**Option 2: Use service account impersonation**
```bash
gcloud auth application-default login --impersonate-service-account=${SERVICE_ACCOUNT_EMAIL}
```

### CI/CD (GitHub Actions)
```yaml
# Use google-github-actions/auth with WIF
- uses: google-github-actions/auth@v1
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

### Production (Cloud Run)
```bash
# Service account attached to Cloud Run service
# No code changes needed - uses Application Default Credentials
```

---

## Rollback Plan

### If Issues Arise During Migration

#### Quick Rollback Steps
1. Revert to previous deployment with service account keys
2. Re-enable service account key in environment variables
3. Switch traffic back to stable version

#### Rollback Commands
```bash
# Cloud Run rollback
gcloud run services update-traffic ca-lobby-backend \
  --to-revisions=PREVIOUS_REVISION=100

# Re-create service account key (temporary)
gcloud iam service-accounts keys create key.json \
  --iam-account=${SERVICE_ACCOUNT_EMAIL}
```

### Common Issues & Solutions

**Issue: "Permission denied" errors**
- Verify service account has required IAM roles
- Check workload identity pool bindings
- Ensure correct audience in token exchange

**Issue: Token exchange fails**
- Validate workload identity provider configuration
- Check attribute mappings
- Verify OIDC token claims

**Issue: Application can't authenticate**
- Confirm Application Default Credentials are available
- Check service account attachment (for Cloud Run/GKE)
- Verify environment variables are set correctly

---

## Success Criteria

### Technical Metrics
- ✅ 100% of services using Workload Identity Federation
- ✅ Zero service account keys in use
- ✅ Authentication success rate > 99.9%
- ✅ No increase in BigQuery API latency
- ✅ All automated tests passing

### Security Metrics
- ✅ No long-lived credentials in environment
- ✅ Audit logs enabled for all authentication events
- ✅ Service accounts follow least-privilege model
- ✅ No keys stored in version control or logs

### Operational Metrics
- ✅ Documentation updated and complete
- ✅ Team trained on new authentication flow
- ✅ Monitoring and alerting in place
- ✅ Rollback procedure tested and documented

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1. Assessment | Week 1 | Inventory, IdP selection, permission audit |
| 2. Infrastructure | Week 2 | WIF pool, provider, IAM bindings |
| 3. Code Implementation | Week 2-3 | Updated auth logic, configuration |
| 4. Testing | Week 3 | Test suite, validation |
| 5. Deployment | Week 4 | Production rollout, monitoring |
| 6. Cleanup | Week 4-5 | Key removal, documentation |

**Total Duration: 4-5 weeks**

---

## Resources & References

### Google Cloud Documentation
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Configuring workload identity federation with GitHub Actions](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines#github-actions)
- [Best practices for managing service accounts](https://cloud.google.com/iam/docs/best-practices-service-accounts)

### Tools & Libraries
- [google-auth Python library](https://google-auth.readthedocs.io/)
- [google-auth-library Node.js](https://github.com/googleapis/google-auth-library-nodejs)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)

### Security Best Practices
- [OIDC token exchange](https://cloud.google.com/iam/docs/workload-identity-federation#oidc)
- [Credential access boundaries](https://cloud.google.com/iam/docs/downscoping-short-lived-credentials)
- [Cloud Audit Logs](https://cloud.google.com/logging/docs/audit)

---

## Next Steps

1. Review this plan with the development team
2. Identify which deployment environment(s) apply to CA Lobby
3. Schedule migration window with stakeholders
4. Begin Phase 1: Assessment & Planning
5. Set up test environment for validation

## Questions to Answer Before Starting

- [ ] Where is the CA Lobby backend deployed? (Cloud Run, GKE, external)
- [ ] Which CI/CD system is used? (GitHub Actions, Cloud Build, other)
- [ ] Who has permissions to manage GCP IAM resources?
- [ ] What is the current service account key rotation policy?
- [ ] Are there any compliance requirements for this migration?
- [ ] What is the acceptable downtime window (if any)?

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Owner:** CA Lobby Development Team
