import pandas as pd

# Load both datasets
feature_df = pd.read_csv("feature_sentiment.csv")
clean_stage_df = pd.read_csv("../intermediate/clean_stage_1.csv")

# Step 1: Remove rows where feature == "none" and evidence == "extraction_failed"
feature_df = feature_df[~((feature_df["feature"] == "none") & 
                          (feature_df["evidence"] == "extraction_failed"))]

# Step 2: Align by row index (since clean_stage_1.csv rows correspond to feature_sentiment.csv rows)
# Add the 'Model' column from clean_stage_df into feature_df
feature_df["clean_model"] = clean_stage_df["Model"]

# Step 3: Replace "unknown" with the clean model name
feature_df.loc[feature_df["model"].str.lower() == "unknown", "model"] = feature_df["clean_model"]

# Step 4: Drop helper column
feature_df = feature_df.drop(columns=["clean_model"])

# Step 5: Save cleaned dataset
feature_df.to_csv("feature_sentiment_cleaned.csv", index=False)

print("Cleaning complete. File saved as feature_sentiment_cleaned.csv")