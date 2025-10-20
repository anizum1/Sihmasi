#!/usr/bin/env python3
"""
SihmaSi - Enhanced GPS Detection Version
Debugging tool to see ALL GPS-related fields
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import hashlib

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_banner():
    """Display the SihmaSi banner"""
    banner = f"""
{RED}{BOLD}
███████╗██╗██╗  ██╗███╗   ███╗ █████╗ ███████╗██╗
██╔════╝██║██║  ██║████╗ ████║██╔══██╗██╔════╝██║
███████╗██║███████║██╔████╔██║███████║███████╗██║
╚════██║██║██╔══██║██║╚██╔╝██║██╔══██║╚════██║██║
███████║██║██║  ██║██║ ╚═╝ ██║██║  ██║███████║██║
╚══════╝╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝
{RESET}
{CYAN}        Advanced Metadata Extraction Tool{RESET}
{YELLOW}         GPS Detection Enhanced Version{RESET}
{MAGENTA}═══════════════════════════════════════════════════{RESET}
"""
    print(banner)

def check_dependencies():
    """Check if required tools are installed"""
    tools = ['exiftool']
    missing = []
    
    for tool in tools:
        result = subprocess.run(['which', tool], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(tool)
    
    if missing:
        print(f"{RED}[!] Missing dependencies: {', '.join(missing)}{RESET}")
        print(f"{YELLOW}[*] Install with: sudo apt-get install libimage-exiftool-perl{RESET}")
        return False
    return True

def get_file_hash(file_path):
    """Get MD5 hash of file"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"Error: {e}"

