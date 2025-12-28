#!/usr/bin/env python3
"""
Test script to verify the recipient queries return data
"""

import sys
import os

# Add api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from utils.bigquery_client import BigQueryClient

def test_city_recipients():
    """Test the city recipients query"""
    query = """
    WITH city_payments AS (
        SELECT
            d.FILING_ID,
            d.RPT_DATE_DATE,
            pay.PAYEE_NAML as recipient_name,
            CAST(pay.PER_TOTAL AS FLOAT64) as amount
        FROM `ca-lobby.ca_lobby.lpay_cd` pay
        JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
            ON pay.FILING_ID = d.FILING_ID
            AND pay.AMEND_ID = d.AMEND_ID
        WHERE pay.PAYEE_NAML IS NOT NULL
          AND pay.PER_TOTAL IS NOT NULL
          AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
          AND d.RPT_DATE_DATE IS NOT NULL
          AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
          AND (
            UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
            OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
          )
    )
    SELECT
        recipient_name,
        CAST(ROUND(SUM(amount)) AS INT64) as total_amount
    FROM city_payments
    GROUP BY recipient_name
    HAVING total_amount > 0
    ORDER BY total_amount DESC
    LIMIT 10
    """

    print("Testing City Recipients Query...")
    print("=" * 60)

    try:
        client = BigQueryClient()
        result = client.execute_query(query)

        if result:
            print(f"✓ Query returned {len(result)} results")
            print("\nTop 10 Recipients of City Lobbying Money:")
            print("-" * 60)
            for i, row in enumerate(result, 1):
                print(f"{i}. {row['recipient_name']}: ${row['total_amount']:,}")
        else:
            print("✗ Query returned empty results")
            print("\nLet me check if there's ANY city payment data in 2025...")

            # Simpler query to check if data exists
            check_query = """
            SELECT COUNT(*) as count
            FROM `ca-lobby.ca_lobby.lpay_cd` pay
            JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
                ON pay.FILING_ID = d.FILING_ID
            WHERE EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
              AND UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
            """
            count_result = client.execute_query(check_query)
            if count_result:
                print(f"Found {count_result[0]['count']} city payment records in 2025")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_county_recipients():
    """Test the county recipients query"""
    query = """
    WITH county_payments AS (
        SELECT
            d.FILING_ID,
            d.RPT_DATE_DATE,
            pay.PAYEE_NAML as recipient_name,
            CAST(pay.PER_TOTAL AS FLOAT64) as amount
        FROM `ca-lobby.ca_lobby.lpay_cd` pay
        JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
            ON pay.FILING_ID = d.FILING_ID
            AND pay.AMEND_ID = d.AMEND_ID
        WHERE pay.PAYEE_NAML IS NOT NULL
          AND pay.PER_TOTAL IS NOT NULL
          AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
          AND d.RPT_DATE_DATE IS NOT NULL
          AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
          AND (
            UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
            OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
            OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
          )
    )
    SELECT
        recipient_name,
        CAST(ROUND(SUM(amount)) AS INT64) as total_amount
    FROM county_payments
    GROUP BY recipient_name
    HAVING total_amount > 0
    ORDER BY total_amount DESC
    LIMIT 10
    """

    print("\n\nTesting County Recipients Query...")
    print("=" * 60)

    try:
        client = BigQueryClient()
        result = client.execute_query(query)

        if result:
            print(f"✓ Query returned {len(result)} results")
            print("\nTop 10 Recipients of County Lobbying Money:")
            print("-" * 60)
            for i, row in enumerate(result, 1):
                print(f"{i}. {row['recipient_name']}: ${row['total_amount']:,}")
        else:
            print("✗ Query returned empty results")
            print("\nLet me check if there's ANY county payment data in 2025...")

            # Simpler query to check if data exists
            check_query = """
            SELECT COUNT(*) as count
            FROM `ca-lobby.ca_lobby.lpay_cd` pay
            JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
                ON pay.FILING_ID = d.FILING_ID
            WHERE EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
              AND UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
            """
            count_result = client.execute_query(check_query)
            if count_result:
                print(f"Found {count_result[0]['count']} county payment records in 2025")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def explore_lpay_data():
    """Explore LPAY_CD data to understand what's available"""
    print("\n\nExploring LPAY_CD Data...")
    print("=" * 60)

    # Check sample EMPLR_NAML values
    query = """
    SELECT
        pay.EMPLR_NAML,
        COUNT(*) as count,
        SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as total_amount
    FROM `ca-lobby.ca_lobby.lpay_cd` pay
    JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
        ON pay.FILING_ID = d.FILING_ID
    WHERE d.RPT_DATE_DATE IS NOT NULL
      AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
      AND (
        UPPER(pay.EMPLR_NAML) LIKE '%CITY%'
        OR UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
      )
    GROUP BY pay.EMPLR_NAML
    ORDER BY total_amount DESC
    LIMIT 10
    """

    try:
        client = BigQueryClient()
        result = client.execute_query(query)

        if result:
            print(f"✓ Found {len(result)} city/county employers in 2025")
            print("\nTop Employers (Cities/Counties):")
            print("-" * 60)
            for row in result:
                print(f"{row['EMPLR_NAML']}: ${row['total_amount']:,.0f} ({row['count']} payments)")
        else:
            print("✗ No city/county employers found in 2025")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_city_recipients()
    test_county_recipients()
    explore_lpay_data()
