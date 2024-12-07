from flask import Flask, request, jsonify

mock_app = Flask(__name__)

# Endpoint: /gib-mock
@mock_app.route('/gib-mock', methods=['POST'])
def mock_gib_endpoint():
    """
    Mock GİB sunucusu: İmzalanmış XML verisini alır ve başarı yanıtı döner.
    """
    try:
        # XML verisini al
        if not request.data:
            return jsonify({"error": "No XML data received"}), 400

        # Gelen XML'i kaydetmek veya işlemek için loglama yapılabilir
        xml_data = request.data.decode('utf-8')
        print("Gelen XML:", xml_data)

        # Başarı yanıtı döndür
        return jsonify({
            "message": "Veri başarıyla alındı",
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    mock_app.run(debug=True, port=5001)