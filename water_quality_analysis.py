"""
Water Quality Dataset Analysis
Environmental Data Scientist Portfolio Project
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import seaborn as sns

# ============================================
# STEP 1: Load and Inspect the Dataset
# ============================================

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('Water_Quality_Dataset.csv')

# Display basic info about the dataset
print("Dataset Shape:", df.shape)
print("\nColumn Names:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nData Types:")
print(df.dtypes)
print("\nMissing Values:")
print(df.isnull().sum())

# ============================================
# STEP 2: Clean the Dataset
# ============================================

# Make a copy to preserve original data
df_clean = df.copy()

# Convert Timestamp to datetime format
df_clean['Timestamp'] = pd.to_datetime(df_clean['Timestamp'])

# Check for and handle missing values
print("\nMissing values after conversion:")
print(df_clean.isnull().sum())

# Fill missing numerical values with median (more robust than mean for environmental data)
numeric_columns = ['pH', 'Turbidity (NTU)', 'Temperature (°C)', 'DO (mg/L)', 
                   'BOD (mg/L)', 'Lead (mg/L)', 'Mercury (mg/L)', 'Arsenic (mg/L)']

for col in numeric_columns:
    if df_clean[col].isnull().sum() > 0:
        median_val = df_clean[col].median()
        df_clean[col].fillna(median_val, inplace=True)
        print(f"Filled {col} missing values with median: {median_val:.4f}")

# Remove any duplicate rows if present
duplicates = df_clean.duplicated().sum()
if duplicates > 0:
    df_clean = df_clean.drop_duplicates()
    print(f"Removed {duplicates} duplicate rows")

# Check for outliers using IQR method (optional - just flag them)
def detect_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return data[(data[column] < lower) | (data[column] > upper)]

print("\nOutlier Summary (rows with outliers in key parameters):")
for col in ['pH', 'Turbidity (NTU)', 'Lead (mg/L)', 'Arsenic (mg/L)']:
    outliers = detect_outliers_iqr(df_clean, col)
    print(f"  {col}: {len(outliers)} potential outliers")

# ============================================
# STEP 3: Feature Engineering & Monthly Averages
# ============================================

# Extract month and year from Timestamp for grouping
df_clean['Year'] = df_clean['Timestamp'].dt.year
df_clean['Month'] = df_clean['Timestamp'].dt.month
df_clean['Month_Year'] = df_clean['Timestamp'].dt.to_period('M')

# Calculate monthly averages for all numeric parameters
monthly_avg = df_clean.groupby(['Month_Year', 'Location'])[numeric_columns].mean().reset_index()

# Also calculate overall monthly averages (across all locations)
overall_monthly_avg = df_clean.groupby('Month_Year')[numeric_columns].mean().reset_index()
overall_monthly_avg['Month_Year_Str'] = overall_monthly_avg['Month_Year'].astype(str)

print("\nMonthly Averages (first 5 rows):")
print(overall_monthly_avg.head())

# ============================================
# STEP 4: Create Visualization 1 - Monthly Trends
# ============================================

# Chart 1: Monthly average pH, DO, and Temperature trends
plt.figure(figsize=(14, 8))

# pH trend
plt.subplot(3, 1, 1)
plt.plot(overall_monthly_avg['Month_Year_Str'], overall_monthly_avg['pH'], 
         marker='o', linewidth=2, color='blue', label='pH')
plt.axhspan(6.5, 8.5, alpha=0.2, color='green', label='Optimal pH Range (6.5-8.5)')
plt.ylabel('pH Level', fontsize=11)
plt.title('Monthly Average pH Levels (2024)', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# Dissolved Oxygen trend
plt.subplot(3, 1, 2)
plt.plot(overall_monthly_avg['Month_Year_Str'], overall_monthly_avg['DO (mg/L)'], 
         marker='s', linewidth=2, color='cyan', label='DO (mg/L)')
plt.ylabel('Dissolved Oxygen (mg/L)', fontsize=11)
plt.title('Monthly Average Dissolved Oxygen Levels', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# Temperature trend
plt.subplot(3, 1, 3)
plt.plot(overall_monthly_avg['Month_Year_Str'], overall_monthly_avg['Temperature (°C)'], 
         marker='^', linewidth=2, color='red', label='Temperature (°C)')
plt.ylabel('Temperature (°C)', fontsize=11)
plt.xlabel('Month (2024)', fontsize=11)
plt.title('Monthly Average Water Temperature', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
print("\nSaved: monthly_trends.png")
plt.close()

# ============================================
# STEP 5: Create Visualization 2 - Location Comparison
# ============================================

# Chart 2: Average contaminant levels by location (Lead, Mercury, Arsenic)
location_avg = df_clean.groupby('Location')[['Lead (mg/L)', 'Mercury (mg/L)', 'Arsenic (mg/L)']].mean().reset_index()

# WHO safety thresholds (mg/L)
who_thresholds = {'Lead (mg/L)': 0.01, 'Mercury (mg/L)': 0.006, 'Arsenic (mg/L)': 0.01}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Lead by location
axes[0].bar(location_avg['Location'], location_avg['Lead (mg/L)'], color='darkred', alpha=0.7)
axes[0].axhline(y=who_thresholds['Lead (mg/L)'], color='black', linestyle='--', 
                linewidth=2, label=f'WHO Limit ({who_thresholds["Lead (mg/L)"]} mg/L)')
axes[0].set_title('Average Lead Levels by Location', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Lead Concentration (mg/L)')
axes[0].set_xlabel('Location')
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')

# Mercury by location
axes[1].bar(location_avg['Location'], location_avg['Mercury (mg/L)'], color='purple', alpha=0.7)
axes[1].axhline(y=who_thresholds['Mercury (mg/L)'], color='black', linestyle='--', 
                linewidth=2, label=f'WHO Limit ({who_thresholds["Mercury (mg/L)"]} mg/L)')
axes[1].set_title('Average Mercury Levels by Location', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Mercury Concentration (mg/L)')
axes[1].set_xlabel('Location')
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')

# Arsenic by location
axes[2].bar(location_avg['Location'], location_avg['Arsenic (mg/L)'], color='orange', alpha=0.7)
axes[2].axhline(y=who_thresholds['Arsenic (mg/L)'], color='black', linestyle='--', 
                linewidth=2, label=f'WHO Limit ({who_thresholds["Arsenic (mg/L)"]} mg/L)')
axes[2].set_title('Average Arsenic Levels by Location', fontsize=13, fontweight='bold')
axes[2].set_ylabel('Arsenic Concentration (mg/L)')
axes[2].set_xlabel('Location')
axes[2].legend()
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('contaminants_by_location.png', dpi=300, bbox_inches='tight')
print("Saved: contaminants_by_location.png")
plt.close()

# ============================================
# STEP 6: Create Visualization 3 - Correlation Heatmap
# ============================================

# Chart 3: Correlation matrix of water quality parameters
plt.figure(figsize=(12, 10))

# Calculate correlation matrix
corr_matrix = df_clean[numeric_columns + ['Pollution_Level']].corr()

# Create heatmap
sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0, 
            square=True, fmt='.2f', cbar_kws={'label': 'Correlation Coefficient'})
plt.title('Water Quality Parameters Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
print("Saved: correlation_heatmap.png")
plt.close()

# ============================================
# STEP 7: Additional Analysis - Pollution Level Distribution
# ============================================

# Print summary statistics
print("\n" + "="*50)
print("SUMMARY STATISTICS")
print("="*50)

print("\nOverall Statistics by Location:")
location_stats = df_clean.groupby('Location')[numeric_columns].agg(['mean', 'std', 'min', 'max'])
print(location_stats)

print("\nPollution Level Distribution:")
print(df_clean['Pollution_Level'].value_counts().sort_index())

# Save cleaned data and monthly averages
df_clean.to_csv('water_quality_cleaned.csv', index=False)
monthly_avg.to_csv('monthly_averages.csv', index=False)
overall_monthly_avg.to_csv('overall_monthly_averages.csv', index=False)

print("\nSaved: water_quality_cleaned.csv")
print("Saved: monthly_averages.csv")
print("Saved: overall_monthly_averages.csv")

print("\n" + "="*50)
print("ANALYSIS COMPLETE")
print("="*50)
print("Generated files:")
print("  - monthly_trends.png")
print("  - contaminants_by_location.png")
print("  - correlation_heatmap.png")
print("  - water_quality_cleaned.csv")
print("  - monthly_averages.csv")
print("  - overall_monthly_averages.csv")
