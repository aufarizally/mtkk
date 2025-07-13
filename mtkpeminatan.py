import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Fungsi untuk menghitung metrik penjualan 
def calculate_metrics(sales_df):
    fruits = sales_df.columns[1:]  # Kolom pertama adalah tanggal
    metrics = {
        'Buah': [],
        'Total Penjualan (kg)': [],
        'Rata-rata Harian (kg)': [],
        'Rata-rata Mingguan (kg)': [],
        'ROP (kg)': [],
        'Status Stok': []
    }
    
    for fruit in fruits:
        daily_avg = sales_df[fruit].mean()
        weekly_avg = daily_avg * 7  # Konversi ke mingguan
        
        metrics['Buah'].append(fruit)
        metrics['Total Penjualan (kg)'].append(sales_df[fruit].sum())
        metrics['Rata-rata Harian (kg)'].append(round(daily_avg, 2))
        metrics['Rata-rata Mingguan (kg)'].append(round(weekly_avg, 2))
        metrics['ROP (kg)'].append(round(2 * daily_avg, 2))  # Lead time 2 hari
        metrics['Status Stok'].append("🟢 Aman")  # Default
    
    return pd.DataFrame(metrics)

# Konfigurasi tampilan
st.set_page_config(layout="wide", page_title="Analisis Penjualan Buah per kg")

# CSS styling
st.markdown("""
<style>
.header {
    background-color: #800000;
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# Header aplikasi
st.markdown('<div class="header"><h1>📈 Analisis Penjualan Buah (per kg)</h1></div>', unsafe_allow_html=True)

# Inisialisasi data
if 'sales_data' not in st.session_state:
    cols = ['Tanggal', 'Apel', 'Pisang', 'Anggur', 'Stroberi', 'Mangga', 'Jeruk']
    st.session_state.sales_data = pd.DataFrame(columns=cols)

# Tab utama
tab1, tab2 = st.tabs(["📝 Input Data", "📊 Analisis"])

with tab1:
    st.markdown("### Input Data Penjualan")
    
    # Input form
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Tanggal", datetime.today())        
        apel = st.number_input("Apel (kg)", min_value=0.0, format="%.2f")
        anggur = st.number_input("Anggur (kg)", min_value=0.0, format="%.2f")
    with col2:
        pisang = st.number_input("Pisang (kg)", min_value=0.0, format="%.2f")
        stroberi = st.number_input("Stroberi (kg)", min_value=0.0, format="%.2f")
        mangga = st.number_input("Mangga (kg)", min_value=0.0, format="%.2f")
        jeruk = st.number_input("Jeruk (kg)", min_value=0.0, format="%.2f")
    
    if st.button("Simpan Data"):
        new_data = {
            'Tanggal': date,
            'Apel': apel, 'Pisang': pisang, 'Anggur': anggur,
            'Stroberi': stroberi, 'Mangga': mangga, 'Jeruk': jeruk
        }
        st.session_state.sales_data = st.session_state.sales_data.append(new_data, ignore_index=True)
        st.success("Data tersimpan!")

    st.markdown("### Riwayat Data")
    st.dataframe(st.session_state.sales_data)

with tab2:
    if st.session_state.sales_data.empty:
        st.warning("Silakan input data terlebih dahulu")
    else:
        # Hitung metrik
        metrics = calculate_metrics(st.session_state.sales_data)
        
        # Tampilkan buah terlaris
        st.markdown("### 🏆 Buah Terlaris")
        top_product = metrics.iloc[0]
        st.markdown(f"""
        <div class="card">
            <h3>{top_product['Buah']}</h3>
            <p>Total: {top_product['Total Penjualan (kg)']} kg</p>
            <p>Rata-rata: {top_product['Rata-rata Mingguan (kg)']} kg/minggu</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik penjualan
        st.markdown("### Grafik Penjualan")
        fig, ax = plt.subplots()
        metrics.sort_values('Total Penjualan (kg)').plot(
            x='Buah', y='Total Penjualan (kg)', kind='barh', ax=ax)
        st.pyplot(fig)
        
        # Kalkulator EOQ
        st.markdown("### Kalkulator EOQ Mingguan")
        selected = st.selectbox("Pilih Buah:", metrics['Buah'])
        
        if selected:
            data = metrics[metrics['Buah'] == selected].iloc[0]
            
            with st.expander("Parameter EOQ"):
                col1, col2 = st.columns(2)
                with col1:
                    biaya_pesan = st.number_input("Biaya Pemesanan (Rp)", value=10000)
                with col2:
                    biaya_simpan = st.number_input("Biaya Penyimpanan (Rp/kg/minggu)", value=500)
                
                # Hitung EOQ mingguan
                permintaan = data['Rata-rata Mingguan (kg)']
                eoq = np.sqrt((2 * permintaan * biaya_pesan) / biaya_simpan)
                
                st.metric("Jumlah Pesanan Optimal", f"{round(eoq, 2)} kg/minggu")

# Footer
st.markdown("---")
st.caption("Aplikasi Analisis Penjualan Buah")
