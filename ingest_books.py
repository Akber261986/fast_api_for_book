#!/usr/bin/env python3
"""
Script to ingest book content from docs folder into Qdrant database
"""
import os
import requests
import time
from pathlib import Path


def find_markdown_files(docs_dir="docs"):
    """Find all markdown files in the docs directory"""
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.lower().endswith('.md'):
                full_path = os.path.abspath(os.path.join(root, file))
                md_files.append(full_path)
    return md_files


def process_markdown_files(files, base_url="http://localhost:8000"):
    """Send markdown files to the API for processing"""
    print(f"Found {len(files)} markdown files to process:")
    for i, file in enumerate(files):
        print(f"  {i+1}. {file}")

    if not files:
        print("No markdown files found in the docs directory!")
        return False

    print(f"\nSending request to {base_url}/api/v1/embeddings/process-markdown...")

    try:
        # Send the request with source_files as query parameters
        # The API expects source_files as a query parameter (List[str])
        # We'll send each file as a separate query parameter with the same name
        params = {
            "rebuild_collection": False  # Set to True if you want to clear existing content
        }

        # Create the URL with query parameters for each source file
        # For multiple source files, we'll build the URL manually
        import urllib.parse

        # Build the full URL with all source files as query parameters
        # We need to construct the query string manually to handle multiple values for the same parameter
        query_parts = []
        for file in files:
            query_parts.append(f"source_files={urllib.parse.quote(str(file))}")

        query_parts.append(f"rebuild_collection={str(params['rebuild_collection']).lower()}")

        base_url_with_params = f"{base_url}/api/v1/embeddings/process-markdown"
        full_url = f"{base_url_with_params}?{'&'.join(query_parts)}"

        # For this endpoint, we don't need a JSON body, just the query parameters in the URL
        response = requests.post(
            full_url,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minute timeout for processing
        )

        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"\nSUCCESS! Ingestion job started successfully!")
            print(f"Job ID: {job_id}")
            print(f"Status: {result.get('status')}")
            print(f"Total files: {result.get('total_files')}")

            # Poll for job completion
            return monitor_job_status(job_id, base_url)
        else:
            print(f"ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed: {str(e)}")
        return False


def monitor_job_status(job_id, base_url="http://localhost:8000"):
    """Monitor the job status until completion"""
    print(f"\nMonitoring job {job_id}...")

    while True:
        try:
            response = requests.get(f"{base_url}/api/v1/embeddings/job/{job_id}")

            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status", "unknown")
                progress = status_data.get("progress", 0)
                total = status_data.get("total", 0)

                if total > 0:
                    percentage = progress/total*100
                    print(f"   Status: {status} | Progress: {progress}/{total} ({percentage:.1f}%)")
                else:
                    print(f"   Status: {status} | Progress: {progress}/{total}")

                if status == "completed":
                    print("SUCCESS! Job completed!")
                    return True
                elif status == "failed":
                    print("ERROR! Job failed!")
                    return False
                elif status in ["pending", "processing"]:
                    time.sleep(2)  # Wait 2 seconds before checking again
                else:
                    print(f"Unexpected status: {status}")
                    return False
            else:
                print(f"ERROR checking job status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"ERROR monitoring job: {str(e)}")
            return False
        except ZeroDivisionError:
            # Handle case where total is 0
            time.sleep(2)


def test_search(base_url="http://localhost:8000"):
    """Test search functionality after ingestion"""
    print(f"\nTesting search functionality...")

    try:
        response = requests.post(
            f"{base_url}/api/v1/search/query",
            json={
                "query_text": "What is AI?",
                "top_k": 3,
                "similarity_threshold": 0.5
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            results = response.json()
            print("SUCCESS! Search test completed.")
            print(f"Found {results.get('total_results', 0)} results")

            if 'results' in results and results['results']:
                print("\nSample results:")
                for i, result in enumerate(results['results'][:2]):  # Show first 2 results
                    content = result.get('content', {})
                    print(f"  {i+1}. File: {content.get('source_file', 'Unknown')}")
                    print(f"     Text preview: {content.get('text', '')[:100]}...")
                    print(f"     Similarity: {result.get('similarity_score', 0):.3f}")
        else:
            print(f"Search test failed: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Search test failed: {str(e)}")


def main():
    """Main function to process all markdown files in docs folder"""
    print("Book Content Ingestion Script")
    print("=" * 30)

    # Check if the docs directory exists
    if not os.path.exists("docs"):
        print("ERROR: 'docs' directory not found!")
        print("Please make sure your markdown files are in a 'docs' folder")
        return

    # Find all markdown files
    md_files = find_markdown_files("docs")

    if not md_files:
        print("ERROR: No markdown files found in the 'docs' directory!")
        print("Supported extensions: .md, .MD")
        return

    print(f"Found {len(md_files)} markdown files")

    # Show a preview of files to be processed
    print("\nFiles to be processed:")
    for i, file in enumerate(md_files[:5]):  # Show first 5 files
        rel_path = os.path.relpath(file, os.getcwd())
        print(f"  {i+1}. {rel_path}")

    if len(md_files) > 5:
        print(f"  ... and {len(md_files) - 5} more files")

    print(f"\nAutomatically proceeding with ingesting {len(md_files)} files...")

    # Process the files
    success = process_markdown_files(md_files)

    if success:
        print("\nIngestion completed successfully!")
        print("\nYou can now search your book content using:")
        print("- The API: POST to /api/v1/search/query")
        print("- The chat interface: POST to /api/v1/agents/chat")

        # Test search functionality
        test_search()
    else:
        print("\nIngestion failed!")
        print("Check that your FastAPI server is running on http://localhost:8000")


if __name__ == "__main__":
    main()