import pandas as pd

files = [
    "/mnt/data/daily_sales_data_0.csv",
    "/mnt/data/daily_sales_data_1.csv",
    "/mnt/data/daily_sales_data_2.csv"
]

dfs = []
for file in files:
    dfs.append(pd.read_csv(file))

df = pd.concat(dfs, ignore_index=True)

df["product"] = df["product"].astype(str).str.strip().str.lower()
pink = df[df["product"] == "pink morsel"].copy()

pink["price"] = (
    pink["price"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
pink["price"] = pd.to_numeric(pink["price"], errors="coerce")
pink["quantity"] = pd.to_numeric(pink["quantity"], errors="coerce")

pink["Sales"] = pink["quantity"] * pink["price"]

out = pink[["Sales", "date", "region"]].copy()
out = out.rename(columns={"date": "Date", "region": "Region"})

out = out.groupby(["Date", "Region"], as_index=False)["Sales"].sum()

out.to_csv("/mnt/data/pink_morsels_sales.csv", index=False)

print("Saved:", "/mnt/data/pink_morsels_sales.csv")
print(out.head())
