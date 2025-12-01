# app_avantes_streamlit.py

import os

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ------------------------------------------------
# Donanım kullanılabilir mi? (lokal vs. cloud ayırma)
# ------------------------------------------------
try:
    from avantes_client import AvantesSpectrometer
    HW_AVAILABLE = True
    IMPORT_ERROR = None
except Exception as e:
    # Streamlit Cloud gibi ortamlarda avaspec import'u libavs.so.0 yüzünden patlar
    HW_AVAILABLE = False
    AvantesSpectrometer = None
    IMPORT_ERROR = e


# ------------------------------------------------
# Sayfa ayarları
# ------------------------------------------------
st.set_page_config(
    page_title="Günhan OSTİM LIBS Software V1",
    layout="wide"
)


# ------------------------------------------------
# Session state başlatma
# ------------------------------------------------
if "spectrometer" not in st.session_state:
    st.session_state.spectrometer = AvantesSpectrometer() if HW_AVAILABLE else None
    st.session_state.connected = False
    st.session_state.wavelengths = None
    st.session_state.last_spectrum = None
    st.session_state.measure_count = 0
    st.session_state.last_temperature = None

if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Dosya"

if "active_analysis" not in st.session_state:
    st.session_state.active_analysis = "PCA"


# ------------------------------------------------
# Cloud ortamında donanımın kapalı olduğuna dair uyarı
# ------------------------------------------------
if not HW_AVAILABLE:
    st.warning(
        "Bu ortamda (Streamlit Cloud vb.) Avantes donanım kütüphanesi yüklenemedi. "
        "Spektrum ölçümü ve cihaza bağlanma **yalnızca lokal Windows PC üzerinde** çalışacaktır. "
        "Burada arayüz ve analiz menülerini test edebilirsin."
    )


# ------------------------------------------------
# Üst header: Logo + Başlık
# ------------------------------------------------
header_container = st.container()
with header_container:
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        if os.path.exists("gunhan_logo.png"):
            st.image("gunhan_logo.png", use_column_width=False, width=90)
        else:
            st.markdown("**GÜNHAN OSTİM**")
    with col_title:
        st.markdown(
            "<h1 style='margin-bottom: 0px;'>Günhan OSTİM LIBS Software V1</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='margin-top: 2px; color: gray;'>Avantes spektrometresi ile LIBS veri toplama ve analiz arayüzü</p>",
            unsafe_allow_html=True,
        )

st.markdown("---")


# ------------------------------------------------
# Menü bar (yatay)
# ------------------------------------------------
menu_items = [
    "Dosya",
    "Ayarlar",
    "Kalibrasyon",
    "Lazer",
    "Kamera",
    "Hareket Sistemi",
    "Analiz",
    "Yardım",
]

menu_selection = st.radio(
    "Ana Menü",
    menu_items,
    horizontal=True,
    label_visibility="collapsed",
    key="menu_main",
)

st.session_state.active_menu = menu_selection


# ------------------------------------------------
# Menü içerik alanı (şimdilik placeholder’lar)
# ------------------------------------------------
if st.session_state.active_menu == "Dosya":
    with st.expander("Dosya İşlemleri", expanded=False):
        st.write("- Spektrum kaydet (CSV)")
        st.write("- Proje dosyası aç/kaydet (ileride eklenecek)")
        st.write("- Konfigürasyon profilleri (ileride)")

elif st.session_state.active_menu == "Ayarlar":
    with st.expander("Genel Ayarlar (placeholder)", expanded=False):
        st.write("- Cihaz seçimi, varsayılan entegrasyon süresi vb. (ileride)")

elif st.session_state.active_menu == "Kalibrasyon":
    with st.expander("Kalibrasyon (placeholder)", expanded=False):
        st.write("- Dalgaboyu kalibrasyonu")
        st.write("- Intensity / radiometrik kalibrasyon")
        st.write("- Karanlık spektrum kaydı (dark)")

elif st.session_state.active_menu == "Lazer":
    with st.expander("Lazer Kontrol (placeholder)", expanded=False):
        st.write("- Lazer tetikleme sinyali (dijital çıkış)")
        st.write("- Atım sayısı / frekans ayarı (dış sistemle)")

elif st.session_state.active_menu == "Kamera":
    with st.expander("Kamera Modülü (placeholder)", expanded=False):
        st.write("- Numune görüntüleme")
        st.write("- Lazer spot konumlandırma")

elif st.session_state.active_menu == "Hareket Sistemi":
    with st.expander("Hareket Sistemi (placeholder)", expanded=False):
        st.write("- XYZ eksen kontrolü")
        st.write("- Tarama (mapping) planı")

elif st.session_state.active_menu == "Analiz":
    with st.expander("Analiz Modülleri", expanded=True):
        analysis_option = st.radio(
            "Analiz tipi seçin:",
            ["PCA", "Sınıflandırma – Basit", "Sınıflandırma – Gelişmiş"],
            horizontal=False,
        )
        st.session_state.active_analysis = analysis_option

        if analysis_option == "PCA":
            st.info(
                "PCA (Principal Component Analysis) ile çok boyutlu spektrum verilerini "
                "2D/3D uzaya indirip kümelenmeyi göreceğiz. "
                "İleride bu menüden spektrum setini seçip PCA grafiğini çizeceğiz."
            )
        elif analysis_option == "Sınıflandırma – Basit":
            st.info(
                "Basit sınıflandırma (örneğin k-En Yakın Komşu, kNN) modülü burada olacak. "
                "Önceden etiketlenmiş spektrum setine göre yeni ölçümü sınıflandıracağız."
            )
        elif analysis_option == "Sınıflandırma – Gelişmiş":
            st.info(
                "Daha gelişmiş sınıflandırıcılar (SVM, Random Forest, basit NN) "
                "bu bölümde yer alacak."
            )

