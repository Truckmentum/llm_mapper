import pandas as pd
import yaml

def load_target_schema(schema_path):
    with open(schema_path, "r") as f:
        schema = yaml.safe_load(f)
    return schema

def extract_columns_from_excel(file_path, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.columns = df.columns.map(str)  # Ensure all are strings
        return df
    except Exception as e:
        print(f"❌ Failed to read {file_path} ({sheet_name}): {e}")
        return pd.DataFrame()

def apply_mapping(df, mapping, drop_unmapped=False):
    df = df.rename(columns=mapping)
    if drop_unmapped:
        # Keep only columns that were mapped to target schema
        mapped_targets = list(mapping.values())
        df = df[[col for col in df.columns if col in mapped_targets]]
    return df
