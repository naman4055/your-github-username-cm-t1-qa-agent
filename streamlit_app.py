import streamlit as st
import pandas as pd

def main():
    st.title(🔍" CM-T1 QA Agent (Placement ID Matching)")

    st.write("Upload the Campaign Legacy Sheet and the T1 Trafficking Sheet")

    legacy_file = st.file_uploader("Upload Campaign Legacy Spreadsheet", type=["xlsx"])
    t1_file = st.file_uploader("Upload Trafficking Sheet (T1)", type=["xlsx"])

    if legacy_file and t1_file:
        legacy_df = pd.read_excel(legacy_file)
        t1_df = pd.read_excel(t1_file)

        mismatches = compare_sheets(legacy_df, t1_df)

        if mismatches.empty:
            st.success("No mismatches found! ✅")
        else:
            st.error("Mismatches found!")
            st.dataframe(mismatches)

@st.cache_data

def compare_sheets(legacy_df, t1_df):
    # Define field mappings
    mapping = {
        "Site Name": "SITE NAME",
        "Placement ID": "PLACEMENT ID",
        "Placement Name": "PLACEMENT NAME",
        "Creative Name": "CREATIVE NAME",
        "Creative Start Date": "CREATIVE START DATE",
        "Creative End Date": "CREATIVE END DATE",
        "Creative Type": "CREATIVE TYPE",
        "Placement Compatibility": "PLACEMENT TYPE",
        "Dimensions": "DISPLAY DIMENSION",
        "Placement Duration": "VIDEO DURATION",
        "Rotation Value": "ROTATION",
        "Creative Click-Through URL": "FINAL CLICK-THROUGH URL"
    }

    results = []

    # Make sure Placement ID is treated as str
    legacy_df['Placement ID'] = legacy_df['PLACEMENT ID'].astype(str)
    t1_df['Placement ID'] = t1_df['Placement ID'].astype(str)

    for idx, t1_row in t1_df.iterrows():
        placement_id = str(t1_row['Placement ID'])
        matching_rows = legacy_df[legacy_df['Placement ID'] == placement_id]

        if not matching_rows.empty:
            legacy_row = matching_rows.iloc[0]  # Take the first match

            for t1_field, legacy_field in mapping.items():
                t1_value = str(t1_row.get(t1_field, "")).strip()
                legacy_value = str(legacy_row.get(legacy_field, "")).strip()

                qa_status = "✅" if t1_value == legacy_value else "❌"

                results.append({
                    "Level": identify_level(t1_field),
                    "Field": t1_field,
                    "T1 Sheet Value": t1_value,
                    "Legacy Sheet Value": legacy_value,
                    "QA Status": qa_status
                })

    return pd.DataFrame(results)

def identify_level(field_name):
    field_name = field_name.lower()
    if "placement" in field_name:
        return "Placement"
    if "creative" in field_name:
        return "Creative"
    if "rotation" in field_name:
        return "Creative"
    if "site" in field_name:
        return "Campaign"
    if "ad" in field_name:
        return "Ad"
    return "Other"

if __name__ == "__main__":
    main()
