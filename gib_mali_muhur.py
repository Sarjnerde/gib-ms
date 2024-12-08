import xml.etree.ElementTree as ET
from PyKCS11 import PyKCS11Lib, PyKCS11
import requests

# GİB API URL
API_URL = "https://okctest.gib.gov.tr/api/v1/okc/okcesu/yeniEsuKayit"
API_KEY = "YOUR_API_KEY"  # GİB’den alınan API anahtarı
PKCS11_LIB_PATH = "C:\\Windows\\System32\\akisp11.dll"  # Mali mühür sürücüsü yolu
PIN = "123456"  # Mali mühür PIN'i

# XML Oluşturma Fonksiyonu
def create_xml(data):
    """
    XML verisini oluşturur.
    """
    root = ET.Element("eArsivRaporu", attrib={
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
        "xmlns": "http://earsiv.efatura.gov.tr"
    })

    # Başlık bilgileri
    baslik = ET.SubElement(root, "baslik")
    ET.SubElement(baslik, "versiyon").text = data["versiyon"]
    mukellef = ET.SubElement(baslik, "mukellef")
    ET.SubElement(mukellef, "vkn").text = data["mukellef_vkn"]
    ET.SubElement(baslik, "raporNo").text = data["rapor_no"]

    # Rapor detayları
    for esu in data["esu_raporlari"]:
        esu_rapor = ET.SubElement(root, "esuRapor")
        ET.SubElement(esu_rapor, "UUID").text = esu["uuid"]
        ET.SubElement(esu_rapor, "plakaNo").text = esu["plaka_no"]
        hizmet_miktari = ET.SubElement(esu_rapor, "hizmetMiktari", attrib={"unitCode": "kWh"})
        hizmet_miktari.text = str(esu["hizmet_miktari"])
        ET.SubElement(esu_rapor, "toplamTutar").text = str(esu["toplam_tutar"])
        ET.SubElement(esu_rapor, "paraBirimi").text = esu["para_birimi"]

    return ET.tostring(root, encoding="utf-8", method="xml")

# Mali Mühür ile İmzalama Fonksiyonu
def sign_with_hsm(xml_data):
    """
    Mali mühür cihazını kullanarak XML'i imzalar.
    """
    pkcs11 = PyKCS11Lib()
    pkcs11.load(PKCS11_LIB_PATH)  # Mali mühür sürücüsü

    # Cihaza bağlan ve oturum aç
    slot = pkcs11.getSlotList(tokenPresent=True)[0]
    session = pkcs11.openSession(slot)
    session.login(PIN)  # PIN ile doğrulama

    # XML verisini hashle
    xml_hash = session.digest(xml_data, PyKCS11.CKM_SHA256)

    # Hash'i imzala
    private_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])[0]
    signed_data = session.sign(private_key, xml_hash, PyKCS11.CKM_RSA_PKCS)

    # Oturumu kapat
    session.logout()
    session.closeSession()

    return signed_data

# GİB API Gönderim Fonksiyonu
def send_to_gib(xml_data, signed_data):
    """
    GİB API'sine imzalı XML verisini gönderir.
    """
    headers = {
        "Content-Type": "application/xml",
        "Authorization": f"Bearer {API_KEY}"
    }

    # XML'in içine imza ekle
    xml_with_signature = xml_data.decode("utf-8").replace(
        "</eArsivRaporu>",
        f"<ds:Signature>{signed_data.hex()}</ds:Signature></eArsivRaporu>"
    )

    # GİB'e gönder
    response = requests.post(API_URL, data=xml_with_signature.encode("utf-8"), headers=headers)
    if response.status_code == 200:
        print("Başarılı:", response.text)
    else:
        print("Hata:", response.status_code, response.text)

# Ana İş Akışı
if __name__ == "__main__":
    # XML verisi için örnek giriş
    data = {
        "versiyon": "1.0",
        "mukellef_vkn": "1234567890",
        "rapor_no": "d34512e8-8141-4c38-8c25-e86ef42f1bb5",
        "esu_raporlari": [
            {
                "uuid": "dbaacd1f-400d-4634-b628-3606ef6b91b9",
                "plaka_no": "06ABC123",
                "hizmet_miktari": 7.224,
                "toplam_tutar": 57.07,
                "para_birimi": "TRY"
            },
            {
                "uuid": "c40af62a-508e-4ea0-86ab-9a1112f8c1c6",
                "plaka_no": "06ACD519",
                "hizmet_miktari": 4.373,
                "toplam_tutar": 34.55,
                "para_birimi": "TRY"
            }
        ]
    }

    try:
        # XML oluştur
        xml_data = create_xml(data)

        # XML'i mali mühür cihazıyla imzala
        signed_data = sign_with_hsm(xml_data)

        # GİB'e gönder
        send_to_gib(xml_data, signed_data)

    except Exception as e:
        print("Hata oluştu:", e)