#!/usr/bin/env python3
"""
Remove Old Views from BigQuery

This script removes views created before October 29, 2025.
Keeps only the 5 new production views created today.
"""

from pipeline.Bigquery_connection import bigquery_connect
import os
from dotenv import load_dotenv

def main():
    print("=" * 80)
    print("REMOVING OLD VIEWS FROM BIGQUERY")
    print("=" * 80)

    load_dotenv()
    credentials_path = os.getenv('CREDENTIALS_LOCATION')

    if not credentials_path:
        print("❌ ERROR: CREDENTIALS_LOCATION not set")
        return

    client = bigquery_connect(credentials_path)
    if not client:
        print("❌ ERROR: Failed to connect to BigQuery")
        return

    # Views to remove (created before Oct 29, 2025)
    old_views = [
        'v_alameda_who_paid_who',
        'v_money_flow_alameda_summary',
        'v_money_flow_expenditures',
        'v_money_flow_payments',
        'v_filers',
        'v_expenditures',
        'v_payments',
        'v_alameda_activity',
        'v_employers',
        'v_attachments',
        'v_other_payments',
        'v_campaign_contributions',
        'v_registrations',
        'v_disclosures',
        'v_alameda_filers',
        'v_test_dates',  # Test view from today
    ]

    # Views to KEEP (created Oct 29, 2025 - production views)
    keep_views = [
        'v_org_profiles_complete',
        'v_lobbyist_network',
        'v_activity_timeline',
        'v_expenditure_categories',
        'v_organization_summary',
    ]

    print("\n📋 Views to KEEP (Production):")
    for view in keep_views:
        print(f"  ✅ {view}")

    print(f"\n🗑️  Views to REMOVE ({len(old_views)} total):")
    for view in old_views:
        print(f"  🗑️  {view}")

    print("\n" + "=" * 80)
    response = input("Do you want to proceed with removal? (yes/no): ")

    if response.lower() not in ['yes', 'y']:
        print("\n⚠️  Removal cancelled by user")
        return

    print("\n🔨 Removing old views...")
    success_count = 0
    failed_views = []

    for view_name in old_views:
        print(f"\nRemoving {view_name}...", end=" ")
        try:
            sql = f"DROP VIEW IF EXISTS `ca-lobby.ca_lobby.{view_name}`"
            client.query(sql).result()
            print("✅")
            success_count += 1
        except Exception as e:
            print(f"❌")
            print(f"   Error: {str(e)[:200]}")
            failed_views.append((view_name, str(e)))

    # Summary
    print("\n" + "=" * 80)
    print("REMOVAL SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successfully removed: {success_count}/{len(old_views)} views")

    if failed_views:
        print(f"\n❌ Failed to remove: {len(failed_views)} views")
        for view_name, error in failed_views:
            print(f"   - {view_name}: {error[:100]}")
    else:
        print("\n🎉 All old views removed successfully!")

    print("\n📋 Remaining views (Production only):")
    query = '''
    SELECT table_name, creation_time
    FROM `ca-lobby.ca_lobby.INFORMATION_SCHEMA.TABLES`
    WHERE table_type = 'VIEW'
    ORDER BY creation_time DESC
    '''
    results = client.query(query).result()
    for row in results:
        print(f"  ✅ {row.table_name} ({row.creation_time})")

if __name__ == "__main__":
    main()
