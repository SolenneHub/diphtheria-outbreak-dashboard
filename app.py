import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Page Configuration
st.set_page_config(page_title="Advanced Jema'a LGA Diphtheria Dashboard", layout="wide")

st.title("📊 Advanced Diphtheria Outbreak Surveillance & Decision Dashboard")
st.markdown("### Jema'a Local Government Area, Kaduna State, Nigeria")
st.write("This interactive system translates raw epidemiological data into actionable public health policies.")

# 2. Load and Preprocess Dataset
@st.cache_data
def load_data():
    data = pd.read_csv('diphtheria_jemaa_mock_data.csv')
    # Convert date column to actual datetime objects for time-series analysis
    data['Date_of_Onset'] = pd.to_datetime(data['Date_of_Onset'])
    
    # Feature Engineering: Create meaningful epidemiological Age Groups
    def assign_age_group(age):
        if age <= 2: return "Infants/Toddlers (0-2 yrs)"
        elif age <= 5: return "Preschool (3-5 yrs)"
        elif age <= 10: return "Early School Age (6-10 yrs)"
        else: return "Adolescents (11-15 yrs)"
        
    data['Age_Group'] = data['Age'].apply(assign_age_group)
    return data

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Options")
selected_ward = st.sidebar.multiselect("Select Ward/Location:", options=df['Ward'].unique(), default=df['Ward'].unique())
selected_vax = st.sidebar.multiselect("Select Vaccination Status:", options=df['Vaccination_Status'].unique(), default=df['Vaccination_Status'].unique())

filtered_df = df[(df['Ward'].isin(selected_ward)) & (df['Vaccination_Status'].isin(selected_vax))]

# 4. Top-Level Metric Cards
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Confirmed Cases", len(filtered_df))
with col2:
    st.metric("Average Patient Age", f"{filtered_df['Age'].mean():.1f} Years")
with col3:
    st.metric("Severe / Hospitalized", len(filtered_df[filtered_df['Outcome'] == 'Severe/Hospitalized']))
with col4:
    st.metric("Recovery Rate", f"{(len(filtered_df[filtered_df['Outcome'] == 'Recovered']) / len(filtered_df) * 100):.1f}%" if len(filtered_df) > 0 else "0%")

# 5. NEW VISUALIZATION ROW 1: Time-Series & Age Grouping
st.markdown("---")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📈 Outbreak Timeline (Epidemic Curve)")
    # Group cases by date of onset
    epi_data = filtered_df.groupby('Date_of_Onset').size().reset_index(name='Case_Count')
    
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    sns.lineplot(data=epi_data, x='Date_of_Onset', y='Case_Count', marker='o', color='#d95f02', linewidth=2.5, ax=ax1)
    plt.xticks(rotation=45)
    plt.ylabel("New Daily Cases")
    plt.xlabel("Date of Symptom Onset")
    plt.tight_layout()
    st.pyplot(fig1)
    
    # Actionable Decision Path
    st.info("**📍 Policy Decision Path:** If the curve shows a steep upward trajectory, initiate immediate emergency isolation protocols. If the curve is plateauing or dropping, transition resources toward community-wide ring-vaccination campaigns.")

with row1_col2:
    st.subheader("👶 Case Burden by Pediatric Age Groups")
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    age_order = ["Infants/Toddlers (0-2 yrs)", "Preschool (3-5 yrs)", "Early School Age (6-10 yrs)", "Adolescents (11-15 yrs)"]
    sns.countplot(data=filtered_df, x='Age_Group', order=age_order, palette='Set3', ax=ax2)
    plt.xticks(rotation=15, fontsize=9)
    plt.ylabel("Number of Patients")
    plt.xlabel("Target Age Categories")
    plt.tight_layout()
    st.pyplot(fig2)
    
    # Actionable Decision Path
    st.warning("**📍 Policy Decision Path:** High concentrations in the *0-2 and 3-5 categories* indicate low primary immunization coverage. Decision: Deploy mobile immunization teams directly to local healthcare facilities and markets.")

# 6. VISUALIZATION ROW 2: Vaccine Profiles & Wards
st.markdown("---")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("💡 Vaccine Efficacy Profile")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    sns.countplot(data=filtered_df, x='Vaccination_Status', hue='Outcome', palette='Set2', ax=ax3)
    st.pyplot(fig3)
    st.error("**📍 Policy Decision Path:** The data reveals that being Unvaccinated heavily correlates with severe hospitalization. Decision: Launch targeted public health radio broadcasts across Jema'a LGA to counter vaccine hesitancy.")

with row2_col2:
    st.subheader("📍 Geographic Load by Ward")
    fig4, ax4 = plt.subplots(figsize=(7, 4))
    sns.countplot(data=filtered_df, y='Ward', order=filtered_df['Ward'].value_counts().index, palette='viridis', ax=ax4)
    st.pyplot(fig4)
    st.success("**📍 Policy Decision Path:** Resource Allocation. Prioritize emergency medical logistics, antibiotics, and antitoxins to the top three wards displaying the heaviest case totals.")