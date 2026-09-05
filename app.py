import pandas as pd
import streamlit as st
import yfinance as yf

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Screener & Global Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Dashboard Trading & Monitor Komoditas Global")
st.caption(
    "Pantau Pengaruh Komoditas Global terhadap Saham IHSG secara Real-Time"
)

# Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()

# --- 1. MONITOR KOMODITAS & INDEKS GLOBAL ---
st.subheader("1. Komoditas & Indeks Global")

# Daftar Komoditas & Indeks Global (Simbol Bebas Error)
global_symbols = {
    "Minyak Mentah": "CL=F",
    "Emas (Gold)": "GC=F",
    "Tembaga": "HG=F",
    "Dolar (USD/IDR)": "USDIDR=X",
    "S&P 500": "^GSPC",
}


@st.cache_data(ttl=300)
def get_global_data():
    results = []
    for name, symbol in global_symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")
            if len(df) >= 2:
                last_price = df["Close"].iloc[-1]
                prev_price = df["Close"].iloc[-2]
                change_pct = ((last_price - prev_price) / prev_price) * 100
                results.append(
                    {
                        "Instrumen": name,
                        "Harga Terakhir": round(last_price, 2),
                        "Perubahan (%)": round(change_pct, 2),
                    }
                )
        except Exception:
            pass

    if not results:
        return pd.DataFrame(
            columns=["Instrumen", "Harga Terakhir", "Perubahan (%)"]
        )
    return pd.DataFrame(results)


df_global = get_global_data()

# Tampilkan data global dalam bentuk kolom meteran (Metrics)
if not df_global.empty:
    cols = st.columns(len(df_global))
    for idx, row in df_global.iterrows():
        cols[idx].metric(
            label=row["Instrumen"],
            value=row["Harga Terakhir"],
            delta=f"{row['Perubahan (%)']}%",
        )
else:
    st.warning("Gagal memuat data komoditas. Coba tekan tombol Refresh.")

st.markdown("---")

# --- 2. SCREENER & PEMANTAU SAHAM IHSG ---
st.subheader("2. Pantauan Saham IHSG & Korelasi Komoditas")

ihsg_watchlist = {
    "TINS.JK": "Timah / Tembaga",
    "MEDC.JK": "Minyak Mentah",
    "MDKA.JK": "Emas & Tembaga",
    "SQMI.JK": "Emas",
    "GGRM.JK": "Konsumsi / USDIDR",
    "FILM.JK": "Sentimen Pasar / IHSG",
}


@st.cache_data(ttl=300)
def get_ihsg_data():
    results = []
    for symbol, korelasi in ihsg_watchlist.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")
            if len(df) >= 2:
                last_price = df["Close"].iloc[-1]
                prev_price = df["Close"].iloc[-2]
                change_pct = ((last_price - prev_price) / prev_price) * 100

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
        except Exception:
            pass
    return pd.DataFrame(results)


df_ihsg = get_ihsg_data()

# Tampilkan Tabel
st.dataframe(df_ihsg, use_container_width=True)

st.info(
    "💡 **Tips Beli Pagi Jual Sore:** Amati kolom 'Pengaruh Utama'. Jika harga komoditas global di tabel atas bergerak naik tinggi (>1%), saham IHSG terkait di tabel bawah cenderung berpotensi menguat di awal sesi."
)
