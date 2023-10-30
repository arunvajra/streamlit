import streamlit as st
import pandas as pd

# Load data from TSV files
drugs_df = pd.read_csv('drugs.tsv', sep='\t')
genes_df = pd.read_csv('genes.tsv', sep='\t')
clinical_variants_df = pd.read_csv('clinicalVariants.tsv', sep='\t')

# Update the 'variant' column to keep only the part after "*"
clinical_variants_df['variant'] = clinical_variants_df['variant'].apply(lambda x: '*' + x.split('*')[-1] if '*' in str(x) else x)

# Get lists of drug and gene names
drug_names = drugs_df['Name'].dropna().tolist()
gene_names = genes_df['Symbol'].dropna().tolist()

# Homepage with search boxes
st.title('Drug-Gene Search')

# Drug search box
selected_drug = st.selectbox('What drug do you want to prescribe this patient?', options=drug_names, key='drug_search')

# Gene search box
selected_gene = st.selectbox('What is the gene of interest?', options=gene_names, key='gene_search')

# Display user selection
if selected_drug:
    st.markdown(f"<div style='font-weight:bold; font-size:20px;'>DRUG: {selected_drug}</div>", unsafe_allow_html=True)

if selected_gene:
    st.markdown(f"<div style='font-weight:bold; font-size:20px;'>BIOMARKER: {selected_gene}</div>", unsafe_allow_html=True)

    # Filter the clinical variants based on the selected gene
    filtered_variants = clinical_variants_df[clinical_variants_df['gene'] == selected_gene]

    # Define function to concatenate while removing consecutive duplicates
    def concatenate_unique(series):
        sorted_values = sorted(series.dropna())
        unique_values = []
        previous_value = None
        for value in sorted_values:
            if value != previous_value:
                unique_values.append(value)
            previous_value = value
        return ', '.join(unique_values)

    # Combine all the phenotypes for each variant, removing consecutive duplicates
    combined_variants = filtered_variants.groupby('variant')['phenotypes'].agg(concatenate_unique).reset_index().rename(columns={'variant': 'variants'})

    # If there are results, display them in a table
    if not combined_variants.empty:
        st.markdown(combined_variants.to_html(index=False), unsafe_allow_html=True)
    else:
        st.write('No clinical variants found for the selected gene.')
