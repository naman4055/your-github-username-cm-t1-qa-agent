import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="CM-T1 QA Agent", page_icon="🔍")
    st.title("\U0001F50D CM-T1 QA Agent (Placement ID Matching)")

    st.write("Upload the Campaign Legacy Sheet and the T1 Trafficking Sheet")

    legacy_file = st.file_uploader("Upload Campaign Legacy Spreadsheet", type=["xlsx"])
    t1_file = st.file_uploader("Upload Trafficking Sheet (T1)", type=["xlsx"])

    if legacy_file and t1_file:
        legacy_df = pd.read_excel(legacy_file)
        t1_df = pd.read_excel(t1_file)

        # Normalize columns: strip spaces and make uppercase
        legacy_df.columns = legacy_df.columns.str.strip().str.upper()
        t1_df.columns = t1_df.columns.str.strip().str.upper()

        mismatches = compare_sheets(legacy_df, t1_df)

        if mismatches.empty:
            st.success("No mismatches found! ✅")
        else:
            st.error("Mismatches found!")
            st.dataframe(mismatches)

            csv = mismatches.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📅 Download QA Mismatches as CSV",
                data=csv,
                file_name='qa_mismatches.csv',
                mime='text/csv'
            )

@st.cache_data

def compare_sheets(legacy_df, t1_df):
    # Define field mappings (uppercase)
    mapping = {
        "SITE NAME": "SITE NAME",
        "PLACEMENT ID": "PLACEMENT ID",
        "PLACEMENT NAME": "PLACEMENT NAME",
        "CREATIVE NAME": "CREATIVE NAME",
        "CREATIVE START DATE": "CREATIVE START DATE",
        "CREATIVE END DATE": "CREATIVE END DATE",
        "CREATIVE TYPE": "CREATIVE TYPE",
        "PLACEMENT COMPATIBILITY": "PLACEMENT TYPE",
        "DIMENSIONS": "DISPLAY DIMENSION",
        "PLACEMENT DURATION": "VIDEO DURATION",
        "ROTATION VALUE": "ROTATION",
        "CREATIVE CLICK-THROUGH URL": "FINAL CLICK-THROUGH URL"
    }

    results = []

    # Match by Placement ID
    for idx, t1_row in t1_df.iterrows():
        placement_id = str(t1_row.get('PLACEMENT ID', '')).strip()

        matching_rows = legacy_df[legacy_df['PLACEMENT ID'] == placement_id]

        if not matching_rows.empty:
            legacy_row = matching_rows.iloc[0]  # Take first match

            for t1_field, legacy_field in mapping.items():
                t1_value = str(t1_row.get(t1_field, '')).strip()
                legacy_value = str(legacy_row.get(legacy_field, '')).strip()

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
