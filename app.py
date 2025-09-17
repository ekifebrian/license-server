from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import secrets
import os
import json
from threading import Lock

app = Flask(__name__)
CORS(app)

# Gunakan environment variable untuk secret key
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# File untuk menyimpan data lisensi
LICENSE_FILE = 'licenses.json'
license_lock = Lock()

def load_licenses():
    """Memuat data lisensi dari file"""
    try:
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_licenses(licenses_data):
    """Menyimpan data lisensi ke file"""
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump(licenses_data, f, indent=2)
        return True
    except:
        return False

# Simpan data lisensi dalam dictionary
licenses = load_licenses()

@app.route('/')
def home():
    return jsonify({
        'message': 'License Server for NIK Checker',
        'status': 'active',
        'endpoints': {
            'admin_generate_license': '/admin/generate_license (POST)',
            'admin_remove_license': '/admin/remove_license (POST)',
            'admin_list_licenses': '/admin/list_licenses (GET)',
            'verify_license': '/verify_license (POST)',
            'activate_license': '/activate_license (POST)'
        }
    })

@app.route('/admin/generate_license', methods=['POST'])
def generate_license():
    # Verifikasi admin key
    admin_key = request.headers.get('X-Admin-Key')
    if not admin_key or admin_key != os.environ.get('ADMIN_KEY'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    duration_days = request.json.get('duration_days', 30)
    
    license_key = f"KPUC_{secrets.token_hex(8).upper()}"
    created_date = datetime.now()
    expiry_date = created_date + timedelta(days=duration_days)
    
    with license_lock:
        licenses[license_key] = {
            'hwid': None,
            'duration_days': duration_days,
            'created_date': created_date.isoformat(),
            'expiry_date': expiry_date.isoformat(),
            'activated': False
        }
        save_licenses(licenses)
    
    return jsonify({
        'success': True, 
        'license_key': license_key,
        'expiry_date': expiry_date.strftime('%d-%m-%Y')
    })

@app.route('/admin/remove_license', methods=['POST'])
def remove_license():
    # Verifikasi admin key
    admin_key = request.headers.get('X-Admin-Key')
    if not admin_key or admin_key != os.environ.get('ADMIN_KEY'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    license_key = request.json.get('license_key')
    
    with license_lock:
        if license_key in licenses:
            del licenses[license_key]
            save_licenses(licenses)
            return jsonify({'success': True, 'message': 'Lisensi berhasil dihapus'})
        return jsonify({'success': False, 'message': 'Lisensi tidak ditemukan'})

@app.route('/admin/list_licenses', methods=['GET'])
def list_licenses():
    # Verifikasi admin key
    admin_key = request.headers.get('X-Admin-Key')
    if not admin_key or admin_key != os.environ.get('ADMIN_KEY'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    # Format data untuk tampilan yang lebih baik
    formatted_licenses = {}
    for key, data in licenses.items():
        formatted_licenses[key] = {
            'status': 'Aktif' if data['activated'] else 'Tidak Aktif',
            'hwid': data['hwid'],
            'durasi': f"{data['duration_days']} hari",
            'dibuat': datetime.fromisoformat(data['created_date']).strftime('%d-%m-%Y'),
            'kedaluwarsa': datetime.fromisoformat(data['expiry_date']).strftime('%d-%m-%Y')
        }
    return jsonify({'success': True, 'licenses': formatted_licenses})

@app.route('/verify_license', methods=['POST'])
def verify_license():
    data = request.json
    hwid = data.get('hwid')
    license_key = data.get('license_key')
    
    if license_key in licenses:
        license_data = licenses[license_key]
        
        # Jika lisensi belum diaktifkan
        if not license_data['activated']:
            return jsonify({
                'valid': True, 
                'message': 'Lisensi valid tetapi belum diaktifkan',
                'expiry_date': license_data['expiry_date']
            })
        
        # Jika hwid cocok
        elif license_data['hwid'] == hwid:
            # Cek masa berlaku
            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            if datetime.now() < expiry_date:
                return jsonify({
                    'valid': True, 
                    'message': 'Lisensi valid',
                    'expiry_date': license_data['expiry_date']
                })
            else:
                return jsonify({
                    'valid': False, 
                    'message': 'Lisensi telah kedaluwarsa',
                    'expiry_date': license_data['expiry_date']
                })
        
        # Jika hwid tidak cocok
        else:
            return jsonify({
                'valid': False, 
                'message': 'Lisensi sudah digunakan di perangkat lain',
                'expiry_date': license_data['expiry_date']
            })
    
    return jsonify({
        'valid': False, 
        'message': 'Lisensi tidak valid',
        'expiry_date': None
    })

@app.route('/activate_license', methods=['POST'])
def activate_license():
    data = request.json
    hwid = data.get('hwid')
    license_key = data.get('license_key')
    
    if license_key in licenses:
        license_data = licenses[license_key]
        
        # Jika lisensi belum diaktifkan
        if not license_data['activated']:
            license_data['hwid'] = hwid
            license_data['activated'] = True
            license_data['activation_date'] = datetime.now().isoformat()
            
            with license_lock:
                save_licenses(licenses)
            
            return jsonify({
                'success': True, 
                'message': 'Aktivasi berhasil',
                'expiry_date': license_data['expiry_date']
            })
        
        # Jika sudah diaktifkan di perangkat yang sama
        elif license_data['hwid'] == hwid:
            return jsonify({
                'success': True, 
                'message': 'Lisensi sudah aktif di perangkat ini',
                'expiry_date': license_data['expiry_date']
            })
        
        # Jika sudah diaktifkan di perangkat lain
        else:
            return jsonify({
                'success': False, 
                'message': 'Lisensi sudah digunakan di perangkat lain',
                'expiry_date': license_data['expiry_date']
            })
    
    return jsonify({
        'success': False, 
        'message': 'Lisensi tidak valid',
        'expiry_date': None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
