from pkcs11 import lib, Mechanism, Attribute, ObjectClass
import hashlib
# PKCS#11 Kütüphane Yolu
PKCS11_LIB_PATH = "C:\\Windows\\System32\\akisp11.dll"  # PKCS#11 sürücüsü yolu
PIN = "010321"  # Mali mühür PIN kodu


def create_hash(data):
    """
    Veriyi SHA-384 ile hashler.
    """
    return hashlib.sha384(data.encode("utf-8")).digest()

def find_signing_key(session):
    """
    Cihazdaki özel anahtarları tarar ve imzalama için uygun olanı otomatik olarak seçer.
    """
    keys = session.get_objects({Attribute.CLASS: ObjectClass.PRIVATE_KEY})
    for key in keys:
        print(f"Bulunan Anahtar: {key}")
        # Etikette 'SIGN' anahtar kelimesini kontrol et
        if 'SIGN' in key.label:
            print(f"İmzalama Anahtarı Bulundu: {key.label}")
            return key
    return None

def sign_with_hsm(data):
    """
    Slot bilgisi ile bağlanarak SHA384WITH RSA_PKCS algoritması ile imzalama işlemi yapar.
    """
    try:
        library = lib(PKCS11_LIB_PATH)

        # İlk Slot'u Seç
        slots = library.get_slots()
        if not slots:
            raise Exception("Bağlı bir slot bulunamadı!")

        slot = slots[0]  # İlk slotu kullanıyoruz, gerekirse doğru slotu seçin
        print(f"Seçilen Slot: {slot}")

        # Token ile Oturum Aç
        token = slot.get_token()
        print(f"Token Etiketi: {token.label}")
        with token.open(user_pin=PIN) as session:
            print("Token ile oturum açıldı.")

            # Otomatik Etiket Çekimi: İmzalama Anahtarını Bul
            private_key = find_signing_key(session)
            if private_key is None:
                raise Exception("İmzalama için uygun özel anahtar bulunamadı!")

            # SHA-384 Hash Oluştur
            data_hash = create_hash(data)
            print("Oluşturulan SHA-384 Hash:", data_hash.hex())

            # Özel Anahtarı Kullanarak İmzalama İşlemi
            signature = private_key.sign(data_hash, mechanism=Mechanism.RSA_PKCS)
            print("İmzalama başarılı:", signature.hex())
            return signature

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