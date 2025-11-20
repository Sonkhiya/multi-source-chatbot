#!/usr/bin/env python

import httpx
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

async def test_health():
    print("\n=== Testing Health Check ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


async def test_ingest_document():
    print("\n=== Testing Document Ingestion ===")
    sample_doc = Path("examples/sample_document.txt")
    if not sample_doc.exists():
        print("Sample document not found. Skipping.")
        return None
    
    async with httpx.AsyncClient(timeout=60) as client:
        with open(sample_doc, "rb") as f:
            files = {"file": ("sample_document.txt", f)}
            response = await client.post(f"{BASE_URL}/ingest/document", files=files)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        return result.get("document_id")


async def test_ingest_webpage():
    print("\n=== Testing Webpage Ingestion ===")
    async with httpx.AsyncClient(timeout=60) as client:
        payload = {
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "title": "Python Programming Language"
        }
        response = await client.post(
            f"{BASE_URL}/ingest/webpage",
            json=payload
        )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    return result.get("webpage_id")


async def test_ingest_record():
    print("\n=== Testing Record Ingestion ===")
    async with httpx.AsyncClient() as client:
        payload = {
            "record_id": "emp-001",
            "data": {
                "name": "Alice Johnson",
                "role": "Senior Engineer",
                "department": "Backend",
                "skills": ["Python", "Go", "Kubernetes", "AWS"],
                "years_experience": 8,
                "certifications": ["AWS Solutions Architect", "Kubernetes Admin"]
            },
            "context": "Employee profile from company database"
        }
        response = await client.post(
            f"{BASE_URL}/ingest/record",
            json=payload
        )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))


async def test_query():
    print("\n=== Testing Query ===")
    queries = [
        "What skills are mentioned in the records?",
        "Tell me about Python programming",
        "Who are the senior engineers?"
    ]
    
    async with httpx.AsyncClient(timeout=60) as client:
        for query in queries:
            print(f"\nQuery: {query}")
            payload = {"question": query, "retrieve_top_k": 3}
            response = await client.post(
                f"{BASE_URL}/query",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Answer: {result['answer'][:200]}...")
                print(f"Confidence: {result['confidence_score']:.2%}")
                print(f"References: {len(result['references'])}")
                print(f"Response time: {result['response_time_ms']:.1f}ms")
            else:
                print(f"Error: {response.status_code}")


async def test_stats():
    print("\n=== Testing Stats ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/stats")
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


async def run_all_tests():
    print("Starting API Tests...")
    
    try:
        await test_health()
        
        await test_ingest_record()
        time.sleep(2)
        
        await test_ingest_webpage()
        time.sleep(2)
        
        await test_ingest_document()
        time.sleep(2)
        
        await test_query()
        
        await test_stats()
        
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"❌ Error during tests: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_all_tests())
