#!/bin/bash

# Error Code Classification System for CA Lobby Deployment Pipeline
# Defines standard error codes and their handling procedures
# Created: 2025-09-22

# Error code definitions
export ERROR_CODE_TEST_FAILURE=1       # Test failures (block deployment)
export ERROR_CODE_BUILD_FAILURE=2      # Build failures (rollback to last known good)
export ERROR_CODE_DEPLOY_FAILURE=3     # Deployment failures (immediate rollback)
export ERROR_CODE_VALIDATION_FAILURE=4 # Validation failures (conditional rollback)

# Error descriptions (using functions for compatibility)
get_error_description_lookup() {
    case $1 in
        1) echo "Test Failure - Tests failed during pre-deployment verification" ;;
        2) echo "Build Failure - Application build process failed" ;;
        3) echo "Deployment Failure - Deployment to platform failed" ;;
        4) echo "Validation Failure - Post-deployment validation failed" ;;
        *) echo "Unknown error code: $1" ;;
    esac
}

# Error handling strategies (using functions for compatibility)
get_error_strategy_lookup() {
    case $1 in
        1) echo "BLOCK_DEPLOYMENT" ;;
        2) echo "ROLLBACK_TO_LAST_GOOD" ;;
        3) echo "IMMEDIATE_ROLLBACK" ;;
        4) echo "CONDITIONAL_ROLLBACK" ;;
        *) echo "UNKNOWN_STRATEGY" ;;
    esac
}

# Functions for error handling

# Get error description
get_error_description() {
    local error_code=$1
    get_error_description_lookup "$error_code"
}

# Get error strategy
get_error_strategy() {
    local error_code=$1
    get_error_strategy_lookup "$error_code"
}

# Log error with classification
log_classified_error() {
    local error_code=$1
    local error_message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    local description=$(get_error_description "$error_code")
    local strategy=$(get_error_strategy "$error_code")

    echo "[$timestamp] [ERROR] Code: $error_code | Strategy: $strategy | Description: $description | Message: $error_message"

    # Log to error classification file
    local error_log="logs/error_classification.log"
    mkdir -p logs
    echo "[$timestamp] ERROR_CODE=$error_code STRATEGY=$strategy MESSAGE=\"$error_message\"" >> "$error_log"
}

# Determine rollback action based on error code
get_rollback_action() {
    local error_code=$1

    case $error_code in
        $ERROR_CODE_TEST_FAILURE)
            echo "BLOCK"
            ;;
        $ERROR_CODE_BUILD_FAILURE)
            echo "ROLLBACK_LAST_GOOD"
            ;;
        $ERROR_CODE_DEPLOY_FAILURE)
            echo "IMMEDIATE_ROLLBACK"
            ;;
        $ERROR_CODE_VALIDATION_FAILURE)
            echo "CONDITIONAL_ROLLBACK"
            ;;
        *)
            echo "MANUAL_INTERVENTION"
            ;;
    esac
}

# Check if error code requires immediate action
is_critical_error() {
    local error_code=$1

    case $error_code in
        $ERROR_CODE_DEPLOY_FAILURE|$ERROR_CODE_VALIDATION_FAILURE)
            return 0  # Critical
            ;;
        *)
            return 1  # Not critical
            ;;
    esac
}

# Handle error with appropriate strategy
handle_classified_error() {
    local error_code=$1
    local error_message="$2"
    local deployment_url="$3"

    log_classified_error "$error_code" "$error_message"

    local action=$(get_rollback_action "$error_code")

    case $action in
        "BLOCK")
            echo "BLOCKING deployment due to test failures"
            return $ERROR_CODE_TEST_FAILURE
            ;;
        "ROLLBACK_LAST_GOOD")
            echo "TRIGGERING rollback to last known good deployment"
            if command -v ./scripts/emergency-rollback.sh >/dev/null; then
                ./scripts/emergency-rollback.sh quick
            fi
            return $ERROR_CODE_BUILD_FAILURE
            ;;
        "IMMEDIATE_ROLLBACK")
            echo "TRIGGERING immediate rollback due to deployment failure"
            if command -v ./scripts/emergency-rollback.sh >/dev/null; then
                ./scripts/emergency-rollback.sh quick --validate-url "$deployment_url"
            fi
            return $ERROR_CODE_DEPLOY_FAILURE
            ;;
        "CONDITIONAL_ROLLBACK")
            echo "EVALUATING conditional rollback for validation failure"
            # Check if this is a transient failure
            if [ -n "$deployment_url" ]; then
                echo "Attempting retry validation before rollback"
                # Could implement retry logic here
            fi
            return $ERROR_CODE_VALIDATION_FAILURE
            ;;
        *)
            echo "REQUIRING manual intervention for error code: $error_code"
            return 99
            ;;
    esac
}

# Display error code reference
show_error_codes() {
    echo "CA Lobby Deployment Error Codes:"
    echo ""
    echo "Code | Strategy              | Description"
    echo "-----|----------------------|----------------------------------"
    echo "  1  | BLOCK_DEPLOYMENT     | Test failures"
    echo "  2  | ROLLBACK_LAST_GOOD   | Build failures"
    echo "  3  | IMMEDIATE_ROLLBACK   | Deployment failures"
    echo "  4  | CONDITIONAL_ROLLBACK | Validation failures"
    echo ""
    echo "Usage examples:"
    echo "  log_classified_error 1 \"Backend tests failed\""
    echo "  handle_classified_error 3 \"Vercel deployment failed\" \"https://example.com\""
    echo "  get_rollback_action 2"
}

# If script is run directly, show help
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        show_error_codes
    else
        echo "Error code classification system loaded."
        echo "Use --help to see error codes reference."
        echo "Source this script to use error handling functions."
    fi
fi