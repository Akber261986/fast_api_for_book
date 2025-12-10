import asyncio
import os
import requests
from pathlib import Path

async def ingest_docs_book():
    """
    Script to ingest your book content from the docs directory into the deployed API
    """

    # Replace with your deployed API URL
    base_url = "https://fastapiforbook-production.up.railway.app"

    # Find all markdown files in the docs directory
    docs_path = Path("docs")
    markdown_files = list(docs_path.rglob("*.md"))  # This will find all .md files recursively

    print(f"Found {len(markdown_files)} markdown files to process:")
    for file in markdown_files:
        print(f"  - {file}")

    if not markdown_files:
        print("No markdown files found in docs directory!")
        return

    # Since the files are local, we need to host them somewhere public
    # For now, let's create a script that you can use once you host the files
    # Or use the raw GitHub URLs if your repo is public

    # Option 1: If your GitHub repo is public, you can use raw URLs
    # Update these with your actual GitHub information:
    github_username = "akber"  # Replace with your GitHub username if different
    github_repo = "fast_api_for_book"           # Replace with your repo name if different
    github_branch = "main"  # or "master" depending on your default branch

    raw_urls = []
    for file_path in markdown_files:
        # Convert local path to GitHub raw URL
        # e.g., docs/module1/intro_physical_ai.md ->
        # https://raw.githubusercontent.com/username/repo/main/docs/module1/intro_physical_ai.md
        relative_path = str(file_path).replace('\\', '/')  # Convert Windows path separators
        raw_url = f"https://raw.githubusercontent.com/{github_username}/{github_repo}/{github_branch}/{relative_path}"
        raw_urls.append(raw_url)

    print(f"\nGenerated {len(raw_urls)} raw GitHub URLs:")
    for url in raw_urls:
        print(f"  - {url}")

    # Now send the request to your deployed API
    endpoint = f"{base_url}/api/v1/embeddings/process-markdown"

    payload = {
        "source_files": raw_urls,
        "rebuild_collection": True  # This will clear existing content and add new
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"\nSending request to: {endpoint}")
    print("Payload:", payload)

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Content ingestion started successfully!")
            print(f"Job ID: {result.get('job_id')}")
            print(f"Total files: {result.get('total_files')}")
            print(f"Message: {result.get('message')}")

            # Provide instructions for checking status
            print(f"\nTo check job status:")
            print(f"  curl {base_url}/api/v1/embeddings/job/{result.get('job_id')}")
        else:
            print(f"❌ Error ingesting content: {response.text}")

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        print("Make sure:")
        print("  1. Your GitHub repo is public")
        print("  2. The file paths in the URLs are correct")
        print("  3. Your deployed API is running and accessible")

def list_docs_files():
    """
    Simple function to list all the markdown files in your docs directory
    """
    docs_path = Path("docs")
    markdown_files = list(docs_path.rglob("*.md"))

    print("Book content files found in docs/:")
    for file in markdown_files:
        print(f"  - {file}")

    return markdown_files

if __name__ == "__main__":
    print("Listing all book content files...")
    files = list_docs_files()
    print(f"\nTotal files found: {len(files)}")

    print("\n" + "="*50)
    print("Generated GitHub Raw URLs for your book content:")

    # Generate the URLs to show them
    github_username = "akber"
    github_repo = "fast_api_for_book"
    github_branch = "main"

    raw_urls = []
    for file_path in files:
        relative_path = str(file_path).replace('\\', '/')  # Convert Windows path separators
        raw_url = f"https://raw.githubusercontent.com/{github_username}/{github_repo}/{github_branch}/{relative_path}"
        raw_urls.append(raw_url)

    for url in raw_urls:
        print(f"  - {url}")

    print("\nTo ingest your book content:")
    print("1. Make sure your GitHub repository is public")
    print("2. Update the github_username and github_repo variables in the script if needed")
    print("3. Run this script: python ingest_docs_book.py")
    print("="*50)