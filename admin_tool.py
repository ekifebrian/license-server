import requests
import argparse
import sys

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
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Connection error: {str(e)}'}
    
    def remove_license(self, license_key):
        """Hapus lisensi"""
        try:
            response = requests.post(
                f"{self.server_url}/admin/remove_license",
                json={'license_key': license_key},
                headers=self.headers,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Connection error: {str(e)}'}
    
    def list_licenses(self):
        """Daftar semua lisensi"""
        try:
            response = requests.get(
                f"{self.server_url}/admin/list_licenses",
                headers=self.headers,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'message': f'Connection error: {str(e)}'}

def main():
    parser = argparse.ArgumentParser(description='Admin Tool untuk Mengelola Lisensi NIK Checker')
    parser.add_argument('--server', default='https://licenseserverr-aeb3a843fdaa.herokuapp.com', help='URL server lisensi')
    parser.add_argument('--key', required=True, help='Kunci admin (ADMIN_KEY dari Heroku)')
    
    subparsers = parser.add_subparsers(dest='command', help='Perintah')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate lisensi baru')
    generate_parser.add_argument('--days', type=int, default=30, help='Durasi lisensi dalam hari (default: 30)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Hapus lisensi')
    remove_parser.add_argument('--license', required=True, help='Kode lisensi yang akan dihapus')
    
    # List command
    subparsers.add_parser('list', help='Daftar semua lisensi')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    admin = LicenseAdmin(args.server, args.key)
    
    if args.command == 'generate':
        result = admin.generate_license(args.days)
        if result.get('success'):
            print("✅ LISENSI BERHASIL DIBUAT")
            print(f"🔑 Kode Lisensi: {result.get('license_key')}")
            print(f"📅 Berlaku hingga: {result.get('expiry_date')}")
            print(f"⏰ Durasi: {args.days} hari")
        else:
            print(f"❌ ERROR: {result.get('message')}")
    
    elif args.command == 'remove':
        result = admin.remove_license(args.license)
        if result.get('success'):
            print(f"✅ Lisensi {args.license} berhasil dihapus")
        else:
            print(f"❌ ERROR: {result.get('message')}")
    
    elif args.command == 'list':
        result = admin.list_licenses()
        if result.get('success'):
            licenses = result.get('licenses', {})
            if not licenses:
                print("📭 Tidak ada lisensi yang terdaftar")
            else:
                print("📋 DAFTAR LISENSI:")
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
            print(f"❌ ERROR: {result.get('message')}")

if __name__ == '__main__':
    main()
