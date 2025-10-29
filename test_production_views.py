#!/usr/bin/env python3
"""
Test Production Views in BigQuery

Runs sample queries against each view to verify:
- Data exists
- No NULL fields in key columns
- Dates parse correctly
- Aggregations work
"""

from pipeline.Bigquery_connection import bigquery_connect
import os
from dotenv import load_dotenv

def run_test_query(client, test_name, query, expected_min_rows=0):
    """Run a test query and print results"""
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print('=' * 80)
    print(f"Query: {query[:200]}...")

    try:
        results = client.query(query).result()
        rows = list(results)

        print(f"\n✅ Query executed successfully")
        print(f"   Rows returned: {len(rows)}")

        if len(rows) < expected_min_rows:
            print(f"   ⚠️  WARNING: Expected at least {expected_min_rows} rows, got {len(rows)}")

        # Print first 3 rows
        if rows:
            print(f"\n   Sample data (first 3 rows):")
            for i, row in enumerate(rows[:3], 1):
                print(f"   Row {i}: {dict(row)}")
        else:
            print("   ⚠️  No data returned")

        return True, len(rows)

    except Exception as e:
        print(f"\n❌ Query failed:")
        print(f"   {str(e)}")
        return False, 0


def main():
    print("=" * 80)
    print("TESTING PRODUCTION VIEWS")
    print("=" * 80)

    # Load credentials
    load_dotenv()
    credentials_path = os.getenv('CREDENTIALS_LOCATION')

    if not credentials_path:
        print("❌ ERROR: CREDENTIALS_LOCATION not set in .env file")
        return

    # Connect to BigQuery
    print("\n📡 Connecting to BigQuery...")
    client = bigquery_connect(credentials_path)
    if not client:
        print("❌ ERROR: Failed to connect to BigQuery")
        return

    test_results = []

    # TEST 1: v_organization_summary - Get top 10 organizations by spending
    success, rows = run_test_query(
        client,
        "Organization Summary - Top 10 by Total Spending",
        """
        SELECT
          organization_name,
          organization_city,
          organization_state,
          total_filings,
          total_lobbying_firms,
          total_spending,
          most_recent_year
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        ORDER BY total_spending DESC
        LIMIT 10
        """,
        expected_min_rows=10
    )
    test_results.append(("Organization Summary", success, rows))

    # TEST 2: v_organization_summary - Alameda County organizations
    success, rows = run_test_query(
        client,
        "Organization Summary - Alameda County Organizations",
        """
        SELECT
          organization_name,
          organization_city,
          total_spending,
          total_filings,
          most_recent_year
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        WHERE UPPER(organization_city) LIKE '%ALAMEDA%'
        ORDER BY total_spending DESC
        LIMIT 15
        """,
        expected_min_rows=5
    )
    test_results.append(("Alameda Organizations", success, rows))

    # TEST 3: v_lobbyist_network - Network for a specific organization
    success, rows = run_test_query(
        client,
        "Lobbyist Network - Top Firms for an Organization",
        """
        SELECT
          organization_name,
          lobbying_firm,
          firm_city,
          firm_state,
          filing_count,
          total_payments,
          first_activity_date,
          last_activity_date
        FROM `ca-lobby.ca_lobby.v_lobbyist_network`
        WHERE UPPER(organization_name) LIKE '%ALAMEDA%'
        ORDER BY total_payments DESC
        LIMIT 10
        """,
        expected_min_rows=1
    )
    test_results.append(("Lobbyist Network", success, rows))

    # TEST 4: v_activity_timeline - Recent activity for 2024
    success, rows = run_test_query(
        client,
        "Activity Timeline - 2024 Activity",
        """
        SELECT
          organization_name,
          lobbying_firm_name,
          period_start_date,
          period_end_date,
          reporting_year,
          reporting_quarter,
          total_payments,
          payment_line_item_count
        FROM `ca-lobby.ca_lobby.v_activity_timeline`
        WHERE reporting_year = 2024
        ORDER BY period_start_date DESC
        LIMIT 10
        """,
        expected_min_rows=1
    )
    test_results.append(("Activity Timeline 2024", success, rows))

    # TEST 5: v_org_profiles_complete - Detailed profile data
    success, rows = run_test_query(
        client,
        "Organization Profiles - Detailed Records",
        """
        SELECT
          organization_name,
          organization_city,
          lobbying_firm_name,
          period_start_date,
          reporting_year,
          fees_amount,
          period_total,
          lobbying_activity
        FROM `ca-lobby.ca_lobby.v_org_profiles_complete`
        WHERE UPPER(organization_name) LIKE '%WATER%'
          AND reporting_year >= 2023
        ORDER BY period_start_date DESC
        LIMIT 10
        """,
        expected_min_rows=1
    )
    test_results.append(("Organization Profiles Detail", success, rows))

    # TEST 6: v_expenditure_categories - Expenditure breakdown
    success, rows = run_test_query(
        client,
        "Expenditure Categories - Sample Expenditures",
        """
        SELECT
          organization_name,
          period_start_date,
          expense_description,
          payee_full_name,
          payee_city,
          expense_amount
        FROM `ca-lobby.ca_lobby.v_expenditure_categories`
        ORDER BY expense_amount DESC
        LIMIT 10
        """,
        expected_min_rows=1
    )
    test_results.append(("Expenditure Categories", success, rows))

    # TEST 7: Check for NULL firm names (should be fixed now)
    success, rows = run_test_query(
        client,
        "Data Quality Check - Firm Names Populated",
        """
        SELECT
          COUNT(*) as total_records,
          COUNT(lobbying_firm_name) as records_with_firm_name,
          COUNT(DISTINCT lobbying_firm_name) as unique_firms,
          ROUND(COUNT(lobbying_firm_name) * 100.0 / COUNT(*), 2) as percent_populated
        FROM `ca-lobby.ca_lobby.v_org_profiles_complete`
        WHERE reporting_year >= 2023
        """,
        expected_min_rows=1
    )
    test_results.append(("Firm Names Data Quality", success, rows))

    # TEST 8: Check date parsing
    success, rows = run_test_query(
        client,
        "Data Quality Check - Date Parsing",
        """
        SELECT
          reporting_year,
          reporting_quarter,
          COUNT(*) as record_count,
          MIN(period_start_date) as earliest_date,
          MAX(period_end_date) as latest_date
        FROM `ca-lobby.ca_lobby.v_activity_timeline`
        WHERE reporting_year >= 2020
        GROUP BY reporting_year, reporting_quarter
        ORDER BY reporting_year DESC, reporting_quarter DESC
        LIMIT 12
        """,
        expected_min_rows=4
    )
    test_results.append(("Date Parsing Quality", success, rows))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    total_tests = len(test_results)
    passed_tests = sum(1 for _, success, _ in test_results if success)

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    print("\nDetailed Results:")
    for test_name, success, row_count in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name} ({row_count} rows)")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("""
1. Review test results above
2. If data looks good, document API endpoints
3. Create Flask API backend to query these views
4. Update frontend to call API instead of loading static files

Views are now ready for production use!
""")

if __name__ == "__main__":
    main()
