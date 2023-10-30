import streamlit as st
import pandas as pd

# Load data from TSV files
drugs_df = pd.read_csv('drugs.tsv', sep='\t')
genes_df = pd.read_csv('genes.tsv', sep='\t')
clinical_variants_df = pd.read_csv('clinicalVariants.tsv', sep='\t')

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

    # Remove gene name from variant names
    filtered_variants['variant'] = filtered_variants['variant'].apply(lambda x: x.replace(selected_gene, '') if pd.notnull(x) else x)

    # Define function to concatenate while removing consecutive duplicates
    def concatenate_unique(series):
        # Split the phenotype strings into individual phenotype terms
        phenotype_terms = series.dropna().str.split(',').explode()
        # Remove leading/trailing whitespaces and sort the terms
        sorted_unique_terms = sorted(set(phenotype_terms.str.strip()))
        # Join the unique, sorted terms back into a string
        return ', '.join(sorted_unique_terms)

    # Combine all the phenotypes for each variant, removing consecutive duplicates
    combined_variants = filtered_variants.groupby('variant')['phenotypes'].agg(concatenate_unique).reset_index().rename(columns={'variant': 'variants'})

    # If there are results, display them in a table
    if not combined_variants.empty:
        st.markdown(combined_variants.to_html(index=False), unsafe_allow_html=True)
    else:
        st.write('No clinical variants found for the selected gene.')
