"""
Test Script for AI Prediction System
Run this to verify your setup is working correctly
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_SCHEDULE_ID = "SCH001"  # Replace with actual schedule ID from your database
TEST_ROUTE_ID = "R01"        # Replace with actual route ID
TEST_TRAIN_ID = "T001"       # Replace with actual train ID

def test_ollama_health():
    """Test 1: Check if Ollama is running"""
    print("\n🧪 TEST 1: Checking Ollama Health")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/health", timeout=5)
        data = response.json()
        
        if data["is_running"]:
            print("✅ PASS: Ollama is running")
            print(f"   Model: {data['current_model']}")
            print(f"   Available models: {', '.join(data['models'])}")
            return True
        else:
            print("❌ FAIL: Ollama is not running")
            print("   Action: Run 'ollama serve' in a terminal")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to backend API")
        print(f"   Action: Start your backend server (python run_server.py)")
        return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_prediction_generation():
    """Test 2: Generate a prediction"""
    print("\n🧪 TEST 2: Generating AI Prediction")
    print("-" * 50)
    
    target_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    try:
        print(f"   Requesting prediction for:")
        print(f"   - Schedule: {TEST_SCHEDULE_ID}")
        print(f"   - Date: {target_date}")
        print(f"   - Train: {TEST_TRAIN_ID}")
        print(f"\n   ⏳ Please wait... (AI is analyzing ~30-60 seconds)")
        
        response = requests.post(
            f"{API_BASE_URL}/api/ai/predict",
            json={
                "schedule_id": TEST_SCHEDULE_ID,
                "route_id": TEST_ROUTE_ID,
                "train_id": TEST_TRAIN_ID,
                "target_date": target_date
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ PASS: Prediction generated successfully!")
            print("\n📊 RESULTS:")
            print(f"   First Class:  {data['predicted_first_class']} compartments")
            print(f"   Second Class: {data['predicted_second_class']} compartments")
            print(f"   Third Class:  {data['predicted_third_class']} compartments")
            print(f"   Total:        {data['total_compartments']} compartments")
            print(f"   Confidence:   {data.get('confidence_score', 0):.1%}")
            print(f"\n   Reasoning:")
            reasoning = data.get('reasoning', 'No reasoning provided')
            # Print first 200 characters
            print(f"   {reasoning[:200]}...")
            
            return True
        else:
            print(f"❌ FAIL: API returned status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ FAIL: Request timed out")
        print("   Possible causes:")
        print("   - Ollama is still loading the model (first time is slow)")
        print("   - No historical data in database")
        print("   - Schedule/Train IDs don't exist")
        return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_retrieve_predictions():
    """Test 3: Retrieve saved predictions"""
    print("\n🧪 TEST 3: Retrieving Saved Predictions")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/ai/predictions/{TEST_SCHEDULE_ID}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get("total", 0)
            
            if count > 0:
                print(f"✅ PASS: Found {count} predictions for {TEST_SCHEDULE_ID}")
                
                # Show latest prediction
                latest = data["predictions"][0]
                print(f"\n   Latest Prediction:")
                print(f"   - Date: {latest['schedule_date']}")
                print(f"   - Allocation: {latest['predicted_first_class']}/"
                      f"{latest['predicted_second_class']}/"
                      f"{latest['predicted_third_class']}")
                print(f"   - Confidence: {latest.get('confidence_score', 0):.1%}")
                
                return True
            else:
                print(f"⚠️  WARNING: No predictions found for {TEST_SCHEDULE_ID}")
                print("   This is normal if you just ran Test 2 for the first time")
                return True
        else:
            print(f"❌ FAIL: API returned status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_logs():
    """Test 4: Check prediction logs"""
    print("\n🧪 TEST 4: Checking Prediction Logs")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/ai/logs?limit=5", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            
            if logs:
                success_count = sum(1 for log in logs if log["success"])
                print(f"✅ PASS: Found {len(logs)} recent logs")
                print(f"   - Successful: {success_count}")
                print(f"   - Failed: {len(logs) - success_count}")
                
                # Show latest log
                latest = logs[0]
                status = "✅ SUCCESS" if latest["success"] else "❌ FAILED"
                print(f"\n   Latest attempt: {status}")
                print(f"   - Schedule: {latest.get('schedule_id', 'N/A')}")
                print(f"   - Time: {latest.get('execution_time_ms', 0)}ms")
                
                return True
            else:
                print("⚠️  WARNING: No logs found (this is normal for first run)")
                return True
        else:
            print(f"❌ FAIL: API returned status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 AI PREDICTION SYSTEM - TEST SUITE")
    print("=" * 50)
    print("\nℹ️  Make sure:")
    print("   1. Ollama is running (ollama serve)")
    print("   2. Backend server is running (python run_server.py)")
    print("   3. Database has historical data")
    print("   4. Update TEST_SCHEDULE_ID, TEST_ROUTE_ID, TEST_TRAIN_ID above")
    
    # Run tests
    results = []
    
    results.append(("Ollama Health", test_ollama_health()))
    
    if results[0][1]:  # Only continue if Ollama is running
        results.append(("Generate Prediction", test_prediction_generation()))
        results.append(("Retrieve Predictions", test_retrieve_predictions()))
        results.append(("Check Logs", test_logs()))
    else:
        print("\n⚠️  Skipping remaining tests (Ollama not available)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your AI system is working correctly!")
        print("\n📚 Next steps:")
        print("   - Try the frontend UI (if implemented)")
        print("   - Generate predictions for more schedules")
        print("   - Monitor accuracy over time")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\n📚 Troubleshooting:")
        print("   - See AI_SETUP_GUIDE.md")
        print("   - Check backend logs")
        print("   - Verify database has data")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
