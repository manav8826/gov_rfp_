import requests
import time
import os

# Create a dummy PDF if none exists
if not os.path.exists("sample_rfp.pdf"):
    with open("sample_rfp.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 R obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 R obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000114 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n213\n%%EOF")
    print("Created dummy sample_rfp.pdf")

url = "http://127.0.0.1:8000/api/v1"

print(f"Uploading PDF to {url}/rfp/upload...")
with open("sample_rfp.pdf", "rb") as f:
    files = {"file": ("sample_rfp.pdf", f, "application/pdf")}
    resp = requests.post(f"{url}/rfp/upload", files=files)

if resp.status_code != 200:
    print(f"Upload Failed: {resp.text}")
    exit(1)

data = resp.json()
job_id = data["job_id"]
print(f"Job ID: {job_id}")

print("Polling for status...")
while True:
    status_resp = requests.get(f"{url}/rfp/{job_id}/status")
    status = status_resp.json()
    print(f"Status: {status['status']} ({status['progress']}%)")
    
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(2)

print("Fetching Result...")
result_resp = requests.get(f"{url}/rfp/{job_id}/result")
if result_resp.status_code == 200:
    print("Result:", result_resp.json())
else:
    print("Result Error:", result_resp.text)
