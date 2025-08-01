import hashlib
import json

def fingerprint_device(device_info, user_agent):
    # Create a device fingerprint hash for tracking
    raw = json.dumps(device_info, sort_keys=True) + (user_agent or '')
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()
