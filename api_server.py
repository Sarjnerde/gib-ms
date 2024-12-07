import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request
from signxml import XMLSigner
import requests

app = Flask(__name__)

API_URL = "https://okctest.gib.gov.tr/api/v1/okc/okcesu/yeniEsuKayit"
API_KEY = "YOUR_API_KEY"

# XML Oluşturma Fonksiyonu
def create_xml(data, root_tag):
    """
    XML verisini oluşturur.
    """
    root = ET.Element(root_tag)
    for key, value in data.items():
        if isinstance(value, dict):  # Nested dictionary support
            sub_element = ET.SubElement(root, key)
            for sub_key, sub_value in value.items():
                ET.SubElement(sub_element, sub_key).text = str(sub_value)
        else:
            ET.SubElement(root, key).text = str(value)
    return ET.tostring(root, encoding="utf-8", method="xml")

# XML İmzalama Fonksiyonu
def sign_xml(xml_data):
    """
    XML verisini mali mühürle imzalar.
    """
    signer = XMLSigner()
    signed_xml = signer.sign(xml_data)
    return signed_xml

# GİB API Gönderim Fonksiyonu
def send_to_gib(xml_data):
    """
    XML verisini GİB API'sine gönderir.
    """
    headers = {
        "Content-Type": "application/xml",
        "Authorization": f"Bearer {API_KEY}"
    }
    response = requests.post(API_URL, data=xml_data, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return {"error": "GİB hata döndürdü", "status_code": response.status_code, "response": response.text}

# Endpoint: /status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "API is running"}), 200

# Endpoint: /gib_workflow
@app.route('/gib_workflow', methods=['POST'])
def gib_workflow():
    """
    GİB için XML oluşturma, imzalama ve gönderme işlemi.
    """
    try:
        # Gelen veriyi al
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # XML oluştur
        xml_data = create_xml(data, "ElectricChargingUnit")

        # XML'i imzala
        signed_xml = sign_xml(xml_data)

        # GİB API'sine gönder
        response = send_to_gib(signed_xml)

        return jsonify({"message": "GİB işlemi tamamlandı", "response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)