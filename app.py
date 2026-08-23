import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Infografis Performa & Strategi Klinik",
    page_icon="🏥",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #1E88E5;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 14px;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-sub {
        font-size: 13px;
        color: #555555;
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# Load and process database dynamically
@st.cache_data
def load_data():
    excel_path = 'Data Transaksi (6).xlsx'
    df = pd.read_excel(excel_path, sheet_name=0)
    df_clean = df.dropna(subset=['No. Reg/Invoice']).copy()
    
    def classify_patient_type(row):
        jp = str(row['Jenis Pasien']).strip()
        if jp in ['Local', 'BPJS']:
            return 'Lokal'
        elif jp in ['Tourist', 'Expat', 'VIP']:
            return 'Bule'
        else:
            wn = str(row['Negara/WN']).strip()
            if wn in ['INDONESIA', 'nan', '']:
                return 'Lokal'
            else:
                return 'Bule'

    df_clean['Patient_Category'] = df_clean.apply(classify_patient_type, axis=1)

    def classify_service(row):
        nama = str(row['Nama Pasien']).upper()
        total = row['Total']
        p_cat = row['Patient_Category']
        
        if 'PHARMACY' in nama:
            return 'Farmasi'
        elif p_cat == 'Lokal' and total == 30000.0:
            return 'Medical Check Up'
        elif p_cat == 'Bule' and total == 50000.0:
            return 'Medical Check Up'
        else:
            return 'Perawatan'

    df_clean['Service_Type'] = df_clean.apply(classify_service, axis=1)
    return df_clean

df_data = load_data()

# Sidebar Navigation
st.sidebar.title("🏥 Navigasi Klinik")
st.sidebar.markdown("---")
page_option = st.sidebar.radio(
    "PILIH HALAMAN:",
    ["Historical Data", "Future Prospects"]
)

