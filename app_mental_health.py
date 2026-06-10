import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency

# 1. Page Configuration
st.set_page_config(page_title="Tech Mental Health Dashboard", layout="wide")

st.title("🧠 Corporate Wellness & Mental Health Analytics Dashboard")
st.markdown("### Evaluating Systemic Support Systems and Demographic Variances in Tech")
st.write("This interactive application maps out workplace health trends and runs inferential statistical models on the fly.")

# 2. Load and Clean Dataset
@st.cache_data
def load_and_clean_data():
    # Load the survey file
    data = pd.read_csv('Desktop/DocumentsPublic_Health_Project/survey.csv')
    
    # Clean Age boundaries
    data['Age'] = pd.to_numeric(data['Age'], errors='coerce')
    data = data[(data['Age'] >= 18) & (data['Age'] <= 75)]
    
    # Standardize Gender inputs
    def clean_gender(gender):
        if pd.isna(gender): return 'Unknown'
        g = str(gender).lower().strip()
        if g in ['male', 'm', 'marle', 'maleish', 'maile', 'mal', 'cis male', 'guy', 'cis man']: return 'Male'
        elif g in ['female', 'f', 'woman', 'femake', 'cis female', 'cis woman', 'femail']: return 'Female'
        else: return 'Non-Binary/Other'
        
    data['Clean_Gender'] = data['Gender'].apply(clean_gender)
    return data

df = load_and_clean_data()

# 3. Sidebar Filters
st.sidebar.header("Data Filter Controls")
selected_country = st.sidebar.multiselect("Select Countries:", options=df['Country'].unique(), default=['United States', 'United Kingdom', 'Canada'])
selected_gender = st.sidebar.multiselect("Select Gender Groups:", options=df['Clean_Gender'].unique(), default=df['Clean_Gender'].unique())

# Apply side filters to the dataset
filtered_df = df[(df['Country'].isin(selected_country)) & (df['Clean_Gender'].isin(selected_gender))]

# 4. High-Level Summary Metrics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Rows Evaluated", len(filtered_df))
with col2:
    treatment_rate = (len(filtered_df[filtered_df['treatment'] == 'Yes']) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Sought Clinical Treatment", f"{treatment_rate:.1f}%")
with col3:
    knows_benefits = (len(filtered_df[filtered_df['benefits'] == 'Yes']) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Aware of Company Benefits", f"{knows_benefits:.1f}%")
with col4:
    remote_pct = (len(filtered_df[filtered_df['remote_work'] == 'Yes']) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Remote Workforce Rate", f"{remote_pct:.1f}%")

# 5. Charts Visualization Row
st.markdown("---")
row_col1, row_col2 = st.columns(2)

with row_col1:
    st.subheader("📊 Frequency of Mental Health Work Interference")
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    sns.set_theme(style="whitegrid")
    sns.countplot(
        data=filtered_df.fillna({'work_interfere': 'Not Reported'}), 
        x='work_interfere', 
        palette='pastel',
        order=['Often', 'Sometimes', 'Rarely', 'Never', 'Not Reported'],
        ax=ax1
    )
    plt.xlabel("Level of Productivity Interference")
    plt.ylabel("Employee Count")
    plt.tight_layout()
    st.pyplot(fig1)

with row_col2:
    st.subheader("🏢 Benefits Awareness Level by Company Size")
    # Build cross tabulation percentages dynamically
    if len(filtered_df) > 0:
        cross_tab = pd.crosstab(filtered_df['no_employees'], filtered_df['benefits'], normalize='index') * 100
        fig2, ax2 = plt.subplots(figsize=(7, 4.5))
        cross_tab.plot(kind='bar', stacked=True, colormap='Set3', ax=ax2)
        plt.xlabel("Company Size Category")
        plt.ylabel("Percentage (%)")
        plt.xticks(rotation=45)
        plt.legend(title="Offers Benefits?")
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.write("No data available for the active filters.")

# 6. Inferential Statistical Analysis Section
st.markdown("---")
st.subheader("🔬 Live Inferential Statistics: Chi-Square Test of Independence")
st.write("Hypothesis Testing: Does having a **family history of mental illness** significantly increase an employee's likelihood to **seek treatment** within the current selected filter criteria?")

if len(filtered_df) > 5:
    # Run dynamic contingency matrix
    matrix = pd.crosstab(filtered_df['family_history'], filtered_df['treatment'])
    chi2, p_val, dof, exp = chi2_contingency(matrix)
    
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.markdown("**Test Output Matrix Data:**")
        st.write(matrix)
    with stat_col2:
        st.markdown(f"**Calculated Chi-Square Statistic:** `{chi2:.4f}`")
        st.markdown(f"**P-Value (Statistical Significance):** `{p_val:.6f}`")
        
        if p_val < 0.05:
            st.success("🎯 **Statistical Outcome:** Highly Significant ($p < 0.05$). The correlation between family health background and individual care-seeking behavior is mathematically verified for this subgroup.")
        else:
            st.warning("⚠️ **Statistical Outcome:** Not Significant ($p \geq 0.05$). We fail to reject the null hypothesis for this specific filtered subset.")
else:
    st.error("Insufficent records filtered to safely run a Chi-Square calculation.")