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

def get_file_hash(file_path):
    """Get MD5 hash of file to verify it's unique"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"Error: {e}"

def extract_metadata_detailed(file_path):
    """Extract ALL metadata using exiftool with maximum verbosity"""
    if not os.path.exists(file_path):
        print(f"{RED}[!] Error: File not found - {file_path}{RESET}")
        return None
    
    try:
        abs_path = os.path.abspath(file_path)
        
        # Extract ALL metadata including binary data, duplicates, and unknown tags
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
        
        # Categorize based on tag group or content
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

def extract_critical_info(metadata):
    """Extract most important metadata fields"""
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
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue
            
        key = parts[0].strip()
        value = parts[1].strip()
        
        # GPS data
        if 'gpslatitude' in line_lower and 'ref' not in line_lower:
            critical['gps']['latitude'] = value
        elif 'gpslongitude' in line_lower and 'ref' not in line_lower:
            critical['gps']['longitude'] = value
        elif 'gpsaltitude' in line_lower and 'ref' not in line_lower:
            critical['gps']['altitude'] = value
        elif 'gpsposition' in line_lower:
            critical['gps']['position'] = value
        elif 'gpsdatestamp' in line_lower:
            critical['gps']['date'] = value
        elif 'gpstimestamp' in line_lower:
            critical['gps']['time'] = value
            
        # Camera info
        elif 'make' in line_lower and 'model' not in line_lower:
            critical['camera']['make'] = value
        elif 'model' in line_lower and 'camera' in line_lower:
            critical['camera']['model'] = value
        elif 'lensmodel' in line_lower or 'lensid' in line_lower:
            critical['camera']['lens'] = value
        elif 'serialnumber' in line_lower:
            critical['camera']['serial'] = value
            
        # DateTime info
        elif 'datetimeoriginal' in line_lower:
            critical['datetime']['original'] = value
        elif 'createdate' in line_lower:
            critical['datetime']['created'] = value
        elif 'modifydate' in line_lower:
            critical['datetime']['modified'] = value
            
        # Software/Editor info
        elif 'software' in line_lower:
            critical['software']['software'] = value
        elif 'creatortool' in line_lower:
            critical['software']['creator'] = value
            
        # Owner/Copyright info
        elif 'artist' in line_lower or 'creator' in line_lower:
            critical['owner']['artist'] = value
        elif 'copyright' in line_lower:
            critical['owner']['copyright'] = value
        elif 'ownername' in line_lower:
            critical['owner']['owner'] = value
    
    return critical

def display_metadata(file_path, metadata, mode='detailed', save_output=False):
    """Display extracted metadata"""
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
    
    # Extract critical information
    critical = extract_critical_info(metadata)
    
    # Display GPS data prominently
    if critical['gps']:
        print(f"\n{RED}{BOLD}[!] GPS LOCATION DATA:{RESET}")
        for key, value in critical['gps'].items():
            print(f"    {RED}{key.capitalize()}:{RESET} {value}")
        
        if 'position' in critical['gps']:
            coords = critical['gps']['position'].replace(' ', '')
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
        abs_path = os.path.abspath(file_path)
        output_file = f"{abs_path}_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"SihmaSi Metadata Extraction Report\n")
                f.write(f"{'='*70}\n")
                f.write(f"File: {abs_path}\n")
                f.write(f"File Hash (MD5): {file_info['hash']}\n")
                f.write(f"Extracted: {datetime.now()}\n")
                f.write(f"{'='*70}\n\n")
                f.write(f"FILE INFORMATION:\n")
                f.write(f"  Size: {file_info['size']:,} bytes\n")
                f.write(f"  Extension: {file_info['extension']}\n")
                f.write(f"  Modified: {file_info['modified']}\n")
                f.write(f"  Created: {file_info['created']}\n\n")
                
                if critical['gps']:
                    f.write(f"GPS LOCATION:\n")
                    for key, value in critical['gps'].items():
                        f.write(f"  {key.capitalize()}: {value}\n")
                    f.write("\n")
                
                f.write(f"COMPLETE METADATA:\n")
                f.write(f"{'-'*70}\n")
                f.write(metadata)
            
            print(f"\n{GREEN}[+] Metadata saved to: {output_file}{RESET}")
        except Exception as e:
            print(f"\n{RED}[!] Error saving file: {e}{RESET}")
    
    print(f"\n{GREEN}{'='*70}{RESET}\n")

def show_metadata_help():
    """Show what metadata can be extracted"""
    help_text = f"""
{CYAN}{BOLD}METADATA TYPES THAT CAN BE EXTRACTED:{RESET}

