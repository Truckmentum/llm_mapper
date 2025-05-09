import os
import pandas as pd
import yaml
from mapper.schema_mapper import extract_columns_from_excel, load_target_schema, apply_mapping

from mapper.llm_mapper import get_llm_column_mapping

def main():
    # Path to all files you want to process
    files = {
        "Van-OC 2025.xlsx": "All Dryvan Lanes",
        "Owens Corning 2024 Outbound Network RFP-Fraley  Schilling.xlsx": "Bid Sheet",
        "OC Flatbed - 2025.xlsx": "Flatbed Lanes",
    }

    # Load schema
    schema_path = "Config/target_schema.yaml"
    schema = load_target_schema(schema_path)

    # Combine all columns from all files
    all_source_columns = set()

    for file, sheet in files.items():
        file_path = os.path.join("/Users/fermet/Downloads/OneDrive_2_24-03-2025/", file)
        df = extract_columns_from_excel(file_path, sheet)
        all_source_columns.update(df.columns)

    # Run LLM mapping
    mapping = get_llm_column_mapping(list(all_source_columns), schema)

    print("\n Final Mapping Result:")
    for source, target in mapping.items():
        print(f"{source} -> {target}")

    # Optionally: apply to a specific file
    sample_file = "/Users/fermet/Downloads/OneDrive_2_24-03-2025/OC Flatbed - 2025.xlsx"
    df = extract_columns_from_excel(sample_file, "Flatbed Lanes")
    transformed_df = apply_mapping(df, mapping, drop_unmapped=True)

    print("\n Final Transformed DataFrame:")
    print(transformed_df.head())

if __name__ == "__main__":
    main()
