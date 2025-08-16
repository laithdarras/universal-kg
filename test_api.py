import requests
import json
import os

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing Universal Knowledge Graph API...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Server is running: {response.json()}")
    except Exception as e:
        print(f"✗ Server not running: {e}")
        return
    
    # Test 2: Test ingest endpoint with a sample URL
    print("\n2. Testing ingest endpoint...")
    try:
        ingest_data = {
            "urls": [
                "https://en.wikipedia.org/wiki/Artificial_intelligence"
            ]
        }
        response = requests.post(f"{BASE_URL}/api/ingest", json=ingest_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Ingest successful: {len(result['nodes'])} nodes, {len(result['edges'])} edges")
        else:
            print(f"✗ Ingest failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Ingest error: {e}")
    
    # Test 3: Test graph endpoint
    print("\n3. Testing graph endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/graph")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Graph retrieved: {len(result['nodes'])} nodes, {len(result['edges'])} edges")
        else:
            print(f"✗ Graph retrieval failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Graph error: {e}")
    
    # Test 4: Test QA endpoint
    print("\n4. Testing QA endpoint...")
    try:
        qa_data = {
            "question": "What is artificial intelligence?"
        }
        response = requests.post(f"{BASE_URL}/api/qa", json=qa_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ QA successful: {result['answer']}")
            print(f"  Cited nodes: {result['cited_nodes']}")
            print(f"  Cited edges: {result['cited_edges']}")
        else:
            print(f"✗ QA failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ QA error: {e}")
    
    # Test 5: Test OpenAI integration (if API key is present)
    print("\n5. Testing OpenAI integration...")
    if os.getenv("OPENAI_API_KEY"):
        try:
            # Test with a simple, known text
            test_text = "Artificial intelligence is a field of computer science. AI systems can learn from data. Machine learning is a subset of AI."
            test_url = "https://test.example.com"
            
            # Create a simple test by ingesting a known text
            test_data = {
                "urls": [test_url]
            }
            
            # This will test the OpenAI extraction if the key is present
            response = requests.post(f"{BASE_URL}/api/ingest", json=test_data)
            if response.status_code == 200:
                result = response.json()
                if len(result['edges']) > 0:
                    print(f"✓ OpenAI extraction working: {len(result['edges'])} triples extracted")
                    # Show some example triples
                    for edge in result['edges'][:3]:
                        print(f"  Triple: {edge['source']} --{edge['relation']}--> {edge['target']}")
                else:
                    print("⚠ OpenAI extraction returned no triples (may be fallback mode)")
            else:
                print(f"✗ OpenAI test failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"✗ OpenAI test error: {e}")
    else:
        print("⚠ Skipping OpenAI test - no OPENAI_API_KEY found in environment")

if __name__ == "__main__":
    test_api()
