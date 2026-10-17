import pandas as pd

df = pd.read_parquet("data/raw/online_retail_ii.parquet")
print("Raw rows:", len(df))

df = df[~df["Invoice"].str.upper().str.startswith("C")]
df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

is_product = df["StockCode"].str.match(r"^\d{5}")
dropped = df[~is_product]
print("Rows dropped as non-product codes:", len(dropped))
print("Codes dropped:", sorted(dropped["StockCode"].unique())[:40])
df = df[is_product].copy()
print("Rows kept:", len(df))

df["week"] = df["InvoiceDate"].dt.to_period("W").dt.start_time

# Last week (5-9 Dec 2011) is incomplete, so drop it
last = df["week"].max()
df = df[df["week"] < last]
print("Dropped incomplete week starting", last.date())

weekly = df.groupby(["week", "StockCode"])["Quantity"].sum().unstack(fill_value=0)
full = pd.date_range(weekly.index.min(), weekly.index.max(), freq="7D")
weekly = weekly.reindex(full, fill_value=0)
weekly.index.name = "week"

eligible = (weekly > 0).sum() >= 52
top = weekly.loc[:, eligible].sum().nlargest(30).index
weekly = weekly[top].astype(float)
weekly.columns = [str(c) for c in weekly.columns]
weekly.to_parquet("data/weekly_units.parquet")

products = (df[df["StockCode"].isin(top)]
            .groupby("StockCode")
            .agg(description=("Description", lambda s: s.mode().iloc[0]),
                 average_price=("Price", "mean"))
            .reset_index().rename(columns={"StockCode": "sku"}))
products["sku"] = products["sku"].astype(str)
products["average_price"] = products["average_price"].round(2)
products.to_csv("data/products.csv", index=False)

print("\nProducts kept:", weekly.shape[1])
print("Weeks:", weekly.shape[0], "from", weekly.index.min().date(), "to", weekly.index.max().date())
print(products.head())
