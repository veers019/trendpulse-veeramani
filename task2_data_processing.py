import pandas as pd
import os
import glob

# Step 1: Load latest JSON file

json_files = glob.glob("data/trends_*.json")

if not json_files:
    print("No JSON files found in data/ folder.")
    exit()

latest_file = max(json_files, key=os.path.getctime)

df = pd.read_json(latest_file)

print(f"Loaded {len(df)} stories from {latest_file}")

# Step 2: Clean the Data

# Remove duplicates based on post_id
before = len(df)
df = df.drop_duplicates(subset="post_id")
print(f"After removing duplicates: {len(df)}")

# Remove missing values
before = len(df)
df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

# Fix data types
df["score"] = df["score"].astype(int)
df["num_comments"] = df["num_comments"].fillna(0).astype(int)

# Remove low-quality stories (score < 5)
df = df[df["score"] >= 5]
print(f"After removing low scores: {len(df)}")

# Clean whitespace in title
df["title"] = df["title"].str.strip()

# Step 3: Save as CSV

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

output_file = "data/trends_clean.csv"

df.to_csv(output_file, index=False)

print(f"\nSaved {len(df)} rows to {output_file}")


# Summary: Stories per category


print("\nStories per category:")
print(df["category"].value_counts())