{RED}{BOLD}📍 GPS/Location Data:{RESET}
  • GPS Latitude & Longitude (exact coordinates)
  • GPS Altitude (elevation)
  • GPS Date & Time stamps
  • GPS Speed, Direction, Satellites
  
{MAGENTA}{BOLD}📷 Camera Information:{RESET}
  • Camera Make & Model
  • Lens Model & Serial Number
  • Camera Serial Number
  • Firmware Version
  
{CYAN}{BOLD}⚙️ Photo Settings (EXIF):{RESET}
  • ISO Speed, Aperture (F-stop)
  • Shutter Speed, Exposure Time
  • White Balance, Metering Mode
  • Flash Settings, Focus Mode
  • Focal Length, Zoom
  
{YELLOW}{BOLD}🖼️ Image Properties:{RESET}
  • Image Width & Height (resolution)
  • Color Space, Bit Depth
  • Compression, Quality
  • Orientation, Thumbnail
  
{BLUE}{BOLD}📅 Date & Time:{RESET}
  • Date/Time Original (when photo taken)
  • Create Date, Modify Date
  • Digitized Date
  • Time Zone information
  
{GREEN}{BOLD}💻 Software/Editor Info:{RESET}
  • Software used (Photoshop, GIMP, etc.)
  • Creator Tool, History
  • Edit count, Processing applied
  
{MAGENTA}{BOLD}👤 Owner/Copyright:{RESET}
  • Artist/Photographer name
  • Copyright information
  • Owner name, Contact info
  • Usage rights, Credits
  
{CYAN}{BOLD}🎥 Video Specific (for videos):{RESET}
  • Duration, Frame Rate (FPS)
  • Video Codec, Audio Codec
  • Bitrate, Resolution
  • Handler, Encoder
  
{YELLOW}{BOLD}📝 IPTC/XMP Metadata:{RESET}
  • Keywords, Caption, Description
  • Category, Subject, Scene
  • City, State, Country
  • Event, Instructions
  
{RED}{BOLD}🔧 Technical Data:{RESET}
  • File Format, MIME Type
  • Encoding, Profile
  • Thumbnail image data
  • Color Profile (ICC)
  • Manufacturer Notes (MakerNotes)

{GREEN}Note: Not all files contain all metadata types. It depends on:
  • Device used (phone, camera, scanner)
  • Settings enabled (GPS, location services)
  • Post-processing (editing may strip data)
  • File format (JPG retains more than PNG)
{RESET}
"""
    print(help_text)

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
        print(f"  -s, --save       Save metadata to a text file")
        print(f"  -r, --raw        Show raw unorganized output")
        print(f"  -d, --detailed   Show organized detailed output (default)")
        print(f"  -h, --help       Show what metadata can be extracted")
        print(f"\n{YELLOW}Examples:{RESET}")
        print(f"  python3 sihmasi.py image.jpg")
        print(f"  python3 sihmasi.py video.mp4 --save")
        print(f"  python3 sihmasi.py photo.png -s -r")
        print(f"  python3 sihmasi.py --help\n")
        sys.exit(1)
    
    # Show help
    if '--help' in sys.argv or '-h' in sys.argv:
        show_metadata_help()
        sys.exit(0)
    
    file_path = sys.argv[1]
    save_output = '--save' in sys.argv or '-s' in sys.argv
    raw_mode = '--raw' in sys.argv or '-r' in sys.argv
    mode = 'raw' if raw_mode else 'detailed'
    
    # Verify file exists before processing
    if not os.path.exists(file_path):
        print(f"{RED}[!] Error: File '{file_path}' does not exist{RESET}")
        sys.exit(1)
    
    # Extract and display metadata
    print(f"{BLUE}[*] Extracting ALL metadata from: {os.path.abspath(file_path)}{RESET}")
    print(f"{BLUE}[*] Using maximum extraction mode (including binary and unknown tags){RESET}\n")
    
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
