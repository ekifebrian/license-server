import requests
import argparse
import sys
from datetime import datetime

class LicenseAdmin:
    def __init__(self, server_url, admin_key):
        self.server_url = server_url
        self.admin_key = admin_key
        self.headers = {'X-Admin-Key': admin_key}
    
    def generate_license(self, duration_days):
        """Generate lisensi baru"""
        try:
            response = requests.post(
                f"{self.server_url}/admin/generate_license",
                json={'duration_days': duration_days},
                headers=self.headers,
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Koneksi error: {str(e)}'}
    
    def remove_license(self, license_key):
        """Hapus lisensi"""
        try:
            response = requests.post(
                f"{self.server_url}/admin/remove_license",
                json={'license_key': license_key},
                headers=self.headers,
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Koneksi error: {str(e)}'}
    
    def list_licenses(self):
        """Daftar semua lisensi"""
        try:
            response = requests.get(
                f"{self.server_url}/admin/list_licenses",
                headers=self.headers,
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Koneksi error: {str(e)}'}
    
    def reset_license(self, license_key):
        """Reset aktivasi lisensi (bisa digunakan di device lain)"""
        try:
            response = requests.post(
                f"{self.server_url}/admin/reset_license",
                json={'license_key': license_key},
                headers=self.headers,
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Koneksi error: {str(e)}'}

def display_licenses(licenses_data):
    """Menampilkan daftar lisensi dalam format rapi"""
    if not licenses_data:
        print("📭 Tidak ada lisensi yang terdaftar")
        return
    
    print("📋 DAFTAR LISENSI:")
    print("=" * 100)
    print(f"{'KODE LISENSI':<20} {'STATUS':<12} {'HWID':<15} {'DURASI':<10} {'KEDALUWARSA':<12}")
    print("=" * 100)
    
    for key, data in licenses_data.items():
        license_key_short = key[:18] + "..." if len(key) > 18 else key
        status = data.get('status', 'Unknown')
        hwid = data.get('hwid', 'Not activated')[:12] + "..." if data.get('hwid') else 'Not activated'
        duration = data.get('durasi', 'Unknown')
        expiry = data.get('kedaluwarsa', 'Unknown')
        
        print(f"{license_key_short:<20} {status:<12} {hwid:<15} {duration:<10} {expiry:<12}")
    
    print("=" * 100)

def main():
    parser = argparse.ArgumentParser(description='Admin Tool untuk Mengelola Lisensi NIK Checker')
    parser.add_argument('--server', default='https://licenseserverr-aeb3a843fdaa.herokuapp.com', 
                       help='URL server lisensi (default: https://licenseserverr-aeb3a843fdaa.herokuapp.com)')
    parser.add_argument('--key', required=True, help='Kunci admin (ADMIN_KEY dari Heroku)')
    
    subparsers = parser.add_subparsers(dest='command', help='Perintah')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate lisensi baru')
    generate_parser.add_argument('--days', type=int, default=30, 
                               help='Durasi lisensi dalam hari (default: 30)')
    generate_parser.add_argument('--count', type=int, default=1,
                               help='Jumlah lisensi yang akan digenerate (default: 1)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Hapus lisensi')
    remove_parser.add_argument('--license', required=True, help='Kode lisensi yang akan dihapus')
    
    # List command
    list_parser = subparsers.add_parser('list', help='Daftar semua lisensi')
    list_parser.add_argument('--detail', action='store_true', help='Tampilkan detail lengkap')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset aktivasi lisensi')
    reset_parser.add_argument('--license', required=True, help='Kode lisensi yang akan direset')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    admin = LicenseAdmin(args.server, args.key)
    
    if args.command == 'generate':
        print(f"🔄 Membuat {args.count} lisensi untuk {args.days} hari...")
        print("-" * 50)
        
        generated_licenses = []
        for i in range(args.count):
            result = admin.generate_license(args.days)
            if result.get('success'):
                generated_licenses.append({
                    'key': result.get('license_key'),
                    'expiry': result.get('expiry_date')
                })
                print(f"✅ {i+1}. {result.get('license_key')} - Berlaku hingga: {result.get('expiry_date')}")
            else:
                print(f"❌ {i+1}. Gagal: {result.get('message')}")
        
        if generated_licenses:
            print("\n📋 LISENSI YANG BERHASIL DIBUAT:")
            print("=" * 80)
            for license in generated_licenses:
                print(f"🔑 {license['key']}")
                print(f"   📅 Kedaluwarsa: {license['expiry']}")
                print("-" * 80)
            
            # Simpan ke file
            try:
                with open('generated_licenses.txt', 'w', encoding='utf-8') as f:
                    f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Server: {args.server}\n")
                    f.write("=" * 50 + "\n")
                    for license in generated_licenses:
                        f.write(f"License: {license['key']}\n")
                        f.write(f"Expiry: {license['expiry']}\n")
                        f.write("-" * 50 + "\n")
                print(f"💾 Lisensi disimpan ke: generated_licenses.txt")
            except Exception as e:
                print(f"⚠️  Gagal menyimpan ke file: {e}")
    
    elif args.command == 'remove':
        print(f"🗑️  Menghapus lisensi: {args.license}")
        result = admin.remove_license(args.license)
        if result.get('success'):
            print(f"✅ Lisensi berhasil dihapus")
        else:
            print(f"❌ Gagal: {result.get('message')}")
    
    elif args.command == 'list':
        result = admin.list_licenses()
        if result.get('success'):
            licenses = result.get('licenses', {})
            if not licenses:
                print("📭 Tidak ada lisensi yang terdaftar")
            else:
                if args.detail:
                    print("📋 DETAIL LISENSI:")
                    print("=" * 80)
                    for key, data in licenses.items():
                        print(f"🔑 Kode: {key}")
                        print(f"   Status: {data.get('status')}")
                        print(f"   HWID: {data.get('hwid') or 'Belum diaktifkan'}")
                        print(f"   Durasi: {data.get('durasi')}")
                        print(f"   Dibuat: {data.get('dibuat')}")
                        print(f"   Kedaluwarsa: {data.get('kedaluwarsa')}")
                        print("-" * 80)
                else:
                    display_licenses(licenses)
                    
                print(f"📊 Total: {len(licenses)} lisensi")
        else:
            print(f"❌ ERROR: {result.get('message')}")
    
    elif args.command == 'reset':
        print(f"🔄 Reset lisensi: {args.license}")
        result = admin.reset_license(args.license)
        if result.get('success'):
            print(f"✅ Lisensi berhasil direset")
            print(f"📝 Pesan: {result.get('message')}")
        else:
            print(f"❌ Gagal: {result.get('message')}")

if __name__ == '__main__':
    main()
