from PyKCS11 import PyKCS11Lib, PyKCS11
import hashlib
import time


PKCS11_LIB_PATH = "C:\\Windows\\System32\\akisp11.dll"  # Mali mühür sürücüsü yolu
PIN = "010321"  # Mali mühür cihazınızın PIN kodu
SLOT = 1  # Doğru slot numarası

def create_hash(data):
    """
    Veriyi SHA-256 ile hashler.
    """
    return hashlib.sha256(data.encode("utf-8")).digest()

def sign_with_hsm(data):
    """
    Mali mühür cihazını kullanarak veriyi imzalar.
    """
    try:
        # PKCS#11 kütüphanesini yükle
        pkcs11 = PyKCS11Lib()
        pkcs11.load(PKCS11_LIB_PATH)

        # Cihaza bağlan ve oturum aç
        session = pkcs11.openSession(SLOT)
        session.login(PIN)

        # Hash oluştur
        xml_hash = create_hash(data)
        print("Oluşturulan SHA-256 Hash:", xml_hash.hex())

        # Özel anahtarı bul ve SIGN0 olanı seç
        private_keys = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])
        signing_key = None
        for key in private_keys:
            attributes = session.getAttributeValue(key, [PyKCS11.CKA_LABEL])
            if attributes[0] and "SIGN" in attributes[0]:
                signing_key = key
                print("Seçilen Anahtar (SIGN):", attributes[0])
                break

        if not signing_key:
            raise Exception("İmzalama için uygun anahtar bulunamadı!")

        # İmzalama işlemi
        signed_data = session.sign(signing_key, xml_hash, PyKCS11.CKM_RSA_PKCS)
        print("İmzalama başarılı:", signed_data.hex())

        session.logout()
        session.closeSession()

        return signed_data
    except Exception as e:
        print("Hata oluştu:", e)
    return None


if __name__ == "__main__":
    # Test XML verisi
    test_xml = "<TestData><Value>12345</Value></TestData>"

    # İmzalama işlemi
    signed_data = sign_with_hsm(test_xml)

    if signed_data:
        print("İmzalı Veri (Hex):", signed_data.hex())
    else:
        print("İmzalama işlemi başarısız!")