# ==========================================
# PAGE 1: HISTORICAL DATA
# ==========================================
if page_option == "Historical Data":
    st.title("📊 Historical Data Performance")
    st.markdown("Ringkasan performa operasional & keuangan klinik berdasarkan database transaksi terkini (`Data Transaksi (6).xlsx`).")
    st.markdown("---")
    
    # Calculate Metrics dynamically
    total_rev = df_data['Total'].sum()
    rev_bule = df_data[df_data['Patient_Category'] == 'Bule']['Total'].sum()
    rev_lokal = df_data[df_data['Patient_Category'] == 'Lokal']['Total'].sum()
    
    total_pat = len(df_data)
    pat_bule = len(df_data[df_data['Patient_Category'] == 'Bule'])
    pat_lokal = len(df_data[df_data['Patient_Category'] == 'Lokal'])
    
    mcu_df = df_data[df_data['Service_Type'] == 'Medical Check Up']
    mcu_total = len(mcu_df)
    mcu_bule = len(mcu_df[mcu_df['Patient_Category'] == 'Bule'])
    mcu_lokal = len(mcu_df[mcu_df['Patient_Category'] == 'Lokal'])
    mcu_rev_bule = mcu_df[mcu_df['Patient_Category'] == 'Bule']['Total'].sum()
    mcu_rev_lokal = mcu_df[mcu_df['Patient_Category'] == 'Lokal']['Total'].sum()

    # --- TOP SUMMARY CARDS ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2E7D32;">
            <div class="metric-title">💰 TOTAL PENDAPATAN</div>
            <div class="metric-value">Rp {total_rev:,.0f}</div>
            <div class="metric-sub">Bule: Rp {rev_bule:,.0f} ({(rev_bule/total_rev)*100:.1f}%)<br>Lokal: Rp {rev_lokal:,.0f} ({(rev_lokal/total_rev)*100:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #1976D2;">
            <div class="metric-title">👥 TOTAL PASIEN DATANG</div>
            <div class="metric-value">{total_pat} Pasien</div>
            <div class="metric-sub">Bule: <b>{pat_bule} Pasien</b> ({(pat_bule/total_pat)*100:.1f}%)<br>Lokal: <b>{pat_lokal} Pasien</b> ({(pat_lokal/total_pat)*100:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #F57C00;">
            <div class="metric-title">🩺 TOTAL MEDICAL CHECK UP (MCU)</div>
            <div class="metric-value">{mcu_total} Pasien</div>
            <div class="metric-sub">Bule: <b>{mcu_bule} Pasien</b> (Rp {mcu_rev_bule:,.0f})<br>Lokal: <b>{mcu_lokal} Pasien</b> (Rp {mcu_rev_lokal:,.0f})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- PIE CHART: KLASIFIKASI PASIEN & PENDAPATAN ---
    st.subheader("🥧 Distribusi Pasien & Pendapatan (Bule vs Lokal)")
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        df_pasien = pd.DataFrame({
            "Kategori": ["Pasien Lokal", "Pasien Bule"],
            "Jumlah": [pat_lokal, pat_bule]
        })
        fig_pasien = px.pie(
            df_pasien, values="Jumlah", names="Kategori", 
            title="Persentase Jumlah Pasien",
            color_discrete_sequence=["#29B6F6", "#FF7043"],
            hole=0.4
        )
        fig_pasien.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig_pasien, use_container_width=True)

    with col_pie2:
        df_rev = pd.DataFrame({
            "Kategori": ["Pasien Lokal", "Pasien Bule"],
            "Pendapatan": [rev_lokal, rev_bule]
        })
        fig_rev = px.pie(
            df_rev, values="Pendapatan", names="Kategori", 
            title="Persentase Pendapatan (Rupiah)",
            color_discrete_sequence=["#29B6F6", "#FF7043"],
            hole=0.4
        )
        fig_rev.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown("---")

    # --- HORIZONTAL BAR CHARTS (REKAPAN BULE & LOKAL) ---
    st.subheader("📊 Detail Transaksi per Layanan (Perawatan, MCU, Farmasi)")
    col_bar1, col_bar2 = st.columns(2)
    
    bule_data = df_data[df_data['Patient_Category'] == 'Bule'].groupby('Service_Type').agg(
        Count=('Total', 'count'), Revenue=('Total', 'sum')
    ).reset_index()

    lokal_data = df_data[df_data['Patient_Category'] == 'Lokal'].groupby('Service_Type').agg(
        Count=('Total', 'count'), Revenue=('Total', 'sum')
    ).reset_index()

    with col_bar1:
        st.markdown("##### 🌍 Rekapan Pasien Bule")
        fig_bule = px.bar(
            bule_data, 
            y="Service_Type", 
            x="Revenue", 
            orientation="h",
            text="Count",
            title="Pendapatan & Pasien Bule per Layanan",
            color_discrete_sequence=["#FF7043"]
        )
        fig_bule.update_traces(
            texttemplate="%{x:,.0f} IDR (%{text} Pasien)", 
            textposition="inside"
        )
        fig_bule.update_layout(xaxis_title="Total Pendapatan (Rp)", yaxis_title="")
        st.plotly_chart(fig_bule, use_container_width=True)

    with col_bar2:
        st.markdown("##### 🇮🇩 Rekapan Pasien Lokal")
        fig_lokal = px.bar(
            lokal_data, 
            y="Service_Type", 
            x="Revenue", 
            orientation="h",
            text="Count",
            title="Pendapatan & Pasien Lokal per Layanan",
            color_discrete_sequence=["#29B6F6"]
        )
        fig_lokal.update_traces(
            texttemplate="%{x:,.0f} IDR (%{text} Pasien)", 
            textposition="inside"
        )
        fig_lokal.update_layout(xaxis_title="Total Pendapatan (Rp)", yaxis_title="")
        st.plotly_chart(fig_lokal, use_container_width=True)

    st.markdown("---")

    # --- TOP CASES & DIAGNOSA ---
    st.subheader("📋 Top Kasus Penyakit & Layanan Ditangani")
    col_case1, col_case2 = st.columns(2)
    
    with col_case1:
        st.markdown("##### 🌍 Top Kasus Diagnosa Pasien Bule")
        bule_diag = df_data[(df_data['Patient_Category'] == 'Bule') & (df_data['Nama Diagnosa'].notna())]['Nama Diagnosa'].value_counts().reset_index()
        bule_diag.columns = ['Diagnosa', 'Jumlah']
        bule_diag = bule_diag.sort_values('Jumlah', ascending=True)
        
        fig_cb = px.bar(
            bule_diag, y="Diagnosa", x="Jumlah", orientation="h",
            text="Jumlah", color_discrete_sequence=["#AB47BC"]
        )
        fig_cb.update_traces(textposition="outside")
        fig_cb.update_layout(xaxis_title="Jumlah Kasus Ditangani", yaxis_title="")
        st.plotly_chart(fig_cb, use_container_width=True)

    with col_case2:
        st.markdown("##### 🇮🇩 Top Kasus Diagnosa Pasien Lokal")
        lokal_diag = df_data[(df_data['Patient_Category'] == 'Lokal') & (df_data['Nama Diagnosa'].notna())]['Nama Diagnosa'].value_counts().head(7).reset_index()
        lokal_diag.columns = ['Diagnosa', 'Jumlah']
        lokal_diag = lokal_diag.sort_values('Jumlah', ascending=True)
        
        fig_cl = px.bar(
            lokal_diag, y="Diagnosa", x="Jumlah", orientation="h",
            text="Jumlah", color_discrete_sequence=["#26A69A"]
        )
        fig_cl.update_traces(textposition="outside")
        fig_cl.update_layout(xaxis_title="Jumlah Kasus Ditangani", yaxis_title="")
        st.plotly_chart(fig_cl, use_container_width=True)

# ==========================================
# PAGE 2: FUTURE PROSPECTS
# ==========================================
elif page_option == "Future Prospects":
    st.title("🎯 Future Prospects & Financial Target")
    st.markdown("Strategi & rincian target operasional harian, mingguan, dan bulanan untuk mencapai profitabilitas optimal.")
    st.markdown("---")
    
    # Financial Back-Calculations
    target_bulan = 325000000
    profit_margin = 0.25
    profit_bulan = target_bulan * profit_margin
    target_minggu = target_bulan / 4
    target_hari = target_bulan / 30
    profit_hari = profit_bulan / 30

    # --- TOP SUMMARY TARGET CARDS ---
    st.subheader("💡 Rangkuman Target Pendapatan & Profitabilitas (25% Margin)")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    
    with col_t1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2E7D32;">
            <div class="metric-title">🎯 TARGET BULANAN</div>
            <div class="metric-value">Rp {target_bulan:,.0f}</div>
            <div class="metric-sub">Est. Profit (25%): <b>Rp {profit_bulan:,.0f}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_t2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #1565C0;">
            <div class="metric-title">📅 TARGET MINGGUAN</div>
            <div class="metric-value">Rp {target_minggu:,.0f}</div>
            <div class="metric-sub">Est. Profit: <b>Rp {target_minggu*profit_margin:,.0f}</b> / mg</div>
        </div>
        """, unsafe_allow_html=True)

    with col_t3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #E65100;">
            <div class="metric-title">☀️ TARGET HARIAN</div>
            <div class="metric-value">Rp {target_hari:,.0f}</div>
            <div class="metric-sub">Est. Profit: <b>Rp {profit_hari:,.0f}</b> / hari</div>
        </div>
        """, unsafe_allow_html=True)

    with col_t4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #6A1B9A;">
            <div class="metric-title">📈 MARGIN PROFIT</div>
            <div class="metric-value">25 %</div>
            <div class="metric-sub">Net Profit Margin Target</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- TARGET RINCIAN PER LAYANAN TABLE ---
    st.subheader("📌 Rincian Target Operasional per Layanan & Kategori Pasien")
    st.markdown("*(Menyesuaikan penyesuaian tarif Agustus: MCU Bule Rp 50.000 & MCU Lokal Rp 30.000)*")
    
    target_table_data = [
        {
            "Kategori Pasien": "Pasien Bule 🌍",
            "Layanan": "Perawatan & Emergency Services",
            "Target Pasien / Hari": "1.6 Pasien",
            "Target Pasien / Bulan": "48 Pasien",
            "Avg Basket Size (Rp)": "Rp 4,500,000",
            "Target Omset / Hari (Rp)": "Rp 7,200,000",
            "Target Omset / Bulan (Rp)": "Rp 216,000,000",
            "Kontribusi (%)": "66.5%"
        },
        {
            "Kategori Pasien": "Pasien Bule 🌍",
            "Layanan": "Medical Check Up (MCU)",
            "Target Pasien / Hari": "5.0 Pasien",
            "Target Pasien / Bulan": "150 Pasien",
            "Avg Basket Size (Rp)": "Rp 50,000",
            "Target Omset / Hari (Rp)": "Rp 250,000",
            "Target Omset / Bulan (Rp)": "Rp 7,500,000",
            "Kontribusi (%)": "2.3%"
        },
        {
            "Kategori Pasien": "Pasien Lokal 🇮🇩",
            "Layanan": "Perawatan & Poli Umum",
            "Target Pasien / Hari": "7.0 Pasien",
            "Target Pasien / Bulan": "210 Pasien",
            "Avg Basket Size (Rp)": "Rp 350,000",
            "Target Omset / Hari (Rp)": "Rp 2,450,000",
            "Target Omset / Bulan (Rp)": "Rp 73,500,000",
            "Kontribusi (%)": "22.6%"
        },
        {
            "Kategori Pasien": "Pasien Lokal 🇮🇩",
            "Layanan": "Medical Check Up (MCU)",
            "Target Pasien / Hari": "15.0 Pasien",
            "Target Pasien / Bulan": "450 Pasien",
            "Avg Basket Size (Rp)": "Rp 30,000",
            "Target Omset / Hari (Rp)": "Rp 450,000",
            "Target Omset / Bulan (Rp)": "Rp 13,500,000",
            "Kontribusi (%)": "4.2%"
        },
        {
            "Kategori Pasien": "Pasien Lokal 🇮🇩",
            "Layanan": "Farmasi & Obat Rawat Jalan",
            "Target Pasien / Hari": "8.0 Pasien",
            "Target Pasien / Bulan": "240 Pasien",
            "Avg Basket Size (Rp)": "Rp 60,417",
            "Target Omset / Hari (Rp)": "Rp 483,336",
            "Target Omset / Bulan (Rp)": "Rp 14,500,080",
            "Kontribusi (%)": "4.5%"
        }
    ]
    
    df_target_table = pd.DataFrame(target_table_data)
    st.dataframe(df_target_table, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Visual Breakdown of Targets
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### 📊 Proporsi Target Pendapatan per Layanan")
        df_prop = pd.DataFrame({
            "Layanan": [
                "Perawatan Bule", "MCU Bule", 
                "Perawatan Lokal", "MCU Lokal", "Farmasi Lokal"
            ],
            "Target Omset Harian (Rp)": [7200000, 250000, 2450000, 450000, 483336]
        })
        fig_prop = px.bar(
            df_prop, x="Layanan", y="Target Omset Harian (Rp)", color="Layanan",
            text_auto=".2s", title="Target Omset Harian per Layanan (Rp)"
        )
        fig_prop.update_layout(showlegend=False, xaxis_title="", yaxis_title="Rupiah / Hari")
        st.plotly_chart(fig_prop, use_container_width=True)

    with col_chart2:
        st.markdown("##### 👥 Target Volume Pasien Harian")
        df_vol = pd.DataFrame({
            "Layanan": [
                "Perawatan Bule", "MCU Bule", 
                "Perawatan Lokal", "MCU Lokal", "Farmasi Lokal"
            ],
            "Pasien / Hari": [1.6, 5.0, 7.0, 15.0, 8.0]
        })
        fig_vol = px.bar(
            df_vol, x="Layanan", y="Pasien / Hari", color="Layanan",
            text="Pasien / Hari", title="Target Volume Pasien Datang per Hari"
        )
        fig_vol.update_traces(textposition="outside")
        fig_vol.update_layout(showlegend=False, xaxis_title="", yaxis_title="Jumlah Pasien / Hari")
        st.plotly_chart(fig_vol, use_container_width=True)
