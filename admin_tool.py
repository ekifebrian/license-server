import requests
import argparse
import os

class LicenseAdmin:
    def __init__(self, server_url, admin_key):
        self.server_url = server_url
        self.admin_key = admin_key
        self.headers = {'X-Admin-Key': admin_key}
    
    def generate_license(self, duration_days):
        """Generate lisensi baru"""
        response = requests.post(
            f"{self.server_url}/admin/generate_license",
            json={'duration_days': duration_days},
            headers=self.headers
        )
        return response.json()
    
    def remove_license(self, license_key):
        """Hapus lisensi"""
        response = requests.post(
            f"{self.server_url}/admin/remove_license",
            json={'license_key': license_key},
            headers=self.headers
        )
        return response.json()
    
    def list_licenses(self):
        """Daftar semua lisensi"""
        response = requests.get(
            f"{self.server_url}/admin/list_licenses",
            headers=self.headers
        )
        return response.json()

def main():
    parser = argparse.ArgumentParser(description='Admin Tool untuk Mengelola Lisensi')
    parser.add_argument('--server', required=True, help='URL server lisensi')
    parser.add_argument('--key', required=True, help='Kunci admin')
    
    subparsers = parser.add_subparsers(dest='command', help='Perintah')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate lisensi baru')
    generate_parser.add_argument('--days', type=int, default=30, help='Durasi lisensi dalam hari')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Hapus lisensi')
    remove_parser.add_argument('--license', required=True, help='Kode lisensi yang akan dihapus')
    
    # List command
    subparsers.add_parser('list', help='Daftar semua lisensi')
    
    args = parser.parse_args()
    
    admin = LicenseAdmin(args.server, args.key)
    
    if args.command == 'generate':
        result = admin.generate_license(args.days)
        print(f"Lisensi Baru: {result.get('license_key')}")
        print(f"Kedaluwarsa: {result.get('expiry_date')}")
    
    elif args.command == 'remove':
        result = admin.remove_license(args.license)
        print(result.get('message'))
    
    elif args.command == 'list':
        result = admin.list_licenses()
        if result.get('success'):
            licenses = result.get('licenses', {})
            for key, data in licenses.items():
                print(f"Kode: {key}")
                print(f"  Status: {data.get('status')}")
                print(f"  HWID: {data.get('hwid') or 'Belum diaktifkan'}")
                print(f"  Durasi: {data.get('durasi')}")
                print(f"  Dibuat: {data.get('dibuat')}")
                print(f"  Kedaluwarsa: {data.get('kedaluwarsa')}")
                print("-" * 40)
        else:
            print("Gagal mengambil daftar lisensi")

if __name__ == '__main__':
    main()
