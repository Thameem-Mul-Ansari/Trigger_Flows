from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/trigger-flow": {
        "origins": ["https://unlimitedautomation.netlify.app"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Product to environment variable mapping
PRODUCT_FLOW_MAPPING = {
    "flow_01": "TASKBOT_PRO_FLOW_URL",
    "flow_02": "DATASYNC_FLOW_URL",
    "flow_03": "CLOUDBOT_FLOW_URL",
    "flow_04": "MOBILEBOT_FLOW_URL",
    "flow_05": "FINANCEBOT_FLOW_URL",
    "flow_06": "HR_AUTOMATION_FLOW_URL",
    "flow_07": "PROCESSIQ_FLOW_URL",
    "flow_08": "CUSTOMERBOT_FLOW_URL"
}

@app.route('/trigger-flow', methods=['POST'])
def trigger_flow():
    try:
        data = request.get_json()

        product_id = data.get('product_id')
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

        # Make empty POST request matching the working example
        response = requests.post(
            flow_url,
            timeout=10
        )

        return jsonify({
            'success': True,
            'product_id': product_id,
            'status_code': response.status_code,
            'response': response.text
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
