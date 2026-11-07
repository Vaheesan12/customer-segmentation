# Customer Segmentation Portfolio Project

A beginner-friendly end-to-end project using **SQL, Python, RFM Analysis, and K-Means clustering**.

## Project objectives
- Analyze historical customer transactions.
- Calculate **Recency, Frequency, and Monetary (RFM)** values.
- Score customers from 1 to 5 for each RFM dimension.
- Create actionable customer segments.
- Use K-Means to create an additional data-driven cluster label.
- Export CSV/Excel reports, charts, and marketing recommendations.

## Folder structure
```text
customer_segmentation_project/
├── data/
│   └── retail_transactions.csv
├── sql/
│   └── schema_and_analysis.sql
├── outputs/                 # Generated after running
├── run_project.py
├── requirements.txt
└── README.md
```

## Dataset columns
| Column | Description |
|---|---|
| transaction_id | Unique transaction reference |
| customer_id | Customer identifier |
| purchase_date | Purchase date (YYYY-MM-DD) |
| quantity | Units purchased |
| unit_price | Price per unit |
| amount | Transaction amount |

The included CSV is **synthetic sample data** so the project runs immediately. Replace it with your own transaction data while keeping the required column names (or edit `load_data()`).

## Run in VS Code (Windows)
1. Extract the ZIP file.
2. Open the extracted folder in VS Code.
3. Open Terminal → New Terminal.
4. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run:
   ```bash
   python run_project.py
   ```

## Outputs
The `outputs/` folder will contain:
- `customer_rfm_segments.csv` — customer-level RFM scores, segments, and K-Means cluster.
- `segment_summary.csv` — segment size, average RFM measures, and revenue.
- `customer_segmentation_report.xlsx` — Excel workbook with transactions, customer RFM, and summary sheets.
- `customers_by_segment.png` — customer count chart.
- `revenue_by_segment.png` — revenue by segment chart.
- `frequency_vs_monetary.png` — customer behavior scatter plot.
- `business_insights.txt` — automatically generated marketing recommendations.

The script also creates `customer_segmentation.db` with a `transactions` table for SQL practice.

## RFM definitions
- **Recency:** Number of days since the customer's most recent purchase. Lower is better.
- **Frequency:** Number of distinct transactions. Higher is better.
- **Monetary:** Total customer spend. Higher is better.

The R, F, and M scores range from 1 (lower relative score) to 5 (higher relative score). Recency is reversed so a more recent customer receives a higher score.

## Segment definitions
- Champions: recent, frequent, and high-spending customers.
- Loyal Customers: frequent customers with recent activity.
- New Customers: recent customers with relatively few purchases.
- At Risk: customers who have not purchased recently but have a purchase history.
- Hibernating: inactive customers with relatively low frequency.
- Big Spenders: customers with high monetary scores who do not meet a higher-priority rule.
- Potential Loyalists: customers with signs of repeat-purchase potential.

These are practical rule-based labels, not universal industry standards. Adjust thresholds to fit your business.

## Important notes
- RFM scores use quintiles from the dataset, so scores are relative to the customers in the current dataset.
- K-Means cluster numbers (0, 1, 2, 3) are arbitrary labels. They are not the same as the business-friendly RFM segments.
- This sample project is for learning and portfolio demonstration. Validate results against real business context before making campaign decisions.
