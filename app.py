import os
import boto3
import json
from botocore.exceptions import ClientError
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_secret(secret_name, region_name="us-east-2"):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        return None
    except ClientError as e:
        print(f"Error: {e}")
        return None

# Load secret once at startup (cache for performance)
SECRET_DATA = get_secret(os.getenv("secret_name"))

@app.route('/')
def hello():
    if SECRET_DATA and 'name' in SECRET_DATA and 'address' in SECRET_DATA:
        name = SECRET_DATA['name']
        address = SECRET_DATA['address']
        message = f"Hello I am {name} from {address}"
        return jsonify({"message": message, "name": name, "address": address})
    return jsonify({"error": "Secret not found or invalid format"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "secrets_loaded": SECRET_DATA is not None})

if __name__ == "__main__":
    print("Secret loaded:", SECRET_DATA)
    app.run(debug=True, host='0.0.0.0', port=5000)