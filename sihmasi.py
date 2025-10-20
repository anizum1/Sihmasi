#!/usr/bin/env python3
"""
SihmaSi - Advanced Metadata Extraction Tool
Extract metadata from images and videos
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

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
{YELLOW}              For Images & Videos{RESET}
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

def extract_metadata(file_path):
    """Extract metadata using exiftool"""
    if not os.path.exists(file_path):
        print(f"{RED}[!] Error: File not found - {file_path}{RESET}")
        return None
    
    try:
        # Run exiftool
        result = subprocess.run(
            ['exiftool', '-a', '-G1', '-s', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{RED}[!] Error extracting metadata: {e}{RESET}")
        return None

def get_file_info(file_path):
    """Get basic file information"""
    file_stat = os.stat(file_path)
    return {
        'size': file_stat.st_size,
        'modified': datetime.fromtimestamp(file_stat.st_mtime),
        'created': datetime.fromtimestamp(file_stat.st_ctime),
        'extension': Path(file_path).suffix.lower()
    }

def extract_gps_data(metadata):
    """Extract GPS coordinates from metadata"""
    gps_data = {}
    
    if metadata:
        for line in metadata.split('\n'):
            line_lower = line.lower()
            if 'gpslatitude' in line_lower and 'ref' not in line_lower:
                gps_data['latitude'] = line.split(':', 1)[1].strip() if ':' in line else None
            elif 'gpslongitude' in line_lower and 'ref' not in line_lower:
                gps_data['longitude'] = line.split(':', 1)[1].strip() if ':' in line else None
            elif 'gpsaltitude' in line_lower and 'ref' not in line_lower:
                gps_data['altitude'] = line.split(':', 1)[1].strip() if ':' in line else None
            elif 'gpsposition' in line_lower:
                gps_data['position'] = line.split(':', 1)[1].strip() if ':' in line else None
    
    return gps_data

def display_metadata(file_path, metadata, save_output=False):
    """Display extracted metadata in a formatted way"""
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}File:{RESET} {file_path}")
    print(f"{GREEN}{'='*60}{RESET}\n")
    
    # Display file info
    file_info = get_file_info(file_path)
    print(f"{YELLOW}[*] File Information:{RESET}")
    print(f"    Size: {file_info['size']:,} bytes ({file_info['size']/1024:.2f} KB)")
    print(f"    Extension: {file_info['extension']}")
    print(f"    Modified: {file_info['modified']}")
    print(f"    Created: {file_info['created']}")
    
    # Extract and display GPS data prominently
    gps_data = extract_gps_data(metadata)
    if gps_data:
        print(f"\n{RED}{BOLD}[!] GPS LOCATION FOUND:{RESET}")
        if 'latitude' in gps_data and gps_data['latitude']:
            print(f"    {RED}Latitude:{RESET}  {gps_data['latitude']}")
        if 'longitude' in gps_data and gps_data['longitude']:
            print(f"    {RED}Longitude:{RESET} {gps_data['longitude']}")
        if 'position' in gps_data and gps_data['position']:
            print(f"    {RED}Position:{RESET}  {gps_data['position']}")
        if 'altitude' in gps_data and gps_data['altitude']:
            print(f"    {RED}Altitude:{RESET}  {gps_data['altitude']}")
        
        # Generate Google Maps link
        if 'position' in gps_data and gps_data['position']:
            coords = gps_data['position'].replace(' ', '')
            print(f"    {RED}Maps Link:{RESET} https://www.google.com/maps?q={coords}")
    
    print(f"\n{YELLOW}[*] Complete Metadata:{RESET}\n")
    
    if metadata:
        # Parse and display metadata
        for line in metadata.split('\n'):
            if line.strip():
                if ':' in line:
                    parts = line.split(':', 1)
                    key = parts[0].strip()
                    value = parts[1].strip() if len(parts) > 1 else ''
                    print(f"    {CYAN}{key}{RESET}: {value}")
        
        # Save to file if requested
        if save_output:
            output_file = f"{file_path}_metadata.txt"
            with open(output_file, 'w') as f:
                f.write(f"Metadata Extraction Report\n")
                f.write(f"File: {file_path}\n")
                f.write(f"Extracted: {datetime.now()}\n")
                f.write(f"{'='*60}\n\n")
                f.write(metadata)
            print(f"\n{GREEN}[+] Metadata saved to: {output_file}{RESET}")
    else:
        print(f"{RED}[!] No metadata could be extracted{RESET}")
    
    print(f"\n{GREEN}{'='*60}{RESET}\n")

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Parse arguments
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage:{RESET}")
        print(f"  python3 sihmasi.py <file_path> [options]")
        print(f"\n{YELLOW}Options:{RESET}")
        print(f"  -s, --save    Save metadata to a text file")
        print(f"\n{YELLOW}Examples:{RESET}")
        print(f"  python3 sihmasi.py image.jpg")
        print(f"  python3 sihmasi.py video.mp4 --save")
        print(f"  python3 sihmasi.py photo.png -s\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    save_output = '--save' in sys.argv or '-s' in sys.argv
    
    # Extract and display metadata
    print(f"{BLUE}[*] Extracting metadata from: {file_path}{RESET}")
    metadata = extract_metadata(file_path)
    
    if metadata:
        display_metadata(file_path, metadata, save_output)
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
