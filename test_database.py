#!/usr/bin/env python3
"""
🧪 Database Connection Test Script
Quick test to verify Supabase connection and setup
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.supabase_client import supabase_client
    from app.utils.logger import app_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the project root directory and venv is activated")
    sys.exit(1)


def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")

    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_KEY']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask sensitive data
            if 'KEY' in var:
                masked = value[:10] + '...' + value[-10:]
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")

    if missing_vars:
        print(f"   ❌ Missing variables: {', '.join(missing_vars)}")
        return False

    return True


def test_basic_connection():
    """Test basic database connection"""
    print("\n🔗 Testing Database Connection...")

    try:
        # Simple query to test connection
        result = supabase_client.execute_query("SELECT 1 as test", fetch=True)
        if result and len(result) > 0:
            print("   ✅ Basic connection successful")
            return True
        else:
            print("   ❌ Connection failed - no result")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False


def test_tables_exist():
    """Test if required tables exist"""
    print("\n📋 Testing Tables...")

    required_tables = ['sales_data', 'forecasts', 'csv_upload_logs', 'api_usage_stats']

    try:
        # Check if tables exist
        query = """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
            AND tablename IN ('sales_data', 'forecasts', 'csv_upload_logs', 'api_usage_stats')
        ORDER BY tablename;
        """

        result = supabase_client.execute_query(query, fetch=True)

        if result:
            existing_tables = [row[0] for row in result]

            for table in required_tables:
                if table in existing_tables:
                    print(f"   ✅ Table '{table}' exists")
                else:
                    print(f"   ❌ Table '{table}' missing")

            return len(existing_tables) == len(required_tables)
        else:
            print("   ❌ Could not retrieve table list")
            return False

    except Exception as e:
        print(f"   ❌ Error checking tables: {e}")
        return False


def test_sample_data():
    """Test if sample data exists"""
    print("\n📊 Testing Sample Data...")

    try:
        # Check sample data
        query = "SELECT COUNT(*) FROM sales_data;"
        result = supabase_client.execute_query(query, fetch=True)

        if result and result[0][0] > 0:
            count = result[0][0]
            print(f"   ✅ Sample data found: {count} records in sales_data")

            # Get a sample record
            query = "SELECT sku_id, date, units_sold, revenue FROM sales_data LIMIT 1;"
            sample = supabase_client.execute_query(query, fetch=True)

            if sample:
                record = sample[0]
                print(f"   📝 Sample record: SKU={record[0]}, Date={record[1]}, Units={record[2]}, Revenue={record[3]}")

            return True
        else:
            print("   ⚠️  No sample data found (this is optional)")
            return True

    except Exception as e:
        print(f"   ❌ Error checking sample data: {e}")
        return False


def test_permissions():
    """Test database permissions"""
    print("\n🔐 Testing Permissions...")

    try:
        # Test insert permission
        test_data = {
            'sku_id': 'TEST_SKU_001',
            'date': datetime.now().date(),
            'units_sold': 1,
            'revenue': 100.0,
            'price': 100.0
        }

        # Try to insert test data
        insert_result = supabase_client.insert_sales_data([test_data])

        if insert_result > 0:
            print("   ✅ Insert permission working")

            # Clean up test data
            cleanup_query = "DELETE FROM sales_data WHERE sku_id = 'TEST_SKU_001';"
            supabase_client.execute_query(cleanup_query)
            print("   🧹 Test data cleaned up")

            return True
        else:
            print("   ❌ Insert permission failed")
            return False

    except Exception as e:
        print(f"   ❌ Permission test failed: {e}")
        return False


def test_views():
    """Test if views are working"""
    print("\n👁️  Testing Views...")

    try:
        # Test sales_analytics view
        query = "SELECT COUNT(*) FROM sales_analytics;"
        result = supabase_client.execute_query(query, fetch=True)

        if result:
            print("   ✅ sales_analytics view working")

            # Test recent_forecasts view
            query = "SELECT COUNT(*) FROM recent_forecasts;"
            result = supabase_client.execute_query(query, fetch=True)

            if result is not None:  # Can be 0 if no forecasts yet
                print("   ✅ recent_forecasts view working")
                return True
            else:
                print("   ❌ recent_forecasts view failed")
                return False
        else:
            print("   ❌ sales_analytics view failed")
            return False

    except Exception as e:
        print(f"   ❌ Views test failed: {e}")
        return False


def main():
    """Run all database tests"""
    print("🧪 Khabarovsk Forecast Buddy - Database Test")
    print("=" * 50)

    tests = [
        ("Environment Variables", test_environment),
        ("Database Connection", test_basic_connection),
        ("Tables Existence", test_tables_exist),
        ("Sample Data", test_sample_data),
        ("Permissions", test_permissions),
        ("Views", test_views)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n💡 '{test_name}' failed - check SUPABASE_SETUP.md for help")
        except Exception as e:
            print(f"\n❌ '{test_name}' crashed: {e}")

    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Database is ready!")
        print("\n📍 Next steps:")
        print("   1. Start the development server: ./start-dev.sh")
        print("   2. Test API: curl http://localhost:8000/api/v1/health")
        print("   3. Open frontend: http://localhost:8080")
        return True
    else:
        print("❌ Some tests failed. Please check:")
        print("   1. SUPABASE_SETUP.md for setup instructions")
        print("   2. Your .env file configuration")
        print("   3. Supabase project status")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
