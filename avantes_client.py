# avantes_client.py

import time
from typing import List

import numpy as np

from avaspec import (
    AVS_Init,
    AVS_UpdateUSBDevices,
    AVS_GetList,
    AVS_Activate,
    AVS_GetNumPixels,
    AVS_GetLambda,
    AVS_PrepareMeasure,
    AVS_Measure,
    AVS_PollScan,
    AVS_GetScopeData,
    AVS_StopMeasure,
    AVS_Deactivate,
    AVS_Done,
    AVS_GetAnalogIn,      # <-- SICAKLIK/ANALOG OKUMA İÇİN
    MeasConfigType,
)


class AvantesSpectrometer:
    """
    Avantes spektrometresini yüksek seviyeli bir Python sınıfı ile saran arayüz.
    Streamlit tarafı bu sınıfı kullanıyor.
    """

    def __init__(self):
        self.handle = None
        self.pixels = None
        self.wavelengths = None
        self._initialized = False

    # -----------------------------
    # Yardımcı: wrapper fonksiyonların tuple / scalar dönüşünü normalize et
    # -----------------------------
    @staticmethod
    def _unwrap(result, index=0):
        """
        avaspec wrapper'ları bazen tuple (err, value) döndürüyor.
        Bazen sadece scalar değer dönebiliyor. Bunu normalize etmek için küçük util.
        """
        if isinstance(result, tuple):
            # (err, value) ise index=1 ile value'yu alırız
            return result[index]
        return result

    # -----------------------------
    # Bağlan / Kapat
    # -----------------------------
    def connect(self):
        """
        USB üzerinden ilk bulunan Avantes spektrometresine bağlan.
        """
        if self.handle is not None:
            return  # zaten bağlı

        # 1) Kütüphaneyi başlat
        n = AVS_Init(0)  # 0 = USB
        self._initialized = True
        if self._unwrap(n) <= 0:
            raise RuntimeError(f"AVS_Init başarısız veya cihaz yok: return={n}")

        # 2) USB cihaz listesini güncelle
        count = AVS_UpdateUSBDevices()
        count_val = self._unwrap(count)
        if count_val <= 0:
            raise RuntimeError("USB üzerinden bağlı spectrometer bulunamadı.")

        # 3) Cihaz listesini al ve ilkini seç
        dev_list = AVS_GetList(count_val)
        if not dev_list:
            raise RuntimeError("AVS_GetList boş döndü, cihaz bulunamadı.")

        device_id = dev_list[0]

        # 4) Cihazı aktive et → handle
        handle = AVS_Activate(device_id)
        handle_val = self._unwrap(handle)
        if handle_val <= 0:
            raise RuntimeError(f"AVS_Activate başarısız: handle={handle_val}")

        self.handle = int(handle_val)

        # 5) Piksel sayısı
        num_res = AVS_GetNumPixels(self.handle)
        num_pixels = self._unwrap(num_res, index=1) if isinstance(num_res, tuple) else num_res
        self.pixels = int(num_pixels)

        # 6) Dalgaboylarını al
        wl_res = AVS_GetLambda(self.handle)
        wl_arr = self._unwrap(wl_res, index=1) if isinstance(wl_res, tuple) else wl_res

        self.wavelengths = np.array(
            [float(wl_arr[i]) for i in range(self.pixels)],
            dtype=float
        )

    def disconnect(self):
        """
        Ölçümü durdur, cihazı deaktive et ve kütüphaneyi kapat.
        """
        if self.handle is None:
            return

        try:
            AVS_StopMeasure(self.handle)
        except Exception:
            pass

        try:
            AVS_Deactivate(self.handle)
        finally:
            self.handle = None

        if self._initialized:
            try:
                AVS_Done()
            except Exception:
                pass
            self._initialized = False

    # -----------------------------
    # Bilgi fonksiyonları
    # -----------------------------
    def get_wavelengths(self) -> np.ndarray:
        if self.wavelengths is None:
            raise RuntimeError("Spektrometre henüz bağlanmadı.")
        return self.wavelengths

    def get_num_pixels(self) -> int:
        if self.pixels is None:
            raise RuntimeError("Spektrometre henüz bağlanmadı.")
        return self.pixels

    def get_temperature(self, port_id: int = 0) -> float:
        """
        Analog girişten sıcaklık okur.
        Çoğu Avantes konfigürasyonunda belirli analog girişler 'degrees Celsius' olarak ayarlanabiliyor.
        Şu an port_id = 0 kullanıyoruz. Gerekirse sonra port değiştiririz.
        """
        if self.handle is None:
            raise RuntimeError("Spektrometre bağlı değil. Önce connect() çağır.")

        res = AVS_GetAnalogIn(self.handle, port_id)
        # Bazı wrapper'lar (err, value) döndürür; bazıları direkt value
        val = self._unwrap(res, index=1) if isinstance(res, tuple) else res
        return float(val)

    # -----------------------------
    # Ölçüm
    # -----------------------------
    def single_measure(
        self,
        integration_time_ms: float = 10.0,
        averages: int = 1,
        integration_delay_us: int = 0,
    ) -> np.ndarray:
        """
        Tek seferlik spektrum al.

        integration_delay_us: m_IntegrationDelay (µs cinsinden) – trigger/delay kontrolü.
        """
        if self.handle is None:
            raise RuntimeError("Spektrometre bağlı değil. Önce connect() çağır.")

        # Ölçüm konfigürasyon struct'ı
        meas = MeasConfigType()
        meas.m_StartPixel = 0
        meas.m_StopPixel = self.pixels - 1
        meas.m_IntegrationTime = float(integration_time_ms)
        meas.m_IntegrationDelay = int(integration_delay_us)
        meas.m_NrAverages = int(averages)

        # Basit mod: tüm ekstra özellikleri kapatıyoruz
        meas.m_CorDynDark_m_Enable = 0
        meas.m_CorDynDark_m_ForgetPercentage = 0
        meas.m_Smoothing_m_SmoothPix = 0
        meas.m_Smoothing_m_SmoothModel = 0
        meas.m_SaturationDetection = 0
        meas.m_Trigger_m_Mode = 0
        meas.m_Trigger_m_Source = 0
        meas.m_Trigger_m_SourceType = 0
        meas.m_Control_m_StrobeControl = 0
        meas.m_Control_m_LaserDelay = 0
        meas.m_Control_m_LaserWidth = 0
        meas.m_Control_m_LaserWaveLength = 0.0
        meas.m_Control_m_StoreToRam = 0

        # 1) Ölçüme hazırlan
        ret = AVS_PrepareMeasure(self.handle, meas)
        err = self._unwrap(ret)
        if err != 0:
            raise RuntimeError(f"AVS_PrepareMeasure hata kodu: {err}")

        # 2) Ölçümü başlat (windowhandle=0, nummeas=1)
        ret = AVS_Measure(self.handle, 0, 1)
        err = self._unwrap(ret)
        if err != 0:
            raise RuntimeError(f"AVS_Measure hata kodu: {err}")

        # 3) Veri hazır olana kadar bekle (maks ~10 sn)
        for _ in range(1000):
            ready = AVS_PollScan(self.handle)
            ready_val = self._unwrap(ready)
            if bool(ready_val):
                break
            time.sleep(0.01)
        else:
            raise RuntimeError("AVS_PollScan zaman aşımına uğradı, veri gelmedi.")

        # 4) Spektrumu çek
        timestamp, spectrum = AVS_GetScopeData(self.handle)

        intens = np.array(
            [float(spectrum[i]) for i in range(self.pixels)],
            dtype=float
        )
        return intens