def extract_metadata_detailed(file_path):
    """Extract ALL metadata using exiftool"""
    if not os.path.exists(file_path):
        print(f"{RED}[!] Error: File not found - {file_path}{RESET}")
        return None
    
    try:
        abs_path = os.path.abspath(file_path)
        
        result = subprocess.run(
            ['exiftool', '-a', '-u', '-g1', '-s', '-n', '-ee', '-G1', abs_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{RED}[!] Error extracting metadata: {e}{RESET}")
        return None
    except Exception as e:
        print(f"{RED}[!] Unexpected error: {e}{RESET}")
        return None

def get_file_info(file_path):
    """Get basic file information"""
    abs_path = os.path.abspath(file_path)
    file_stat = os.stat(abs_path)
    return {
        'size': file_stat.st_size,
        'modified': datetime.fromtimestamp(file_stat.st_mtime),
        'created': datetime.fromtimestamp(file_stat.st_ctime),
        'accessed': datetime.fromtimestamp(file_stat.st_atime),
        'extension': Path(abs_path).suffix.lower(),
        'absolute_path': abs_path,
        'hash': get_file_hash(abs_path),
        'filename': os.path.basename(abs_path)
    }

def debug_gps_fields(metadata):
    """Debug: Show ALL fields that contain 'gps' (case-insensitive)"""
    print(f"\n{YELLOW}{BOLD}[DEBUG] GPS Field Detection:{RESET}")
    print(f"{YELLOW}Searching for ANY field containing 'gps'...{RESET}\n")
    
    gps_fields = []
    if metadata:
        for line in metadata.split('\n'):
            if 'gps' in line.lower() and line.strip():
                gps_fields.append(line)
    
    if gps_fields:
        print(f"{GREEN}Found {len(gps_fields)} GPS-related fields:{RESET}")
        for field in gps_fields:
            print(f"  {GREEN}✓{RESET} {field}")
    else:
        print(f"{RED}✗ No GPS fields found in this file{RESET}")
        print(f"{YELLOW}This means:{RESET}")
        print(f"  • The device didn't have GPS enabled when photo was taken")
        print(f"  • GPS data was stripped during editing/sharing")
        print(f"  • The file format doesn't support GPS metadata")
    
    return gps_fields

def extract_critical_info(metadata):
    """Extract GPS and other critical metadata - ENHANCED VERSION"""
    critical = {
        'gps': {},
        'camera': {},
        'datetime': {},
        'software': {},
        'owner': {}
    }
    
    if not metadata:
        return critical
    
    for line in metadata.split('\n'):
        if ':' not in line:
            continue
        
        line_lower = line.lower()
        
        # Split on FIRST colon only to handle values with colons
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue
            
        key = parts[0].strip()
        value = parts[1].strip()
        
        # More flexible GPS extraction - catch ANY gps field
        if 'gps' in line_lower:
            # Store every GPS field we find
            field_name = key.split()[-1] if ' ' in key else key
            critical['gps'][field_name] = value
        
        # Camera info
        if 'make' in line_lower and 'model' not in line_lower:
            critical['camera']['make'] = value
        elif 'model' in line_lower and ('camera' in line_lower or 'make' not in line_lower):
            critical['camera']['model'] = value
        elif 'lens' in line_lower:
            critical['camera']['lens'] = value
        elif 'serialnumber' in line_lower:
            critical['camera']['serial'] = value
            
        # DateTime info
        if 'datetimeoriginal' in line_lower:
            critical['datetime']['original'] = value
        elif 'createdate' in line_lower:
            critical['datetime']['created'] = value
        elif 'modifydate' in line_lower:
            critical['datetime']['modified'] = value
            
        # Software info
        if 'software' in line_lower and 'version' not in line_lower:
            critical['software']['software'] = value
        elif 'creatortool' in line_lower:
            critical['software']['creator'] = value
            
        # Owner info
        if ('artist' in line_lower or 'creator' in line_lower) and 'tool' not in line_lower:
            critical['owner']['artist'] = value
        elif 'copyright' in line_lower:
            critical['owner']['copyright'] = value
        elif 'ownername' in line_lower:
            critical['owner']['owner'] = value
    
    return critical

def organize_metadata(metadata):
    """Organize metadata into categories"""
    categories = {
        'GPS': [],
        'Camera': [],
        'Image': [],
        'File': [],
        'EXIF': [],
        'IPTC': [],
        'XMP': [],
        'Composite': [],
        'MakerNotes': [],
        'Other': []
    }
    
    if not metadata:
        return categories
    
    for line in metadata.split('\n'):
        if not line.strip() or ':' not in line:
            continue
            
        line_lower = line.lower()
        
        if 'gps' in line_lower:
            categories['GPS'].append(line)
        elif any(x in line_lower for x in ['camera', 'lens', 'flash', 'focallength', 'aperture', 'shutterspeed', 'iso']):
            categories['Camera'].append(line)
        elif any(x in line_lower for x in ['exif', 'exposure', 'metering', 'whitebalance']):
            categories['EXIF'].append(line)
        elif 'iptc' in line_lower:
            categories['IPTC'].append(line)
        elif 'xmp' in line_lower:
            categories['XMP'].append(line)
        elif 'composite' in line_lower:
            categories['Composite'].append(line)
        elif 'makernote' in line_lower:
            categories['MakerNotes'].append(line)
        elif any(x in line_lower for x in ['width', 'height', 'resolution', 'colorspace', 'bitdepth']):
            categories['Image'].append(line)
        elif any(x in line_lower for x in ['file', 'directory', 'filesize', 'mimetype']):
            categories['File'].append(line)
        else:
            categories['Other'].append(line)
    
    return categories

def display_metadata(file_path, metadata, mode='detailed', save_output=False):
    """Display extracted metadata with GPS debugging"""
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}File:{RESET} {file_path}")
    print(f"{GREEN}{'='*70}{RESET}\n")
    
    # Display file info
    file_info = get_file_info(file_path)
    print(f"{YELLOW}{BOLD}[*] FILE INFORMATION:{RESET}")
    print(f"    Filename: {file_info['filename']}")
    print(f"    Full Path: {file_info['absolute_path']}")
    print(f"    File Hash (MD5): {file_info['hash']}")
    print(f"    Size: {file_info['size']:,} bytes ({file_info['size']/1024:.2f} KB)")
    print(f"    Extension: {file_info['extension']}")
    print(f"    Created: {file_info['created']}")
    print(f"    Modified: {file_info['modified']}")
    print(f"    Accessed: {file_info['accessed']}")
    
    if not metadata:
        print(f"\n{RED}[!] No metadata could be extracted{RESET}")
        return
    
    # DEBUG: Show all GPS fields found
    gps_fields = debug_gps_fields(metadata)
    
    # Extract critical information
    critical = extract_critical_info(metadata)
    
    # Display GPS data prominently
    if critical['gps']:
        print(f"\n{RED}{BOLD}[!] GPS LOCATION DATA FOUND:{RESET}")
        for key, value in critical['gps'].items():
            print(f"    {RED}{key}:{RESET} {value}")
        
        # Try to build Google Maps link if we have coordinates
        if 'GPSLatitude' in critical['gps'] and 'GPSLongitude' in critical['gps']:
            lat = critical['gps']['GPSLatitude']
            lon = critical['gps']['GPSLongitude']
            print(f"    {RED}Google Maps:{RESET} https://www.google.com/maps?q={lat},{lon}")
        elif 'GPSPosition' in critical['gps']:
            coords = critical['gps']['GPSPosition'].replace(' ', '')
            print(f"    {RED}Google Maps:{RESET} https://www.google.com/maps?q={coords}")
    
    # Display Camera info
    if critical['camera']:
        print(f"\n{MAGENTA}{BOLD}[*] CAMERA INFORMATION:{RESET}")
        for key, value in critical['camera'].items():
            print(f"    {key.capitalize()}: {value}")
    
    # Display DateTime info
    if critical['datetime']:
        print(f"\n{CYAN}{BOLD}[*] DATE & TIME INFORMATION:{RESET}")
        for key, value in critical['datetime'].items():
            print(f"    {key.capitalize()}: {value}")
    
    # Display Software info
    if critical['software']:
        print(f"\n{BLUE}{BOLD}[*] SOFTWARE INFORMATION:{RESET}")
        for key, value in critical['software'].items():
            print(f"    {key.capitalize()}: {value}")
    
    # Display Owner info
    if critical['owner']:
        print(f"\n{YELLOW}{BOLD}[*] OWNER/COPYRIGHT INFORMATION:{RESET}")
        for key, value in critical['owner'].items():
            print(f"    {key.capitalize()}: {value}")
    
    # Display organized metadata by category
    if mode == 'detailed':
        print(f"\n{GREEN}{BOLD}[*] DETAILED METADATA BY CATEGORY:{RESET}")
        categories = organize_metadata(metadata)
        
        for category, items in categories.items():
            if items:
                print(f"\n  {CYAN}━━━ {category} ━━━{RESET}")
                for item in items:
                    if ':' in item:
                        parts = item.split(':', 1)
                        key = parts[0].strip()
                        value = parts[1].strip() if len(parts) > 1 else ''
                        print(f"    {key}: {value}")
    
    elif mode == 'raw':
        print(f"\n{GREEN}{BOLD}[*] RAW METADATA OUTPUT:{RESET}\n")
        for line in metadata.split('\n'):
            if line.strip():
                print(f"    {line}")
    
    # Count total metadata fields
    field_count = len([line for line in metadata.split('\n') if ':' in line])
    print(f"\n{GREEN}[+] Total metadata fields extracted: {field_count}{RESET}")
    
    # Save to file if requested
    if save_output:
        output_file = f"{file_info['absolute_path']}_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"SihmaSi Metadata Extraction Report\n")
                f.write(f"{'='*70}\n")
                f.write(f"File: {file_info['absolute_path']}\n")
                f.write(f"Extracted: {datetime.now()}\n")
                f.write(f"{'='*70}\n\n")
                f.write(metadata)
            
            print(f"\n{GREEN}[+] Metadata saved to: {output_file}{RESET}")
        except Exception as e:
            print(f"\n{RED}[!] Error saving file: {e}{RESET}")
    
    print(f"\n{GREEN}{'='*70}{RESET}\n")

def main():
    """Main function"""
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage:{RESET}")
        print(f"  python3 sihmasi.py <file_path> [options]")
        print(f"\n{YELLOW}Options:{RESET}")
        print(f"  -s, --save       Save metadata to a text file")
        print(f"  -r, --raw        Show raw unorganized output")
        print(f"  -d, --detailed   Show organized detailed output (default)")
        print(f"\n{YELLOW}Examples:{RESET}")
        print(f"  python3 sihmasi.py image.jpg")
        print(f"  python3 sihmasi.py photo.png -s\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    save_output = '--save' in sys.argv or '-s' in sys.argv
    raw_mode = '--raw' in sys.argv or '-r' in sys.argv
    mode = 'raw' if raw_mode else 'detailed'
    
    if not os.path.exists(file_path):
        print(f"{RED}[!] Error: File '{file_path}' does not exist{RESET}")
        sys.exit(1)
    
    print(f"{BLUE}[*] Extracting metadata from: {os.path.abspath(file_path)}{RESET}\n")
    
    metadata = extract_metadata_detailed(file_path)
    
    if metadata:
        display_metadata(file_path, metadata, mode, save_output)
        print(f"{GREEN}[+] Extraction complete!{RESET}")
    else:
        print(f"{RED}[!] Failed to extract metadata{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
        sys.exit(1)
