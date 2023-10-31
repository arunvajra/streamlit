import streamlit as st
import pandas as pd

# Load data from TSV files
drugs_df = pd.read_csv('drugs.tsv', sep='\t')
genes_df = pd.read_csv('genes.tsv', sep='\t')
clinical_variants_df = pd.read_csv('clinicalVariants.tsv', sep='\t')
filtered_drugs_details_df = pd.read_csv('filtered_drugs_with_details.csv')

# Get lists of drug and gene names
drug_names = drugs_df['Name'].dropna().tolist()
gene_names = genes_df['Symbol'].dropna().tolist()

# Get unique medical conditions from the "filtered_drugs_with_details.csv"
medical_conditions = set(filtered_drugs_details_df['contraindications'].dropna().str.split(',').explode().str.strip())
medical_conditions = sorted(medical_conditions)

# Homepage with search boxes
st.title('Drug-Gene Search')

# Drug search box
selected_drug = st.selectbox('What drug do you want to prescribe this patient?', options=drug_names, key='drug_search')

# Filter genes based on the selected drug
filtered_genes = clinical_variants_df[clinical_variants_df['chemicals'].str.contains(selected_drug, case=False, na=False)]['gene'].unique()
filtered_genes = [gene for gene in filtered_genes if gene in gene_names]  # Ensure that the genes are in the list of known genes

# Gene search box
selected_gene = st.selectbox('What is the gene of interest?', options=filtered_genes, key='gene_search')

# Medical Conditions search box (for multiple selection)
selected_conditions = st.multiselect('Select medical conditions (optional):', options=medical_conditions, key='medical_conditions_search')

# Function to check drug contraindications
def check_contraindications(selected_drug, selected_conditions):
    if not selected_conditions:  # Skip check if no conditions are selected
        return False
    drug_info = filtered_drugs_details_df[filtered_drugs_details_df['Name'].str.lower() == selected_drug.lower()]
    if not drug_info.empty:
        contraindications = drug_info.iloc[0]['contraindications']
        if pd.notnull(contraindications):
            contraindications = set(map(str.strip, contraindications.lower().split(',')))
            selected_conditions_set = set(map(str.lower, selected_conditions))
            if selected_conditions_set.intersection(contraindications):
                return True
    return False

# Function to get drug mechanism
def get_mechanism(selected_drug):
    drug_info = filtered_drugs_details_df[filtered_drugs_details_df['Name'].str.lower() == selected_drug.lower()]
    if not drug_info.empty:
        mechanism = drug_info.iloc[0]['mechanisms']
        if pd.notnull(mechanism):
            return mechanism
    return None

# Display user selection
if selected_drug:
    st.markdown(f"<div style='font-weight:bold; font-size:20px;'>DRUG: {selected_drug}</div>", unsafe_allow_html=True)

# Display mechanism
mechanism = get_mechanism(selected_drug)
if mechanism:
    st.info(f"**Mechanism:** {mechanism}")

if selected_gene:
    st.markdown(f"<div style='font-weight:bold; font-size:20px;'>BIOMARKER: {selected_gene}</div>", unsafe_allow_html=True)

if selected_conditions:
    conditions_str = ', '.join(selected_conditions)
    st.markdown(f"<div style='font-weight:bold; font-size:20px;'>MEDICAL CONDITIONS: {conditions_str}</div>", unsafe_allow_html=True)

# Check for contraindications
if check_contraindications(selected_drug, selected_conditions):
    st.error("This drug is not recommended based on the selected medical conditions.")

# Filter the clinical variants based on the selected gene and drug
filtered_variants = clinical_variants_df[(clinical_variants_df['gene'] == selected_gene) & (clinical_variants_df['chemicals'].str.contains(selected_drug, case=False, na=False))]

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
