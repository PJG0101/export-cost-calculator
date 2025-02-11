import streamlit as st
import pandas as pd

# Function to calculate costs
def calculate_final_cost(df, product, destination, incoterm, include_cross_stuffing, include_sgs):
    filtered_df = df[df['Product'] == product]

    if filtered_df.empty:
        st.error("No matching data found. Please check your selections.")
        return None

    # Determine relevant costs based on Incoterm
    ocean_freight = filtered_df[f'Ocean Freight ({destination})'].values[0] if incoterm in ['CIF', 'CFR'] else 0
    cross_stuffing = filtered_df['Cross Stuffing Fee'].values[0] if include_cross_stuffing else 0
    land_freight = filtered_df[f'Land Freight ({destination})'].values[0] if incoterm == 'CPT' else 0
    sgs_fee = filtered_df['SGS'].values[0] if include_sgs else 0

    base_cost = filtered_df['Base Cost (Ex-Work)'].values[0]
    packaging_cost = filtered_df['Packaging Cost'].values[0]
    export_duty = filtered_df['Export Duty'].values[0]
    logistic_to_port = filtered_df['Logistic to Port (Bandar Abas)'].values[0]
    thc_stuffing = filtered_df['THC + Stuffing'].values[0]
    warehousing = filtered_df['Warehousing'].values[0]
    demmurag = filtered_df['Demmurag'].values[0]

    total_cost = (
        base_cost + packaging_cost + export_duty + logistic_to_port +
        ocean_freight + land_freight + thc_stuffing + cross_stuffing + warehousing + demmurag + sgs_fee
    )

    result_df = pd.DataFrame({
        'Product': [product],
        'Destination': [destination],
        'Incoterm': [incoterm],
        'Base Cost (Ex-Work)': [base_cost],
        'Packaging Cost': [packaging_cost],
        'Export Duty': [export_duty],
        'Logistic to Port (Bandar Abas)': [logistic_to_port],
        'Ocean Freight': [ocean_freight],
        'Land Freight': [land_freight],
        'THC + Stuffing': [thc_stuffing],
        'SGS Fee': [sgs_fee],
        'Cross Stuffing Fee': [cross_stuffing],
        'Warehousing': [warehousing],
        'Demmurag': [demmurag],
        'Total Landed Cost': [total_cost]
    })

    return result_df

# Streamlit UI
st.title("📦 Export Cost Calculator")

# File uploader
uploaded_file = st.file_uploader("Upload your cost input Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Data Preview", df.head())

    # Dropdown selections
    product = st.selectbox("Select Product", df['Product'].unique())
    destination = st.selectbox("Select Destination", ['Tianjin, China', 'Jebel Ali', 'Rotterdam, NL', 'Mersin, Tr'])
    incoterm = st.selectbox("Select Incoterm", ['FOB', 'CIF', 'CFR', 'CPT'])
    
    # Checkbox options for additional costs
    include_cross_stuffing = st.checkbox("Include Cross Stuffing Fee")
    include_sgs = st.checkbox("Include SGS Fee")

    # Calculate button
    if st.button("🔄 Calculate Cost"):
        result_df = calculate_final_cost(df, product, destination, incoterm, include_cross_stuffing, include_sgs)

        if result_df is not None:
            st.write("### Cost Breakdown", result_df)
            
            # Save and provide download link
            output_file = "Final_Costs.xlsx"
            result_df.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="📥 Download Cost Breakdown",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
