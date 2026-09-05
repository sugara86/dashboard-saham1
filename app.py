import pandas as pd
import streamlit as st
import yfinance as yf

# Konfigurasi Tampilan HP/Mobile
st.set_page_config(
    page_title="Screener Day Trading IHSG",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("⚡ Screener Saham Beli Pagi Jual Sore")
st.caption("Auto-Screener Saham IHSG Potensial & Indikator Komoditas Global")

if st.button("🔄 Refresh Data Real-Time"):
    st.rerun()

st.markdown("---")

# --- 1. KOMODITAS & INDEKS GLOBAL ---
st.subheader("🌐 Sentimen Komoditas & Pasar Global")

global_symbols = {
    "Minyak Mentah": "CL=F",
    "Emas (Gold)": "GC=F",
    "Tembaga": "HG=F",
    "Dolar (USD/IDR)": "USDIDR=X",
    "S&P 500": "^GSPC",
}


@st.cache_data(ttl=180)
def get_global_data():
    results = []
    for name, symbol in global_symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")
            if len(df) >= 2:
                last = df["Close"].iloc[-1]
                prev = df["Close"].iloc[-2]
                chg = ((last - prev) / prev) * 100
                results.append(
                    {
                        "Instrumen": name,
                        "Harga": round(last, 2),
                        "Ubah (%)": round(chg, 2),
                    }
                )
        except Exception:
            pass
    return pd.DataFrame(results)


df_global = get_global_data()
if not df_global.empty:
    cols = st.columns(len(df_global))
    for idx, row in df_global.iterrows():
        cols[idx].metric(
            label=row["Instrumen"],
            value=row["Harga"],
            delta=f"{row['Ubah (%)']}%",
        )

st.markdown("---")

# --- 2. AUTOMATIC SCREENER SAHAM IHSG ---
st.subheader("🔥 Hasil Screener Day Trade / Scalping")

# Daftar Saham Aktif IHSG Paling Populer & Likuid untuk Day Trade
ihsg_universe = {
    # Komoditas & Energi
    "TINS.JK": "Timah / Tembaga",
    "MEDC.JK": "Minyak Mentah",
    "MDKA.JK": "Emas & Tembaga",
    "ANTM.JK": "Emas & Nikel",
    "PTBA.JK": "Batu Bara",
    "ADRO.JK": "Batu Bara",
    "AKRA.JK": "Minyak & Logistik",
    "MBMA.JK": "Nikel",
    "HRUM.JK": "Nikel & Batu Bara",
    "PGAS.JK": "Gas Alam",
    # Consumer & Retail
    "GGRM.JK": "Rokok / Consumer",
    "HMSP.JK": "Rokok / Consumer",
    "ICBP.JK": "Consumer Goods",
    "AMRT.JK": "Ritel / Minimarket",
    # Teknologi & Media / Momentum
    "FILM.JK": "Hiburan / Media",
    "GOTO.JK": "Teknologi",
    "BUKA.JK": "Teknologi",
    "EMTKA.JK": "Media & Tech",
    # Perbankan & Finansial
    "BBCA.JK": "Bank Perbankan",
    "BBRI.JK": "Bank Perbankan",
    "BMRI.JK": "Bank Perbankan",
    "BBNI.JK": "Bank Perbankan",
    "BRIS.JK": "Bank Syariah",
    "ARTO.JK": "Bank Digital",
    # Infrastruktur & Konstruksi
    "TLKM.JK": "Telekomunikasi",
    "PTPP.JK": "Konstruksi",
    "ADHI.JK": "Konstruksi",
}


@st.cache_data(ttl=180)
def run_screener():
    results = []
    for symbol, sektor in ihsg_universe.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="10d")
            if len(df) >= 5:
                last_price = df["Close"].iloc[-1]
                prev_price = df["Close"].iloc[-2]
                change_pct = ((last_price - prev_price) / prev_price) * 100

                # Volume Analysis
                today_vol = df["Volume"].iloc[-1]
                avg_vol = df["Volume"].iloc[-5:-1].mean()
                vol_spike = (
                    (today_vol / avg_vol) if avg_vol > 0 else 1.0
                )  # Rasio lonjakan volume

                # Sinyal Beli Pagi Jual Sore
                if change_pct >= 2.0 and vol_spike >= 1.2:
                    sinyal = "🚀 SUPER BULLISH (Vol Spike + Price Up)"
                elif change_pct >= 1.5:
                    sinyal = "🔥 POTENSI NAIK (Momentum)"
                elif change_pct <= -2.0:
                    sinyal = "⚠️ POTENSI TURUN (Bearish)"
                else:
                    sinyal = "⚪ NETRAL"

                results.append(
                    {
                        "Kode": symbol.replace(".JK", ""),
                        "Harga (Rp)": int(last_price),
                        "Naik (%)": round(change_pct, 2),
                        "Rasio Vol": round(vol_spike, 1),
                        "Sektor / Korelasi": sektor,
                        "Sinyal Screener": sinyal,
                    }
                )
        except Exception:
            pass

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        # Urutkan berdasarkan kenaikan persentase tertinggi
        df_res = df_res.sort_values(by="Naik (%)", ascending=False)
    return df_res


df_screener = run_screener()

# Filter Opsi Tampilan
filter_option = st.radio(
    "Filter Hasil:",
    ["Hanya Sinyal Beli (Potensi Naik / Super Bullish)", "Tampilkan Semua"],
    horizontal=True,
)

if not df_screener.empty:
    if "Hanya Sinyal Beli" in filter_option:
        df_filtered = df_screener[
            df_screener["Sinyal Screener"].str.contains("POTENSI|SUPER")
        ]
    else:
        df_filtered = df_screener

    st.dataframe(df_filtered, use_container_width=True)
else:
    st.info("Sedang memuat data pasar...")

st.success(
    "💡 **Panduan Beli Pagi Jual Sore:**\n"
    "- **Rasio Vol > 1.2:** Menandakan volume transaksi hari ini mendadak melonjak dibanding hari-hari sebelumnya.\n"
    "- **Strategi:** Pilih saham bersinyal **🚀 SUPER BULLISH** di 15-30 menit pertama pasar buka (09.00-09.30 WIB). Pasang target profit 2-4% dan langsung eksekusi jual sebelum pasar tutup."
)
