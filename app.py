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
    st.markdown("Ringkasan performa operasional & keuangan klinik berdasarkan data transaksi historis.")
    st.markdown("---")
    
    # --- TOP SUMMARY CARDS (Ramping / Compact Blocks) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #2E7D32;">
            <div class="metric-title">💰 TOTAL PENDAPATAN</div>
            <div class="metric-value">Rp 144,103,788</div>
            <div class="metric-sub">Bule: Rp 103,867,263 (72.1%)<br>Lokal: Rp 40,236,525 (27.9%)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #1976D2;">
            <div class="metric-title">👥 TOTAL PASIEN DATANG</div>
            <div class="metric-value">477 Pasien</div>
            <div class="metric-sub">Bule: <b>43 Pasien</b> (9%)<br>Lokal: <b>434 Pasien</b> (91%)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" style="border-left-color: #F57C00;">
            <div class="metric-title">🩺 TOTAL MEDICAL CHECK UP (MCU)</div>
            <div class="metric-value">285 Pasien</div>
            <div class="metric-sub">Bule: <b>4 Pasien</b> (Rp 400.000)<br>Lokal: <b>281 Pasien</b> (Rp 14.050.000)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- PIE CHART: KLASIFIKASI PASIEN & PENDAPATAN ---
    st.subheader("🥧 Distribusi Pasien & Pendapatan (Bule vs Lokal)")
    
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        # Pie Chart Jumlah Pasien
        df_pasien = pd.DataFrame({
            "Kategori": ["Pasien Lokal", "Pasien Bule"],
            "Jumlah": [434, 43]
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
        # Pie Chart Pendapatan
        df_rev = pd.DataFrame({
            "Kategori": ["Pasien Lokal", "Pasien Bule"],
            "Pendapatan": [40236525, 103867263]
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

    # --- HORIZONTAL BAR CHARTS (DETAIL TRANSAKSI PER CATEGORY) ---
    st.subheader("📊 Detail Transaksi per Layanan (Perawatan, MCU, Farmasi)")
    
    col_bar1, col_bar2 = st.columns(2)
    
    with col_bar1:
        st.markdown("##### 🌍 Rekapan Pasien Bule")
        # Horizontal Bar Chart Bule
        df_bule_layanan = pd.DataFrame({
            "Layanan": ["Farmasi", "MCU", "Perawatan"],
            "Jumlah Pasien": [17, 4, 22],
            "Pendapatan (Rp)": [3172615, 400000, 100294648]
        })
        fig_bule = px.bar(
            df_bule_layanan, 
            y="Layanan", 
            x="Pendapatan (Rp)", 
            orientation="h",
            text="Jumlah Pasien",
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
        # Horizontal Bar Chart Lokal
        df_lokal_layanan = pd.DataFrame({
            "Layanan": ["Farmasi", "MCU", "Perawatan"],
            "Jumlah Pasien": [81, 281, 72],
            "Pendapatan (Rp)": [3001341, 14050000, 23185184]
        })
        fig_lokal = px.bar(
            df_lokal_layanan, 
            y="Layanan", 
            x="Pendapatan (Rp)", 
            orientation="h",
            text="Jumlah Pasien",
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

    # --- TOP CASES & FARMASI (BAR CHARTS) ---
    st.subheader("📋 Top Kasus Penyakit & Layanan Ditangani")
    
    col_case1, col_case2 = st.columns(2)
    
    with col_case1:
        st.markdown("##### 🌍 Top Kasus Diagnosa Pasien Bule")
        df_case_bule = pd.DataFrame({
            "Kasus / Diagnosa": [
                "Fracture Humerus (Patah Tulang)",
                "Dengue Fever (DBD)",
                "Diarrhoea & Gastroenteritis",
                "Open Wound / Cut Foot",
                "Sprain Foot (Terkilir)",
                "Cellulitis / Infeksi Kulit",
                "Rabies Immunization"
            ],
            "Jumlah Cases": [1, 1, 2, 1, 1, 1, 2]
        }).sort_values("Jumlah Cases", ascending=True)
        
        fig_cb = px.bar(
            df_case_bule,
            y="Kasus / Diagnosa",
            x="Jumlah Cases",
            orientation="h",
            text="Jumlah Cases",
            color_discrete_sequence=["#AB47BC"]
        )
        fig_cb.update_traces(textposition="outside")
        fig_cb.update_layout(xaxis_title="Jumlah Kasus Ditangani", yaxis_title="")
        st.plotly_chart(fig_cb, use_container_width=True)

    with col_case2:
        st.markdown("##### 🇮🇩 Top Kasus Diagnosa Pasien Lokal")
        df_case_lokal = pd.DataFrame({
            "Kasus / Diagnosa": [
                "Scabies (Penyakit Kulit)",
                "Myalgia (Nyeri Otot)",
                "Superficial Injury / Luka",
                "Fever / Demam",
                "Common Cold / ISPA",
                "Dyspepsia (Maag)",
                "Open Wound (Luka Terbuka)"
            ],
            "Jumlah Cases": [4, 4, 3, 3, 2, 2, 2]
        }).sort_values("Jumlah Cases", ascending=True)
        
        fig_cl = px.bar(
            df_case_lokal,
            y="Kasus / Diagnosa",
            x="Jumlah Cases",
            orientation="h",
            text="Jumlah Cases",
            color_discrete_sequence=["#26A69A"]
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
    target_minggu = target_bulan / 4 # 4 minggu dalam 1 bulan
    target_hari = target_bulan / 30 # 30 hari dalam 1 bulan
    profit_hari = profit_bulan / 30

    # --- TOP SUMMARY TARGET CARDS ---
    st.subheader("💡 Rangkuman Target Pendapatan & Profitabilitas (25% Margin)")
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    
    with col_t1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2E7D32;">
            <div class="metric-title">🎯 TARGET BULANAN</div>
            <div class="metric-value">Rp {target_bulan:,.0f}</div>
            <div class="metric-sub">Est. Profit: <b>Rp {profit_bulan:,.0f}</b></div>
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
            <div class="metric-sub">Net Margin Target Klinik</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- TARGET RINCIAN PER LAYANAN (BULE vs LOKAL) ---
    st.subheader("📌 Rincian Target Operasional per Layanan & Kategori Pasien")
    st.markdown("*(Menyesuaikan penyesuaian tarif Agustus: MCU Bule Rp 50.000 & MCU Lokal Rp 30.000)*")
    
    # Table Target Data
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
            df_prop,
            x="Layanan",
            y="Target Omset Harian (Rp)",
            color="Layanan",
            text_auto=".2s",
            title="Target Omset Harian per Layanan (Rp)"
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
            df_vol,
            x="Layanan",
            y="Pasien / Hari",
            color="Layanan",
            text="Pasien / Hari",
            title="Target Volume Pasien Datang per Hari"
        )
        fig_vol.update_traces(textposition="outside")
        fig_vol.update_layout(showlegend=False, xaxis_title="", yaxis_title="Jumlah Pasien / Hari")
        st.plotly_chart(fig_vol, use_container_width=True)
