import pandas as pd
import streamlit as st
import yfinance as yf

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Screener & Global Monitor", layout="wide", initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Trading & Monitor Komoditas Global")
st.caption("Pantau Pengaruh Komoditas Global terhadap Saham IHSG secara Real-Time")

# Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()

# --- 1. MONITOR KOMODITAS & INDEKS GLOBAL ---
st.subheader("1. Komoditas & Indeks Global")

global_symbol = {
    "Minyak Mentah": "CL=F",
    "Emas (Gold)": "GC=F",
    "Tembaga": "HG=F",
    "Dolar (USD/IDR)": "USDIDR=X",
    "S&P 500": "^GSPC",
}



@st.cache_data(ttl=300)  # Cache data selama 5 menit
def get_global_data():
    tickers = list(global_symbols.values())
    df = yf.download(tickers, period="2d")["Close"]
    results = []

    for name, symbol in global_symbols.items():
        if symbol in df.columns:
            last_price = df[symbol].iloc[-1]
            prev_price = df[symbol].iloc[-2]
            change_pct = ((last_price - prev_price) / prev_price) * 100
            results.append(
                {
                    "Instrumen": name,
                    "Harga Terakhir": round(last_price, 2),
                    "Perubahan (%)": round(change_pct, 2),
                }
            )
    return pd.DataFrame(results)


df_global = get_global_data()

# Tampilkan data global dalam bentuk kolom meteran (Metrics)
cols = st.columns(len(df_global))
for idx, row in df_global.iterrows():
    cols[idx].metric(
        label=row["Instrumen"],
        value=row["Harga Terakhir"],
        delta=f"{row['Perubahan (%)']}%",
    )

st.markdown("---")

# --- 2. SCREENER & PEMANTAU SAHAM IHSG ---
st.subheader("2. Pantauan Saham IHSG & Korelasi Komoditas")

# Daftar saham pantauan beserta korelasi utamanya
ihsg_watchlist = {
    "TINS.JK": "Timah",
    "MEDC.JK": "Minyak Mentah",
    "MDKA.JK": "Emas & Tembaga",
    "SQMI.JK": "Emas",
    "GGRM.JK": "Konsumsi / USDIDR",
    "FILM.JK": "Sentimen Pasar / IHSG",
}


@st.cache_data(ttl=300)
def get_ihsg_data():
    tickers = list(ihsg_watchlist.keys())
    df = yf.download(tickers, period="5d")["Close"]
    results = []

    for symbol, korelasi in ihsg_watchlist.items():
        if symbol in df.columns:
            prices = df[symbol].dropna()
            if len(prices) >= 2:
                last_price = prices.iloc[-1]
                prev_price = prices.iloc[-2]
                change_pct = ((last_price - prev_price) / prev_price) * 100

                # Status Sederhana untuk Screener Pagi
                status = "NETRAL"
                if change_pct > 2.0:
                    status = "🔥 POTENSI NAIK (BULLISH)"
                elif change_pct < -2.0:
                    status = "⚠️ POTENSI TURUN (BEARISH)"

                results.append(
                    {
                        "Kode Saham": symbol.replace(".JK", ""),
                        "Harga Terakhir (Rp)": int(last_price),
                        "Perubahan (%)": round(change_pct, 2),
                        "Pengaruh Utama": korelasi,
                        "Sinyal Screener": status,
                    }
                )
    return pd.DataFrame(results)


df_ihsg = get_ihsg_data()

# Tampilkan Tabel
st.dataframe(df_ihsg, use_container_width=True)

st.info(
    "💡 **Tips Beli Pagi Jual Sore:** Amati kolom 'Pengaruh Utama'. Jika harga komoditas global di tabel atas bergerak naik tinggi (>1%), saham IHSG terkait di tabel bawah cenderung berpotensi menguat di awal sesi."
)
