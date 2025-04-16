from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = "a super secret, secret key"

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': user_id
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(f"[DEBUG] Generated Token (Expected): {token}")  # Debugging: Print the expected token
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        else:
            print("[DEBUG] Authorization header is missing.")  # Debugging: Missing Authorization header
            return jsonify({'message': 'Authorization header is missing!'}), 401
        
        if not token:
            print("[DEBUG] No token provided in the request headers.")  # Debugging: No token found
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub']  # Fetch the user ID
            print(f"[DEBUG] Provided Token: {token}")  # Debugging: Print the provided token
            print(f"[DEBUG] Decoded Token User ID: {user_id}")  # Debugging: Print the decoded user ID
            
            # Optional: Compare the provided token with an expected token for debugging
            expected_token = encode_token(user_id)
            print(f"[DEBUG] Expected Token: {expected_token}")  # Debugging: Print the expected token for comparison
            
        except jwt.ExpiredSignatureError:
            print(f"[DEBUG] Token has expired. Provided Token: {token}")  # Debugging: Token expired
            return jsonify({'message': 'Token has expired! Please log in again.'}), 401
        except jwt.InvalidSignatureError:
            print(f"[DEBUG] Token signature is invalid. Provided Token: {token}")  # Debugging: Invalid signature
            return jsonify({'message': 'Token signature is invalid!'}), 401
        except jwt.DecodeError:
            print(f"[DEBUG] Token decoding failed. Provided Token: {token}")  # Debugging: Decoding error
            return jsonify({'message': 'Failed to decode token!'}), 401
        except jwt.InvalidTokenError:
            print(f"[DEBUG] Invalid token provided: {token}")  # Debugging: Invalid token
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            print(f"[DEBUG] An unexpected error occurred: {str(e)}")  # Debugging: Unexpected error
            return jsonify({'message': 'An error occurred while processing the token!'}), 500

        return f(user_id, *args, **kwargs)

    return decorated