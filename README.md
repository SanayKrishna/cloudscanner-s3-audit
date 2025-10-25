# CloudScanner S3 Audit

A Python-based tool to scan AWS S3 buckets for misconfigurations, generate reports, and provide an interactive dashboard for monitoring bucket security.

## Features

- Scan all S3 buckets in your AWS account for:
  - Public access
  - Versioning disabled
  - Unencrypted buckets
- Generate static HTML reports
- Interactive Flask dashboard to view bucket stats and details
- Filter buckets by type and search by name
- Responsive design with clean, modern UI

## Project Structure

```
CloudScanner/
├── app.py                  # Flask application for interactive dashboard
├── report.py               # Generates static HTML report
├── requirements.txt        # Python dependencies
├── utils/
│   └── s3_scanner.py       # Core S3 scanning logic
├── templates/
│   └── dashboard.html      # Flask dashboard template
└── reports/
    └── template.html       # HTML template for static report
```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/SanayKrishna/cloudscanner-s3-audit.git
cd cloudscanner-s3-audit
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

3. Configure AWS CLI with your credentials:

```bash
aws configure
```

## Usage

### Static Report

```bash
python report.py
```

The report will be generated in `reports/s3_report.html`.

### Interactive Dashboard

```bash
python app.py
```

Open your browser at `http://127.0.0.1:5000` to access the dashboard.

## Contributing

Contributions are welcome! Please create a feature branch and submit a pull request with detailed description.

## License

This project is licensed under the MIT License.
