from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from utils.s3_scanner import scan_s3_buckets
import os

# Paths
TEMPLATES_DIR = "reports"
OUTPUT_FILE = os.path.join(TEMPLATES_DIR, "s3_report.html")

# Ensure reports directory exists
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Jinja setup
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
template = env.get_template("template.html")

# Run scan
print("🔍 Scanning S3 buckets...")
scan_results = scan_s3_buckets()

# Extract lists safely
public_buckets = scan_results.get("public_buckets", [])
unencrypted_buckets = scan_results.get("unencrypted_buckets", [])
versioning_disabled = scan_results.get("versioning_disabled", [])

# Compute counts
public_count = len(public_buckets)
unencrypted_count = len(unencrypted_buckets)
versioning_count = len(versioning_disabled)

# Add timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"\n📊 Scan Results:")
print(f"   • Public buckets: {public_count}")
print(f"   • Unencrypted buckets: {unencrypted_count}")
print(f"   • Versioning disabled: {versioning_count}")

# Render template
html_content = template.render(
    public_buckets=public_buckets,
    unencrypted_buckets=unencrypted_buckets,
    versioning_disabled=versioning_disabled,
    public_count=public_count,
    unencrypted_count=unencrypted_count,
    versioning_count=versioning_count,
    generated_time=current_time
)

# Write to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✅ Report generated successfully: {OUTPUT_FILE}")