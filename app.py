import streamlit as st
from Bio import Entrez, SeqIO
from io import StringIO

# Sayfa ayarları
st.set_page_config(page_title="NCBI Gen Analizörü", page_icon="🧬")

st.title("🧬 Gen Sekansı Çekme ve Analiz Aracı")
st.markdown("Bu uygulama, NCBI veritabanından istediğiniz genin dizilimini çeker ve temel GC oranını hesaplar.")

# Kullanıcı Girdileri (Arayüz kutucukları)
email = st.text_input("E-posta adresiniz (NCBI bağlantısı için):", value="muhammedemiresti3@gmail.com")
arama_terimi = st.text_input("Aranacak Gen (Örn: BRCA1, TP53):", value="BRCA1")

# Butona basıldığında çalışacak kısım
if st.button("Veriyi Çek ve Analiz Et"):
    if not email or not arama_terimi:
        st.warning("Lütfen e-posta adresini ve aranacak geni giriniz.")
    else:
        Entrez.email = email
        
        # Yükleniyor animasyonu
        with st.spinner(f"NCBI veritabanında '{arama_terimi}' aranıyor..."):
            try:
                # 1. Arama Yapma
                handle = Entrez.esearch(db="nucleotide", term=arama_terimi, retmax=1)
                record = Entrez.read(handle)
                handle.close()
                
                id_listesi = record["IdList"]
                
                if not id_listesi:
                    st.error("NCBI'da bu gen bulunamadı. Lütfen arama terimini kontrol edin.")
                else:
                    bulunan_id = id_listesi[0]
                    st.success(f"Kayıt bulundu! NCBI ID: {bulunan_id}")
                    
                    # 2. Veriyi Çekme
                    fetch_handle = Entrez.efetch(db="nucleotide", id=bulunan_id, rettype="fasta", retmode="text")
                    fasta_verisi = fetch_handle.read()
                    fetch_handle.close()
                    
                    # 3. Analiz İçin Okuma ve Hesaplama (Senin mantığın)
                    fasta_io = StringIO(fasta_verisi)
                    kayit = SeqIO.read(fasta_io, "fasta")
                    dizilim = str(kayit.seq).upper()
                    
                    toplam_uzunluk = len(dizilim)
                    g_sayisi = dizilim.count("G")
                    c_sayisi = dizilim.count("C")
                    gc_orani = ((g_sayisi + c_sayisi) / toplam_uzunluk) * 100
                    
                    # 4. Sonuçları Ekrana Yazdırma
                    st.subheader("📊 Analiz Sonuçları")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Toplam Uzunluk (Baz)", f"{toplam_uzunluk:,}")
                    col2.metric("GC Oranı", f"%{gc_orani:.2f}")
                    
                    st.subheader("🧬 Dizi Bilgisi (FASTA)")
                    st.text_area("Ham Sekans Verisi", fasta_verisi, height=200)
                    
                    # 5. Dosyayı İndirme Butonu
                    st.download_button(
                        label="FASTA Dosyasını İndir",
                        data=fasta_verisi,
                        file_name=f"{arama_terimi}_sekans.fasta",
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")