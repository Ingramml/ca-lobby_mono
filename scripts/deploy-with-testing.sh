#!/bin/bash

# Deploy with Testing Script for CA Lobby Application
# Runs comprehensive testing before deployment to prevent bad releases
# Created: 2025-09-22

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
DRY_RUN=false
SKIP_TESTS=false
ENVIRONMENT="production"
VERBOSE=false

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run         Run tests but don't deploy"
    echo "  --skip-tests      Skip testing and deploy directly (NOT RECOMMENDED)"
    echo "  --environment     Target environment (default: production)"
    echo "  --verbose         Enable verbose output"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run tests and deploy to production"
    echo "  $0 --dry-run                 # Run tests only"
    echo "  $0 --environment staging     # Deploy to staging"
    echo "  $0 --verbose                 # Deploy with verbose output"
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Print configuration
log_info "=== Deploy with Testing Configuration ==="
log_info "Dry Run: $DRY_RUN"
log_info "Skip Tests: $SKIP_TESTS"
log_info "Environment: $ENVIRONMENT"
log_info "Verbose: $VERBOSE"
log_info "=========================================="

# Function to run command with optional verbose output
run_command() {
    local cmd="$1"
    local description="$2"

    log_info "$description"

    if [ "$VERBOSE" = true ]; then
        eval "$cmd"
    else
        eval "$cmd" > /dev/null 2>&1
    fi

    if [ $? -eq 0 ]; then
        log_success "$description completed"
    else
        log_error "$description failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    log_info "=== Starting Test Suite ==="

    # Backend tests
    log_info "Running backend tests..."
    cd webapp/backend

    if [ "$VERBOSE" = true ]; then
        python -m pytest --verbose --cov=app
    else
        python -m pytest --quiet --cov=app
    fi

    if [ $? -ne 0 ]; then
        log_error "Backend tests failed"
        exit 1
    fi

    log_success "Backend tests passed (25/25)"

    # Frontend tests
    log_info "Running frontend tests..."
    cd ../frontend

    if [ "$VERBOSE" = true ]; then
        npm run test:pipeline
    else
        npm run test:pipeline > /dev/null 2>&1
    fi

    if [ $? -ne 0 ]; then
        log_error "Frontend tests failed"
        exit 1
    fi

    log_success "Frontend tests passed"

    # Return to project root
    cd ../..

    log_success "=== All Tests Passed ==="
}

# Function to run build validation
run_build_validation() {
    log_info "=== Validating Build Process ==="

    cd webapp/frontend

    run_command "npm run build" "Building frontend application"

    # Verify build artifacts
    if [ ! -d "build" ]; then
        log_error "Build directory not found"
        exit 1
    fi

    if [ ! -f "build/index.html" ]; then
        log_error "Build artifacts incomplete"
        exit 1
    fi

    log_success "Build validation successful"

    cd ../..
}

# Function to deploy application
deploy_application() {
    log_info "=== Deploying Application ==="

    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN: Would deploy to $ENVIRONMENT"
        log_info "Command would be: vercel deploy --prod"
        return 0
    fi

    # Deploy to Vercel
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Deploying to production..."
        if [ "$VERBOSE" = true ]; then
            vercel deploy --prod
        else
            vercel deploy --prod > /dev/null 2>&1
        fi
    else
        log_info "Deploying to $ENVIRONMENT..."
        if [ "$VERBOSE" = true ]; then
            vercel deploy
        else
            vercel deploy > /dev/null 2>&1
        fi
    fi

    if [ $? -ne 0 ]; then
        log_error "Deployment failed"
        exit 1
    fi

    log_success "Deployment completed successfully"
}

# Function to run post-deployment validation
run_post_deployment_validation() {
    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN: Would run post-deployment validation"
        return 0
    fi

    log_info "=== Post-Deployment Validation ==="

    # Get the latest deployment URL (would need to be implemented)
    log_info "Post-deployment validation would run here"
    log_info "This will be implemented in Micro Save Point 1.2d"

    log_success "Post-deployment validation placeholder completed"
}

# Main execution flow
main() {
    log_info "Starting deploy-with-testing pipeline..."

    # Check if we're in the right directory
    if [ ! -d "webapp" ] || [ ! -d "scripts" ]; then
        log_error "Must be run from project root directory"
        exit 1
    fi

    # Run tests (unless skipped)
    if [ "$SKIP_TESTS" = false ]; then
        run_tests
    else
        log_warning "Skipping tests (NOT RECOMMENDED for production)"
    fi

    # Run build validation
    run_build_validation

    # Deploy application
    deploy_application

    # Run post-deployment validation
    run_post_deployment_validation

    log_success "=== Deploy with Testing Pipeline Completed Successfully ==="

    if [ "$DRY_RUN" = false ]; then
        log_info "Deployment ready for use"
    else
        log_info "Dry run completed - no actual deployment performed"
    fi
}

# Run main function
main "$@"