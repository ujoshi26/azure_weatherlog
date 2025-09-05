Features:
Scheduled execution: Runs every hour using cron syntax
Manual trigger: Can be triggered manually via GitHub's workflow dispatch
Comprehensive data: Captures temperature, humidity, pressure, wind, and weather description
Error handling: Includes proper logging and error handling
Timestamped files: Each record is stored with a unique timestamp-based filename
JSON format: Data is stored in a structured JSON format for easy processing

File Structure:
The temperature data will be stored in Azure Blob Storage with this structure:
temperature/
├── 2024-03-15T14-00-00-123456Z.json
├── 2024-03-15T15-00-00-789012Z.json
└── ...
Each JSON file contains detailed weather information including temperature, humidity, pressure, wind conditions, and more. The action will run reliably every hour and store historical temperature data for analysis.
