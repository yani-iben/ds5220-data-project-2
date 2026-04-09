# TfL Network Performance Tracker

A Chalice-based serverless application designed to ingest, process, and visualize London transport data.

## Data Source Summary
**Source:** [TfL Unified API](https://api.tfl.gov.uk/)  
The application consumes real-time data from the Transport for London (TfL) Unified API. This source provides a consolidated stream of data across all modes (Tube, Bus, DLR, Overground, and Cycle Hire). Specifically, this project targets line status, arrival predictions, and station occupancy to monitor network efficiency.

## Scheduled Process
The application implements an **Automated ETL (Extract, Transform, Load) Pipeline** scheduled via AWS Lambda:
1. **Ingestion:** A CloudWatch Event triggers the Lambda function at fixed intervals (e.g., every 15 minutes) to fetch JSON payloads from TfL endpoints.
2. **Processing:** The raw JSON is parsed to extract key metrics (delays, station wait times, or bike availability).
3. **Storage:** Processed data is archived in **Amazon S3** (as CSV/Parquet) and indexed in **DynamoDB** for rapid retrieval and historical trend analysis.

## Output Data & Visualization
### Data Description
The output is a structured time-series dataset. Key columns include:
* `timestamp`: The precise time of the data capture.
* `line_id`: The specific transport line (e.g., Victoria, Central).
* `status_severity`: Numerical representation of service health.
* `occupancy_ratio`: For cycle hire, the percentage of available docks.

### Visualization: Diurnal Usage Profile
The primary output is a **Time-Series Line Plot** representing the "Pulse of London."
* **X-Axis:** 24-hour cycle.
* **Y-Axis:** Service volume or delay minutes.
* **Insight:** The plot clearly visualizes the **M-shaped "Rush Hour" curve**, highlighting the morning (08:00) and evening (17:30) peaks, allowing for comparative analysis of peak-time service reliability.
