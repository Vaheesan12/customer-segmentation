from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "retail_transactions.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
DB = ROOT / "customer_segmentation.db"

def load_data():
    df = pd.read_csv(DATA, parse_dates=["purchase_date"])
    required = {"transaction_id", "customer_id", "purchase_date", "quantity", "unit_price", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df = df.drop_duplicates(subset=["transaction_id"])
    df = df.dropna(subset=["customer_id", "purchase_date", "amount"])
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0) & (df["amount"] >= 0)]
    df["amount"] = df["quantity"] * df["unit_price"]
    return df

def save_sqlite(df):
    with sqlite3.connect(DB) as conn:
        df.to_sql("transactions", conn, if_exists="replace", index=False)
        query = """
        CREATE INDEX IF NOT EXISTS idx_transactions_customer
        ON transactions(customer_id);
        """
        conn.execute(query)

def calculate_rfm(df):
    # Use one day after the latest transaction as the analysis date.
    analysis_date = df["purchase_date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_id").agg(
        Recency=("purchase_date", lambda x: (analysis_date - x.max()).days),
        Frequency=("transaction_id", "nunique"),
        Monetary=("amount", "sum")
    ).reset_index()

    # Quintile scores: high recency score means a more recent customer.
    rfm["R"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_Score"] = rfm[["R","F","M"]].astype(str).agg("".join, axis=1)
    rfm["RFM_Total"] = rfm[["R","F","M"]].sum(axis=1)
    return rfm

def assign_segment(row):
    r, f, m = row["R"], row["F"], row["M"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 4:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New Customers"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    if m >= 4:
        return "Big Spenders"
    return "Potential Loyalists"

def add_kmeans(rfm):
    features = rfm[["Recency","Frequency","Monetary"]].copy()
    features["Recency"] = np.log1p(features["Recency"])
    features["Frequency"] = np.log1p(features["Frequency"])
    features["Monetary"] = np.log1p(features["Monetary"])
    scaled = StandardScaler().fit_transform(features)
    model = KMeans(n_clusters=min(4, len(rfm)), random_state=42, n_init=10)
    rfm["KMeans_Cluster"] = model.fit_predict(scaled)
    return rfm

def create_outputs(df, rfm):
    segment_summary = rfm.groupby("Segment").agg(
        Customers=("customer_id","count"),
        Avg_Recency_Days=("Recency","mean"),
        Avg_Frequency=("Frequency","mean"),
        Avg_Monetary=("Monetary","mean"),
        Revenue=("Monetary","sum")
    ).round(2).sort_values("Revenue", ascending=False)

    rfm.to_csv(OUT / "customer_rfm_segments.csv", index=False)
    segment_summary.to_csv(OUT / "segment_summary.csv")
    with pd.ExcelWriter(OUT / "customer_segmentation_report.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Clean_Transactions", index=False)
        rfm.to_excel(writer, sheet_name="RFM_Customers", index=False)
        segment_summary.to_excel(writer, sheet_name="Segment_Summary")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10,6))
    sns.countplot(data=rfm, y="Segment", order=rfm["Segment"].value_counts().index)
    plt.title("Customer Count by Segment")
    plt.xlabel("Number of Customers"); plt.ylabel("Customer Segment")
    plt.tight_layout(); plt.savefig(OUT / "customers_by_segment.png", dpi=160); plt.close()

    plt.figure(figsize=(10,6))
    sns.barplot(data=segment_summary.reset_index(), x="Segment", y="Revenue")
    plt.title("Revenue Contribution by Segment")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout(); plt.savefig(OUT / "revenue_by_segment.png", dpi=160); plt.close()

    plt.figure(figsize=(8,6))
    sns.scatterplot(data=rfm, x="Frequency", y="Monetary", hue="Segment", size="Recency", sizes=(20,180))
    plt.title("Customer Frequency vs Monetary Value")
    plt.tight_layout(); plt.savefig(OUT / "frequency_vs_monetary.png", dpi=160); plt.close()

    total_customers = len(rfm)
    total_revenue = rfm["Monetary"].sum()
    top_segment = segment_summary.index[0]
    lines = [
        "CUSTOMER SEGMENTATION INSIGHTS",
        f"Customers analyzed: {total_customers}",
        f"Total revenue: {total_revenue:,.2f}",
        f"Largest revenue segment: {top_segment}",
        "",
        "Segment-level recommendations:"
    ]
    recommendations = {
        "Champions": "Reward with VIP benefits, early access, referrals, and loyalty rewards.",
        "Loyal Customers": "Use loyalty tiers, cross-sell bundles, and personalized recommendations.",
        "New Customers": "Use welcome journeys, onboarding offers, and second-purchase incentives.",
        "At Risk": "Launch win-back campaigns, feedback surveys, and relevant limited-time offers.",
        "Hibernating": "Test low-cost reactivation campaigns and suppress unresponsive audiences.",
        "Big Spenders": "Offer premium products, personalized service, and exclusive product previews.",
        "Potential Loyalists": "Encourage repeat purchases with product education and loyalty enrollment."
    }
    for segment in segment_summary.index:
        lines.append(f"- {segment}: {recommendations.get(segment, 'Test targeted campaigns and monitor response.')}")
    (OUT / "business_insights.txt").write_text("\n".join(lines), encoding="utf-8")

def main():
    df = load_data()
    save_sqlite(df)
    rfm = calculate_rfm(df)
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)
    rfm = add_kmeans(rfm)
    create_outputs(df, rfm)
    print("Project completed successfully.")
    print(f"Transactions: {len(df):,} | Customers: {rfm['customer_id'].nunique():,}")
    print(f"Outputs saved in: {OUT}")

if __name__ == "__main__":
    main()
