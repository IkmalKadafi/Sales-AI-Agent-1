"""
Script untuk mengkonversi Retail Sales Data Set.csv
menjadi format yang sesuai untuk import ke web AI Sales Agent
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load data
print("Loading Retail Sales Data Set...")
df = pd.read_csv('Data/Retail Sales Data Set.csv')

# Lihat struktur data
print(f"\nJumlah baris: {len(df)}")
print(f"Kolom: {df.columns.tolist()}")

# Bersihkan dan transformasi data
print("\nMemproses data...")

# Ambil kolom yang relevan
df_clean = df[['Date', 'Product Category', 'Quantity', 'Total Amount']].copy()

# Rename kolom
df_clean.columns = ['date', 'product', 'quantity', 'total_sales']

# Parse tanggal
df_clean['date'] = pd.to_datetime(df_clean['date'], format='%m/%d/%Y')

# Tambahkan region (simulasi - karena data asli tidak punya region)
# Kita akan random assign ke 3 region
regions = ['Jakarta', 'Bandung', 'Surabaya']
np.random.seed(42)
df_clean['region'] = np.random.choice(regions, size=len(df_clean))

# Agregasi per hari, region, dan product
print("\nMengagregasi data per hari, region, dan produk...")
df_agg = df_clean.groupby(['date', 'region', 'product']).agg({
    'total_sales': 'sum',
    'quantity': 'sum'
}).reset_index()

# Hitung transaction_count (jumlah transaksi per grup)
transaction_counts = df_clean.groupby(['date', 'region', 'product']).size().reset_index(name='transaction_count')
df_agg = df_agg.merge(transaction_counts, on=['date', 'region', 'product'])

# Sort by date, region, product
df_agg = df_agg.sort_values(['region', 'product', 'date']).reset_index(drop=True)

# Tambahkan kolom day_name dan is_weekend
df_agg['day_name'] = df_agg['date'].dt.day_name()
df_agg['is_weekend'] = df_agg['date'].dt.dayofweek.isin([5, 6])

# Hitung target_daily (simulasi: rata-rata historis * 1.15)
print("\nMenghitung target dan metrik...")
target_multiplier = 1.15
df_agg['target_daily'] = df_agg.groupby(['region', 'product'])['total_sales'].transform(
    lambda x: x.expanding().mean().shift(1) * target_multiplier
)

# Untuk baris pertama tiap grup, gunakan rata-rata keseluruhan
for idx, row in df_agg[df_agg['target_daily'].isna()].iterrows():
    avg_sales = df_agg[(df_agg['region'] == row['region']) & 
                       (df_agg['product'] == row['product'])]['total_sales'].mean()
    df_agg.at[idx, 'target_daily'] = avg_sales * target_multiplier

# Hitung sales_yesterday
df_agg['sales_yesterday'] = df_agg.groupby(['region', 'product'])['total_sales'].shift(1)

# Hitung avg_7d_sales (rolling 7-day average)
df_agg['avg_7d_sales'] = df_agg.groupby(['region', 'product'])['total_sales'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean().shift(1)
)

# Hitung delta_vs_yesterday (%)
df_agg['delta_vs_yesterday'] = ((df_agg['total_sales'] - df_agg['sales_yesterday']) / 
                                 df_agg['sales_yesterday'] * 100)

# Hitung delta_vs_target (%)
df_agg['delta_vs_target'] = ((df_agg['total_sales'] - df_agg['target_daily']) / 
                              df_agg['target_daily'] * 100)

# Fill NaN values untuk baris pertama
df_agg['sales_yesterday'].fillna(df_agg['total_sales'], inplace=True)
df_agg['avg_7d_sales'].fillna(df_agg['total_sales'], inplace=True)
df_agg['delta_vs_yesterday'].fillna(0, inplace=True)
df_agg['delta_vs_target'].fillna(0, inplace=True)

# Round angka
df_agg['total_sales'] = df_agg['total_sales'].round(0).astype(int)
df_agg['target_daily'] = df_agg['target_daily'].round(0).astype(int)
df_agg['sales_yesterday'] = df_agg['sales_yesterday'].round(0).astype(int)
df_agg['avg_7d_sales'] = df_agg['avg_7d_sales'].round(0).astype(int)
df_agg['delta_vs_yesterday'] = df_agg['delta_vs_yesterday'].round(1)
df_agg['delta_vs_target'] = df_agg['delta_vs_target'].round(1)

# Reorder kolom sesuai format yang diminta
columns_order = [
    'date', 'region', 'product', 'total_sales', 'target_daily',
    'sales_yesterday', 'avg_7d_sales', 'delta_vs_yesterday', 'delta_vs_target',
    'day_name', 'is_weekend', 'quantity', 'transaction_count'
]
df_final = df_agg[columns_order].copy()

# Format tanggal
df_final['date'] = df_final['date'].dt.strftime('%Y-%m-%d')

# Ambil hanya data terbaru (misal 30 hari terakhir untuk demo)
latest_date = pd.to_datetime(df_final['date']).max()
cutoff_date = latest_date - timedelta(days=30)
df_final = df_final[pd.to_datetime(df_final['date']) >= cutoff_date]

print(f"\nData final:")
print(f"Jumlah baris: {len(df_final)}")
print(f"Rentang tanggal: {df_final['date'].min()} s/d {df_final['date'].max()}")
print(f"Region: {df_final['region'].unique().tolist()}")
print(f"Produk: {df_final['product'].unique().tolist()}")

# Simpan ke file
output_file = 'data/retail_sales_converted.csv'
df_final.to_csv(output_file, index=False)
print(f"\n✅ File berhasil disimpan: {output_file}")
print(f"\nAnda bisa mengupload file ini melalui halaman Import Data di web!")

# Tampilkan sample
print("\nSample data (5 baris pertama):")
print(df_final.head().to_string())