elif st.session_state.active_menu == "Yardım":
    with st.expander("Yardım ve Hakkında", expanded=False):
        st.write("Bu yazılım Günhan OSTİM & OSTİM Teknik Üniversitesi işbirliği ile geliştirilmektedir.")
        st.write("Versiyon: V1 – Avantes Streamlit prototip")
        if IMPORT_ERROR is not None:
            st.write(f"Donanım import hatası (teknik bilgi): {IMPORT_ERROR}")
        st.write("Geri bildirimler için: Ar-Ge ekibi")


st.markdown("---")


# ------------------------------------------------
# Bağlantı / Ölçüm parametreleri bölümü
# ------------------------------------------------
left_panel, right_panel = st.columns([1, 3])

with left_panel:
    st.subheader("Cihaz Kontrol")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Cihaza Bağlan"):
            if not HW_AVAILABLE:
                st.error(
                    "Bu ortamda Avantes kütüphanesi yüklü değil. "
                    "Cihaza bağlanma yalnızca lokal Windows kurulumunda mümkündür."
                )
            else:
                try:
                    st.session_state.spectrometer.connect()
                    st.session_state.connected = True
                    st.session_state.wavelengths = st.session_state.spectrometer.get_wavelengths()
                    st.success("Spektrometreye bağlantı başarılı.")
                except Exception as e:
                    st.session_state.connected = False
                    st.error(f"Bağlantı hatası: {e}")

    with col2:
        if st.button("❌ Bağlantıyı Kes"):
            if st.session_state.spectrometer is not None:
                try:
                    st.session_state.spectrometer.disconnect()
                except Exception as e:
                    st.error(f"Bağlantı kapatılırken hata: {e}")
            st.session_state.connected = False
            st.session_state.last_spectrum = None
            st.session_state.measure_count = 0
            st.session_state.last_temperature = None
            st.info("Bağlantı kapatıldı / sıfırlandı.")

    st.markdown("---")

    st.subheader("Ölçüm Parametreleri")

    int_time = st.number_input(
        "Entegrasyon süresi (ms)",
        min_value=1.0,
        max_value=2000.0,
        value=50.0,
        step=1.0,
    )

    avg = st.number_input(
        "Average sayısı",
        min_value=1,
        max_value=100,
        value=1,
        step=1,
    )

    delay_us = st.number_input(
        "Entegrasyon gecikmesi (µs)",
        min_value=0,
        max_value=1_000_000,
        value=0,
        step=1_000,
    )

    st.markdown("---")

    # Durum özeti
    st.markdown("**Durum Özeti**")
    st.write(
        f"• **Bağlantı durumu:** "
        f"{'✅ Bağlı' if st.session_state.connected else '❌ Bağlı değil'}"
    )
    st.write(f"• **Toplam ölçüm sayısı:** {st.session_state.measure_count}")
    if st.session_state.last_temperature is not None:
        st.write(f"• **Sıcaklık (port 0):** {st.session_state.last_temperature:.2f} °C")
    else:
        st.write("• **Sıcaklık:** N/A")

    st.markdown("---")

    if st.session_state.connected and HW_AVAILABLE:
        if st.button("📷 Tek Spektrum Ölç", use_container_width=True):
            try:
                spectrum = st.session_state.spectrometer.single_measure(
                    integration_time_ms=float(int_time),
                    averages=int(avg),
                    integration_delay_us=int(delay_us),
                )
                st.session_state.last_spectrum = spectrum
                st.session_state.measure_count += 1

                # Sıcaklık
                try:
                    temp = st.session_state.spectrometer.get_temperature(port_id=0)
                    st.session_state.last_temperature = temp
                except Exception as e:
                    st.warning(f"Sıcaklık okunamadı: {e}")

            except Exception as e:
                st.error(f"Ölçüm sırasında hata: {e}")
    else:
        if HW_AVAILABLE:
            st.info("Ölçüm almak için önce cihaza bağlanın.")
        else:
            st.info("Bu ortamda ölçüm fonksiyonları devre dışı (donanım yok).")


# ------------------------------------------------
# Sağ panel: Geniş grafik alanı
# ------------------------------------------------
with right_panel:
    st.subheader("Spektrum Görüntüleme")

    if (
        st.session_state.last_spectrum is not None
        and st.session_state.wavelengths is not None
    ):
        lam = st.session_state.wavelengths
        spec = st.session_state.last_spectrum

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(lam, spec)
        ax.set_xlabel("Dalgaboyu (nm)")
        ax.set_ylabel("Yoğunluk (counts)")
        ax.set_title("Son Ölçülen Spektrum")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig, use_container_width=True)

        st.write(f"Piksel sayısı: {len(spec)}")
        if isinstance(lam, np.ndarray) and lam.size > 1:
            st.write(f"Dalgaboyu aralığı: {lam[0]:.1f} nm – {lam[-1]:.1f} nm")
        else:
            st.write("Dalgaboyu bilgisi alınamadı.")

        df = pd.DataFrame({
            "wavelength_nm": lam,
            "intensity": spec,
        })
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "💾 Spektrumu CSV olarak indir",
            data=csv,
            file_name="spectrum.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Henüz gösterilecek bir spektrum yok. Soldan ölçüm alarak başlayın (lokal kurulum).")
