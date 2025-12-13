#!/usr/bin/env python3
"""
Test script to verify that the application can be imported without errors.
This helps identify issues that would prevent Railway deployment.
"""

def test_imports():
    """Test importing the main modules without triggering API calls."""
    print("Testing imports...")

    try:
        # Test importing config first
        from app.core.config import settings
        print("[OK] Config imported successfully")

        # Test importing the database module (should not connect immediately now)
        from app.core import database
        print("[OK] Database module imported successfully")

        # Test importing the gemini client (should not connect immediately now)
        from app.core import gemini_client
        print("[OK] Gemini client module imported successfully")

        # Test importing services (should not connect immediately now)
        from app.services import ingestion_service, retrieval_service
        print("[OK] Services imported successfully")

        # Test importing main app (should not connect immediately now)
        from app import main
        print("[OK] Main app imported successfully")

        print("\nAll imports successful! The application should now start without immediate API connections.")
        return True

    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\nThe application should now work with Railway deployment!")
        print("\nNext steps:")
        print("1. Commit all changes: git add . && git commit -m 'Fix lazy loading for all services'")
        print("2. Push to GitHub: git push origin 002-rag-markdown-system")
        print("3. Railway should now be able to deploy without issues")
    else:
        print("\nThere are still import issues to fix.")