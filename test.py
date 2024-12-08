from PyKCS11 import PyKCS11Lib

PKCS11_LIB_PATH = "C:\\Windows\\System32\\akisp11.dll"

def list_tokens():
    """
    PyKCS11 kullanarak bağlı cihazların token etiketlerini listeler.
    """
    pkcs11 = PyKCS11Lib()
    pkcs11.load(PKCS11_LIB_PATH)
    slots = pkcs11.getSlotList(tokenPresent=True)
    for slot in slots:
        info = pkcs11.getTokenInfo(slot)
        print("Token Etiketi (Label):", info.label)

if __name__ == "__main__":
    list_tokens()