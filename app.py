from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import requests
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for your React frontend
CORS(app, resources={
    r"/trigger-flow": {
        # "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "origins": ["https://unlimitedautomation.netlify.app"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Product mapping to environment variable names
PRODUCT_FLOW_MAPPING = {
    "flow_01": "QR_PRODUCT_APPROVAL_FLOW_URL",
    "flow_02": "INSURANCE_CLAIM_FLOW_URL",
    "flow_03": "CUSTOMER_FEEDBACK_FLOW_URL",
    "flow_04": "RESUME_SCREEN_FLOW_URL",
    "flow_05": "INVOICE_PROCESSING_FLOW_URL",
    "flow_06": "WEB_PRICE_FLOW_URL"
}

@app.route('/trigger-flow', methods=['POST'])
def trigger_flow():
    try:
        data = request.get_json()

        product_id = data.get('product_id')
        filename = data.get('filename')
        file_content = data.get('fileContent')

        if not product_id or product_id not in PRODUCT_FLOW_MAPPING:
            return jsonify({
                'success': False,
                'error': 'Invalid product ID',
                'valid_products': list(PRODUCT_FLOW_MAPPING.keys())
            }), 400

        flow_var_name = PRODUCT_FLOW_MAPPING[product_id]
        flow_url = os.getenv(flow_var_name)

        if not flow_url:
            return jsonify({
                'success': False,
                'error': f'Flow URL not configured for {product_id}',
                'env_var_name': flow_var_name
            }), 500

        # Fix base64 padding if needed
        if file_content and isinstance(file_content, str):
            padding = len(file_content) % 4
            if padding:
                file_content += '=' * (4 - padding)

        # Prepare payload for Power Automate
        payload = {
            "filename": filename,
            "fileContent": file_content
        }

        if product_id == "flow_02":
            payload["extraField1"] = data.get("extraField1")
            payload["extraField2"] = data.get("extraField2")
            payload["extraField3"] = data.get("extraField3")
        
        if product_id == "flow_05":
            payload["extraField4"] = data.get("extraField4")

        if product_id == "flow_06":
            payload["extraField6"] = data.get("extraField6")
            payload["extraField5"] = data.get("extraField5")

        # Send the payload to Power Automate flow
        response = requests.post(flow_url, json=payload, timeout=1400)

        return jsonify({
            'success': True,
            'filename': filename,
            'product_id': product_id,
            'status_code': response.status_code,
            'response': response.text  # Return HTML content as plain text
        })

    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timed out',
            'product_id': product_id
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'product_id': product_id
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)