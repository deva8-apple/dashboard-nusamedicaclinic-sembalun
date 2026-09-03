import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(
    page_title="Infografis Performa & Strategi Klinik",
    page_icon="🏥",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #1E88E5;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 14px; color: #6c757d; font-weight: 600; margin-bottom: 5px; }
    .metric-value { font-size: 22px; font-weight: bold; color: #2c3e50; }
    .metric-sub { font-size: 13px; color: #555555; margin-top: 3px; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR: NAVIGATION MENU
# -------------------------------------------------------------
st.sidebar.title("🏥 Menu Navigasi")

page_option = st.sidebar.radio(
    "PILIH TAMPILAN DASHBOARD:",
    ["Historical Monthly Trend 📈", "Monthly Detail Analysis 📊", "Future Prospects 🎯"]
)

# File Mapping for All Months
file_mapping = {
    "Juni 2026": {
        "tx": "Rekap Bulanan Juni 2026.xlsx",
        "mcu": "MCU Recap Juni 2026.xlsx"
    },
    "Juli 2026": {
        "tx": "Rekap Bulanan Juli 2026.xlsx",
        "mcu": "MCU Recap Juli 2026.xlsx"
    },
    "Agustus 2026": {
        "tx": "Rekap Bulanan Agustus 2026.xlsx",
        "mcu": "MCU Recap Aug 2026.xlsx"
    },
    "September 2026": {
        "tx": "Rekap Bulanan September 2026.xlsx",
        "mcu": "MCU Recap September 2026.xlsx"
    }
}

# Data Extraction Functions
@st.cache_data
def load_tx_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    try:
        df_tx = pd.read_excel(file_path, sheet_name='Data Transaksi')
    except:
        try:
            df_tx = pd.read_excel(file_path, sheet_name=0)
        except:
            return pd.DataFrame()
        
    if 'No. Reg/Invoice' in df_tx.columns:
        df_tx_clean = df_tx.dropna(subset=['No. Reg/Invoice']).copy()
    else:
        df_tx_clean = df_tx.dropna(how='all').copy()
    
    if 'Total' in df_tx_clean.columns:
        df_tx_clean['Total'] = pd.to_numeric(df_tx_clean['Total'], errors='coerce').fillna(0)
    else:
        df_tx_clean['Total'] = 0.0

    def classify_patient_type(row):
        jp = str(row.get('Jenis Pasien', '')).strip()
        if jp in ['Local', 'BPJS']:
            return 'Lokal'
        elif jp in ['Tourist', 'Expat', 'VIP']:
            return 'Bule'
        else:
            wn = str(row.get('Negara/WN', '')).strip()
            if wn in ['INDONESIA', 'nan', '']:
                return 'Lokal'
            else:
                return 'Bule'

    df_tx_clean['Patient_Category'] = df_tx_clean.apply(classify_patient_type, axis=1)

    def classify_service(row):
        nama = str(row.get('Nama Pasien', '')).upper()
        tot = row.get('Total', 0)
        if 'PHARMACY' in nama:
            return 'Farmasi'
        elif tot in [30000.0, 50000.0]:
            return 'Medical Check Up'
        else:
            return 'Perawatan'

    df_tx_clean['Service_Type'] = df_tx_clean.apply(classify_service, axis=1)
    
    diag_col = None
    for col in ['Nama Diagnosa', 'Nama Diagnosis', 'Diagnosa', 'Diag.']:
        if col in df_tx_clean.columns:
            diag_col = col
            break
            
    if diag_col:
        df_tx_clean['Diagnosa_Clean'] = df_tx_clean[diag_col].astype(str).str.strip()
        df_tx_clean['Diagnosa_Clean'] = df_tx_clean['Diagnosa_Clean'].replace(['nan', 'NaN', 'None', '', '-'], None)
    else:
        df_tx_clean['Diagnosa_Clean'] = None

    return df_tx_clean

@st.cache_data
def load_mcu_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        df_mcu = pd.read_excel(file_path, sheet_name='Runners data')
    except:
        try:
            df_mcu = pd.read_excel(file_path, sheet_name=0)
        except:
            return pd.DataFrame()
        
    # Find Name column flexibly
    name_col = None
    for col in df_mcu.columns:
        if 'NAMA' in str(col).upper() or 'PATIENT' in str(col).upper():
            name_col = col
            break
            
    if name_col:
        df_mcu_clean = df_mcu.dropna(subset=[name_col]).copy()
    else:
        df_mcu_clean = df_mcu.dropna(how='all').copy()

    # Find Country column flexibly
    country_col = None
    for col in df_mcu.columns:
        if any(term in str(col).upper() for term in ['NEGARA', 'COUNTRY', 'WN', 'KEWARGANEGARAAN', 'ASAL']):
            country_col = col
            break

    def classify_mcu_country(row):
        if country_col:
            val = str(row.get(country_col, '')).strip().upper()
            if val in ['INDONESIA', 'ID', 'IDN', 'LOKAL', 'LOCAL', 'NAN', '', 'NONE', '-']:
                return 'Lokal'
            else:
                return 'Bule'
        return 'Lokal'

    df_mcu_clean['Patient_Category'] = df_mcu_clean.apply(classify_mcu_country, axis=1)
    df_mcu_clean['Service_Type'] = 'Medical Check Up'
    df_mcu_clean['Total'] = df_mcu_clean['Patient_Category'].apply(lambda x: 50000.0 if x == 'Bule' else 30000.0)
    return df_mcu_clean


# -------------------------------------------------------------
# PAGE 1: HISTORICAL MONTHLY TREND 📈 (DASHBOARD KHUSUS TREN BULANAN)
# -------------------------------------------------------------
if page_option == "Historical Monthly Trend 📈":
    st.title("📈 Historical Monthly Trend Dashboard")
    st.markdown("Dashboard perbandingan tren bulanan untuk memantau pertumbuhan pendapatan, jumlah pasien MCU, dan breakdown kategori layanan.")
    st.markdown("---")

    monthly_summary = []
    mcu_summary = []
    service_summary = []

    for month_name, files in file_mapping.items():
        df_tx_m = load_tx_data(files["tx"])
        df_mcu_m = load_mcu_data(files["mcu"])

        if not df_tx_m.empty:
            # Exact Total Income from Data Transaksi
            tot_inc = df_tx_m['Total'].sum()
            monthly_summary.append({
                "Bulan": month_name,
                "Total Income (Rp)": tot_inc
            })

            # Service Type Breakdown (Synced with df_mcu)
            if not df_mcu_m.empty:
                mcu_rev_tot = df_mcu_m['Total'].sum()
            else:
                mcu_rev_tot = df_tx_m[df_tx_m['Service_Type'] == 'Medical Check Up']['Total'].sum()
                
            farmasi_rev_tot = df_tx_m[df_tx_m['Service_Type'] == 'Farmasi']['Total'].sum()
            perawatan_rev_tot = tot_inc - mcu_rev_tot - farmasi_rev_tot
            if perawatan_rev_tot < 0:
                perawatan_rev_tot = df_tx_m[df_tx_m['Service_Type'] == 'Perawatan']['Total'].sum()

            srv_grp = pd.DataFrame([
                {"Service_Type": "Medical Check Up", "Total": mcu_rev_tot, "Bulan": month_name},
                {"Service_Type": "Farmasi", "Total": farmasi_rev_tot, "Bulan": month_name},
                {"Service_Type": "Perawatan", "Total": perawatan_rev_tot, "Bulan": month_name}
            ])
            service_summary.append(srv_grp)

        # MCU Patient Volume Count
        if not df_mcu_m.empty:
            mcu_lokal = len(df_mcu_m[df_mcu_m['Patient_Category'] == 'Lokal'])
            mcu_turis = len(df_mcu_m[df_mcu_m['Patient_Category'] == 'Bule'])
            mcu_summary.append({
                "Bulan": month_name,
                "Lokal": mcu_lokal,
                "Turis / Bule": mcu_turis
            })
        elif not df_tx_m.empty:
            mcu_tx = df_tx_m[df_tx_m['Service_Type'] == 'Medical Check Up']
            mcu_lokal = len(mcu_tx[mcu_tx['Patient_Category'] == 'Lokal'])
            mcu_turis = len(mcu_tx[mcu_tx['Patient_Category'] == 'Bule'])
            mcu_summary.append({
                "Bulan": month_name,
                "Lokal": mcu_lokal,
                "Turis / Bule": mcu_turis
            })

    df_income_trend = pd.DataFrame(monthly_summary)
    df_mcu_trend = pd.DataFrame(mcu_summary)
    df_service_trend = pd.concat(service_summary, ignore_index=True) if service_summary else pd.DataFrame()

    if df_income_trend.empty and df_mcu_trend.empty:
        st.warning("⚠️ **Belum ada data bulanan yang di-upload ke repository GitHub.**")
        st.info("Silakan upload file Excel transaksi bulanan Anda untuk melihat tren perkembangan klinik.")
        st.stop()

    # --- BAR CHART 1: PERKEMBANGAN TOTAL INCOME KLINIK TIAP BULAN ---
    st.subheader("1. 💰 Perkembangan Total Income Klinik per Bulan (Termasuk Pajak)")
    if not df_income_trend.empty:
        fig_inc = px.bar(
            df_income_trend,
            x="Bulan",
            y="Total Income (Rp)",
            text_auto=",.0f",
            title="Total Pendapatan Bersih & Pajak per Bulan (Rupiah)",
            color="Bulan",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_inc.update_traces(textposition="outside", textfont_size=13)
        fig_inc.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Total Pendapatan (Rp)",
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_inc, use_container_width=True)
    else:
        st.info("Data Total Income belum tersedia.")

    st.markdown("---")

    # --- BAR CHART 2: PROGRESS PASIEN MCU TIAP BULAN (LOKAL VS TURIS) ---
    st.subheader("2. 🩺 Progress Pasien MCU per Bulan (Lokal vs Turis)")
    if not df_mcu_trend.empty:
        df_mcu_melt = pd.melt(
            df_mcu_trend,
            id_vars=["Bulan"],
            value_vars=["Lokal", "Turis / Bule"],
            var_name="Kategori Pasien",
            value_name="Jumlah Pasien"
        )
        fig_mcu = px.bar(
            df_mcu_melt,
            x="Bulan",
            y="Jumlah Pasien",
            color="Kategori Pasien",
            barmode="group",
            text="Jumlah Pasien",
            title="Perbandingan Jumlah Pasien MCU (Lokal vs Turis)",
            color_discrete_map={"Lokal": "#29B6F6", "Turis / Bule": "#FF7043"}
        )
        fig_mcu.update_traces(textposition="outside", textfont_size=12)
        fig_mcu.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Jumlah Pasien MCU",
            legend_title="Kategori Pasien",
            height=400,
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_mcu, use_container_width=True)
    else:
        st.info("Data Pasien MCU belum tersedia.")

    st.markdown("---")

    # --- BAR CHART 3: KATEGORI PENDAPATAN PER BULAN (MCU, PERAWATAN, FARMASI) ---
    st.subheader("3. 📊 Kategori Pendapatan per Bulan (MCU, Perawatan/Tindakan, Farmasi)")
    if not df_service_trend.empty:
        fig_srv = px.bar(
            df_service_trend,
            x="Bulan",
            y="Total",
            color="Service_Type",
            barmode="group",
            text_auto=",.0f",
            title="Breakdown Pendapatan per Kategori Layanan (Rupiah)",
            color_discrete_map={
                "Perawatan": "#4CAF50",
                "Medical Check Up": "#FF9800",
                "Farmasi": "#9C27B0"
            }
        )
        fig_srv.update_traces(textposition="outside", textfont_size=11)
        fig_srv.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Pendapatan (Rp)",
            legend_title="Kategori Layanan",
            height=430,
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_srv, use_container_width=True)
    else:
        st.info("Data Kategori Pendapatan belum tersedia.")


# -------------------------------------------------------------
# PAGE 2: MONTHLY DETAIL ANALYSIS 📊 (DASHBOARD FILTER BULANAN)
# -------------------------------------------------------------
elif page_option == "Monthly Detail Analysis 📊":
    st.sidebar.markdown("---")
    st.sidebar.title("🗓️ Filter Periode")
    selected_month = st.sidebar.selectbox(
        "PILIH BULAN TRANSAKSI:",
        ["Juni 2026", "Juli 2026", "Agustus 2026", "September 2026"]
    )

    current_files = file_mapping[selected_month]
    df_tx = load_tx_data(current_files["tx"])
    df_mcu = load_mcu_data(current_files["mcu"])

    if df_tx.empty and df_mcu.empty:
        st.warning(f"⚠️ **Data {selected_month} Belum Tersedia / Sedang Diperbarui.**")
        st.info(f"Silakan upload file `{current_files['tx']}` dan `{current_files['mcu']}` ke repository GitHub Anda.")
        st.stop()

    st.title(f"📊 Monthly Detail Analysis ({selected_month})")
    st.markdown(f"Ringkasan performa operasional & detail transaksi klinik bulan **{selected_month}**.")
    st.markdown("---")

    # Exact Total Revenue directly from Data Transaksi file
    total_rev = df_tx['Total'].sum() if not df_tx.empty else 0
    rev_bule = df_tx[df_tx['Patient_Category'] == 'Bule']['Total'].sum() if not df_tx.empty else 0
    rev_lokal = df_tx[df_tx['Patient_Category'] == 'Lokal']['Total'].sum() if not df_tx.empty else 0

    total_pat = len(df_tx) if not df_tx.empty else 0
    pat_bule = len(df_tx[df_tx['Patient_Category'] == 'Bule']) if not df_tx.empty else 0
    pat_lokal = len(df_tx[df_tx['Patient_Category'] == 'Lokal']) if not df_tx.empty else 0

    # MCU Calculations (Sync between df_mcu and df_tx)
    mcu_tx = df_tx[df_tx['Service_Type'] == 'Medical Check Up'] if not df_tx.empty else pd.DataFrame()
    if not df_mcu.empty:
        mcu_total = len(df_mcu)
        mcu_bule = len(df_mcu[df_mcu['Patient_Category'] == 'Bule'])
        mcu_lokal = len(df_mcu[df_mcu['Patient_Category'] == 'Lokal'])
        mcu_rev_bule = df_mcu[df_mcu['Patient_Category'] == 'Bule']['Total'].sum()
        mcu_rev_lokal = df_mcu[df_mcu['Patient_Category'] == 'Lokal']['Total'].sum()
    else:
        mcu_total = len(mcu_tx)
        mcu_bule = len(mcu_tx[mcu_tx['Patient_Category'] == 'Bule'])
        mcu_lokal = len(mcu_tx[mcu_tx['Patient_Category'] == 'Lokal'])
        mcu_rev_bule = mcu_tx[mcu_tx['Patient_Category'] == 'Bule']['Total'].sum() if not mcu_tx.empty else 0
        mcu_rev_lokal = mcu_tx[mcu_tx['Patient_Category'] == 'Lokal']['Total'].sum() if not mcu_tx.empty else 0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2E7D32;">
            <div class="metric-title">💰 TOTAL PENDAPATAN ({selected_month.upper()})</div>
            <div class="metric-value">Rp {total_rev:,.0f}</div>
            <div class="metric-sub">Bule: Rp {rev_bule:,.0f} ({(rev_bule/total_rev)*100 if total_rev else 0:.1f}%)<br>Lokal: Rp {rev_lokal:,.0f} ({(rev_lokal/total_rev)*100 if total_rev else 0:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #1976D2;">
            <div class="metric-title">👥 TOTAL TRANSAKSI PASIEN</div>
            <div class="metric-value">{total_pat} Transaksi</div>
            <div class="metric-sub">Bule: <b>{pat_bule} Pasien</b> ({(pat_bule/total_pat)*100 if total_pat else 0:.1f}%)<br>Lokal: <b>{pat_lokal} Pasien</b> ({(pat_lokal/total_pat)*100 if total_pat else 0:.1f}%)</div>
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

    # --- PIE CHARTS WITH SEPARATED MCU (LOKAL & BULE) ---
    st.subheader(f"🥧 Distribusi Pasien & Pendapatan - {selected_month}")
    st.caption("Distribusi pendapatan dipisahkan secara spesifik antara MCU (Lokal & Bule) dengan Layanan Perawatan & Farmasi.")
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        df_pasien = pd.DataFrame({
            "Kategori": ["Pasien Lokal", "Pasien Bule"],
            "Jumlah": [pat_lokal, pat_bule]
        })
        fig_pasien = px.pie(
            df_pasien, values="Jumlah", names="Kategori", 
            title="Persentase Total Pasien (Lokal vs Bule)",
            color_discrete_sequence=["#29B6F6", "#FF7043"],
            hole=0.4
        )
        fig_pasien.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig_pasien, use_container_width=True)

    with col_pie2:
        perawatan_rev = df_tx[df_tx['Service_Type'] == 'Perawatan']['Total'].sum() if not df_tx.empty else 0
        farmasi_rev = df_tx[df_tx['Service_Type'] == 'Farmasi']['Total'].sum() if not df_tx.empty else 0

        df_rev_sep = pd.DataFrame({
            "Kategori Layanan": ["MCU Lokal", "MCU Bule / Turis", "Perawatan & Tindakan", "Farmasi"],
            "Pendapatan": [mcu_rev_lokal, mcu_rev_bule, perawatan_rev, farmasi_rev]
        })
        df_rev_sep = df_rev_sep[df_rev_sep["Pendapatan"] > 0]

        fig_rev = px.pie(
            df_rev_sep, values="Pendapatan", names="Kategori Layanan", 
            title="Rincian Distribusi Pendapatan (Termasuk MCU Lokal & Bule)",
            color_discrete_map={
                "MCU Lokal": "#0288D1",
                "MCU Bule / Turis": "#FF7043",
                "Perawatan & Tindakan": "#66BB6A",
                "Farmasi": "#AB47BC"
            },
            hole=0.4
        )
        fig_rev.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown("---")

    # --- TOP CASES & DIAGNOSA ---
    st.subheader("📋 Top Kasus Penyakit & Layanan Ditangani")
    col_case1, col_case2 = st.columns(2)
    
    with col_case1:
        st.markdown("##### 🌍 Top Kasus Diagnosa Pasien Bule")
        if not df_tx.empty and 'Diagnosa_Clean' in df_tx.columns:
            bule_diag_df = df_tx[(df_tx['Patient_Category'] == 'Bule') & (df_tx['Diagnosa_Clean'].notna())]
            if not bule_diag_df.empty:
                bule_diag = bule_diag_df['Diagnosa_Clean'].value_counts().head(7).reset_index()
                bule_diag.columns = ['Diagnosa', 'Jumlah']
                bule_diag = bule_diag.sort_values('Jumlah', ascending=True)
                
                fig_cb = px.bar(
                    bule_diag, y="Diagnosa", x="Jumlah", orientation="h",
                    text="Jumlah", color_discrete_sequence=["#AB47BC"]
                )
                fig_cb.update_traces(textposition="outside")
                fig_cb.update_layout(
                    xaxis_title="Jumlah Kasus Ditangani",
                    yaxis_title="",
                    height=380,
                    margin=dict(l=10, r=20, t=30, b=40)
                )
                st.plotly_chart(fig_cb, use_container_width=True)
            else:
                st.info("ℹ️ Belum ada diagnosa/kasus penyakit tercatat untuk pasien bule pada periode ini.")
        else:
            st.info("ℹ️ Belum ada data diagnosa untuk pasien bule.")

    with col_case2:
        st.markdown("##### 🇮🇩 Top Kasus Diagnosa Pasien Lokal")
        if not df_tx.empty and 'Diagnosa_Clean' in df_tx.columns:
            lokal_diag_df = df_tx[(df_tx['Patient_Category'] == 'Lokal') & (df_tx['Diagnosa_Clean'].notna())]
            if not lokal_diag_df.empty:
                lokal_diag = lokal_diag_df['Diagnosa_Clean'].value_counts().head(7).reset_index()
                lokal_diag.columns = ['Diagnosa', 'Jumlah']
                lokal_diag = lokal_diag.sort_values('Jumlah', ascending=True)
                
                fig_cl = px.bar(
                    lokal_diag, y="Diagnosa", x="Jumlah", orientation="h",
                    text="Jumlah", color_discrete_sequence=["#26A69A"]
                )
                fig_cl.update_traces(textposition="outside")
                fig_cl.update_layout(
                    xaxis_title="Jumlah Kasus Ditangani",
                    yaxis_title="",
                    height=380,
                    margin=dict(l=10, r=20, t=30, b=40)
                )
                st.plotly_chart(fig_cl, use_container_width=True)
            else:
                st.info("ℹ️ Belum ada diagnosa/kasus penyakit tercatat untuk pasien lokal pada periode ini.")
        else:
            st.info("ℹ️ Belum ada data diagnosa untuk pasien lokal.")

# -------------------------------------------------------------
# PAGE 3: FUTURE PROSPECTS 🎯
# -------------------------------------------------------------
elif page_option == "Future Prospects 🎯":
    st.title("🎯 Future Prospects & Financial Target")
    st.markdown("Strategi & rincian target operasional harian, mingguan, dan bulanan untuk mencapai profitabilitas optimal.")
    st.markdown("---")
    
    target_bulan = 325000000
    profit_margin = 0.25
    profit_bulan = target_bulan * profit_margin
    target_minggu = target_bulan / 4
    target_hari = target_bulan / 30
    profit_hari = profit_bulan / 30

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

    st.subheader("📌 Rincian Target Operasional per Layanan & Kategori Pasien")
    
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
