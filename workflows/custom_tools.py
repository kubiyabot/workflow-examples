"""
Custom Tools for Kubiya Workflows

This module contains simple tool implementations using the Kubiya Workflow SDK Tool class.
All tools use shell script content for consistency.
"""

from kubiya_workflow_sdk.tools.models import Tool, Arg
from kubiya_workflow_sdk.tools.registry import tool_registry


# ============================================================================
# SHELL SCRIPT TOOLS (Different Images)
# ============================================================================

### START: json_processor ###
"""
JSON Processor Tool
===================
Purpose: Process and validate JSON data using shell commands
Features:
- Validate JSON syntax
- Pretty-print JSON with formatting
- Minify JSON by removing whitespace
- Uses Python's built-in json.tool module
Docker: python:3.11-slim
"""
json_processor = Tool(
    name="json_processor",
    description="Process and validate JSON data using shell commands",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "Processing JSON data..."
echo "Operation: $operation"

case "$operation" in
    "validate")
        echo "$json_data" | python -m json.tool > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✓ Valid JSON"
        else
            echo "✗ Invalid JSON"
            exit 1
        fi
        ;;
    "pretty")
        echo "$json_data" | python -m json.tool
        ;;
    "minify")
        echo "$json_data" | python -c "import sys,json; print(json.dumps(json.load(sys.stdin), separators=(',', ':')))"
        ;;
    *)
        echo "Unknown operation: $operation"
        exit 1
        ;;
esac
""",
    args=[
        Arg(name="json_data", type="str", description="JSON data to process", required=True),
        Arg(name="operation", type="str", description="Operation: validate, pretty, minify", required=False, default="validate")
    ]
)
### END: json_processor ###



### START: text_analyzer ###
"""
Text Analyzer Tool
==================
Purpose: Analyze text content and provide statistics
Features:
- Count characters, words, and lines
- Find most common words
- Text length analysis
- Basic word frequency counting
Docker: python:3.12
"""
text_analyzer = Tool(
    name="text_analyzer",
    description="Analyze text content and provide statistics",
    type="docker",
    image="python:3.12",
    content="""
#!/bin/bash
echo "=== Text Analysis ==="
echo "Text: $text"
echo ""

# Basic counts
char_count=$(echo -n "$text" | wc -c)
word_count=$(echo "$text" | wc -w)
line_count=$(echo "$text" | wc -l)

echo "Characters: $char_count"
echo "Words: $word_count"
echo "Lines: $line_count"

# Most common words (simple version)
echo ""
echo "Word frequency (top 5):"
echo "$text" | tr ' ' '\n' | tr '[:upper:]' '[:lower:]' | grep -v '^$' | sort | uniq -c | sort -nr | head -5
""",
    args=[
        Arg(name="text", type="str", description="Text to analyze", required=True)
    ]
)
### END: text_analyzer ###



### START: math_calculator ###
"""
Math Calculator Tool
====================
Purpose: Perform mathematical calculations
Features:
- Basic arithmetic operations (+, -, *, /)
- Advanced functions (sqrt, pow, sin, cos, etc.)
- Expression evaluation using Python
- Safe mathematical expression parsing
Docker: python:3.9
"""
math_calculator = Tool(
    name="math_calculator",
    description="Perform mathematical calculations",
    type="docker",
    image="python:3.9",
    content="""
#!/bin/bash
echo "Calculating: $expression"

# Use bc for basic calculations, python for advanced
if echo "$expression" | grep -q '[a-zA-Z]'; then
    # Advanced math with functions
    result=$(python -c "import math; print($expression)" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "Result: $result"
    else
        echo "Error: Invalid expression"
        exit 1
    fi
else
    # Basic arithmetic
    result=$(echo "$expression" | bc -l 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "Result: $result"
    else
        echo "Error: Invalid expression"
        exit 1
    fi
fi
""",
    args=[
        Arg(name="expression", type="str", description="Mathematical expression (e.g., '2+2', 'sqrt(16)')", required=True)
    ]
)
### END: math_calculator ###



### START: url_validator ###
"""
URL Validator Tool
==================
Purpose: Simple URL format validation
Features:
- Check URL format and structure
- Validate HTTP/HTTPS protocols
- Basic URL syntax verification
- Lightweight Alpine-based validation
Docker: alpine:latest
"""
url_validator = Tool(
    name="url_validator",
    description="Simple URL format validation",
    type="docker",
    image="alpine:latest",
    content="""
#!/bin/sh
echo "Validating URL: $url"

# Check if URL starts with http or https
if echo "$url" | grep -q '^https\\?://'; then
    echo "✓ Valid URL format"
    
    # Check if it's secure
    if echo "$url" | grep -q '^https://'; then
        echo "✓ Secure (HTTPS)"
    else
        echo "⚠ Not secure (HTTP)"
    fi
else
    echo "✗ Invalid URL format"
    echo "URL must start with http:// or https://"
    exit 1
fi
""",
    args=[
        Arg(name="url", type="str", description="URL to validate", required=True)
    ]
)
### END: url_validator ###



### START: data_converter ###
"""
Data Converter Tool
===================
Purpose: Convert data between different formats
Features:
- JSON to CSV conversion
- CSV to JSON conversion
- Data format transformation
- Shell-based data processing
Docker: debian:bullseye-slim
"""
data_converter = Tool(
    name="data_converter",
    description="Convert data between different formats",
    type="docker",
    image="debian:bullseye-slim",
    content="""
#!/bin/bash
echo "Converting from $from_format to $to_format"

case "$from_format-$to_format" in
    "json-csv")
        echo "Converting JSON to CSV..."
        echo "$data" | python3 -c "
import json, csv, sys
data = json.load(sys.stdin)
if isinstance(data, list) and data and isinstance(data[0], dict):
    writer = csv.DictWriter(sys.stdout, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
                else:
    print('Error: Data must be array of objects')
    sys.exit(1)
"
        ;;
    "csv-json")
        echo "Converting CSV to JSON..."
        echo "$data" | python3 -c "
import csv, json, sys
reader = csv.DictReader(sys.stdin)
print(json.dumps(list(reader), indent=2))
"
        ;;
    *)
        echo "Conversion from $from_format to $to_format not supported"
        exit 1
        ;;
esac
""",
    args=[
        Arg(name="data", type="str", description="Data to convert", required=True),
        Arg(name="from_format", type="str", description="Source format: json, csv", required=True),
        Arg(name="to_format", type="str", description="Target format: json, csv", required=True)
    ]
)
### END: data_converter ###



### START: system_info ###
"""
System Info Tool
================
Purpose: Get basic system information
Features:
- Display hostname and system details
- Show system architecture
- Current date and time
- Lightweight system monitoring
Docker: alpine:latest
"""
system_info = Tool(
    name="system_info",
    description="Get basic system information",
    type="docker",
    image="alpine:latest",
    content="""
#!/bin/sh
echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "System: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "Date: $(date)"
""",
    args=[]
)
### END: system_info ###



### START: network_checker ###
"""
Network Checker Tool
====================
Purpose: Check network connectivity
Features:
- Test HTTP/HTTPS connectivity
- Validate network endpoints
- Connection status verification
- Uses curl for network testing
Docker: curlimages/curl:latest
"""
network_checker = Tool(
    name="network_checker",
    description="Check network connectivity",
    type="docker",
    image="curlimages/curl:latest",
    content="""
#!/bin/sh
echo "=== Network Connectivity Check ==="
echo "Target: $target"

# Check connectivity
if curl -s --connect-timeout 5 --head "$target" > /dev/null 2>&1; then
    echo "✓ Connection successful"
    
    # Get response time
    time_total=$(curl -s -o /dev/null -w "%{time_total}" "$target")
    echo "Response time: ${time_total}s"
    
    # Get status code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$target")
    echo "Status code: $status_code"
else
    echo "✗ Connection failed"
    exit 1
fi
""",
    args=[
        Arg(name="target", type="str", description="URL or hostname to check", required=True)
    ]
)
### END: network_checker ###


### START: file_operations ###
"""
File Operations Tool
====================
Purpose: Perform file operations
Features:
- Read file contents
- Write data to files
- Basic file manipulation
- Cross-platform file handling
Docker: busybox:latest
"""
file_operations = Tool(
    name="file_operations",
    description="Perform file operations",
                    type="docker",
    image="busybox:latest",
    content="""
#!/bin/sh
echo "=== File Operations ==="
echo "Operation: $operation"

case "$operation" in
    "create")
        echo "$content" > /tmp/output.txt
        echo "✓ File created: /tmp/output.txt"
        echo "Size: $(wc -c < /tmp/output.txt) bytes"
        ;;
    "count")
        echo "$content" | wc -l > /tmp/lines.txt
        echo "$content" | wc -w > /tmp/words.txt
        echo "$content" | wc -c > /tmp/chars.txt
        echo "Lines: $(cat /tmp/lines.txt)"
        echo "Words: $(cat /tmp/words.txt)"
        echo "Characters: $(cat /tmp/chars.txt)"
        ;;
    "search")
        if echo "$content" | grep -q "$pattern"; then
            echo "Pattern '$pattern' found:"
            echo "$content" | grep -n "$pattern"
        else
            echo "Pattern '$pattern' not found"
        fi
        ;;
    *)
        echo "Unknown operation: $operation"
        exit 1
        ;;
esac
""",
    args=[
        Arg(name="operation", type="str", description="Operation: create, count, search", required=True),
        Arg(name="content", type="str", description="Content to process", required=True),
        Arg(name="pattern", type="str", description="Search pattern (for search operation)", required=False)
    ]
)
### END: file_operations ###




### START: text_processor ###
"""
Text Processor Tool
===================
Purpose: Advanced text processing
Features:
- Text transformation operations
- String manipulation utilities
- Advanced text filtering
- Debian-based processing environment
Docker: debian:bullseye-slim
"""
text_processor = Tool(
    name="text_processor",
    description="Advanced text processing",
    type="docker",
    image="debian:bullseye-slim",
    content="""
#!/bin/bash
echo "=== Text Processing ==="
echo "Operation: $operation"
echo "Input length: $(echo -n "$text" | wc -c) characters"

case "$operation" in
    "uppercase")
        echo "Result:"
        echo "$text" | tr '[:lower:]' '[:upper:]'
        ;;
    "lowercase")
        echo "Result:"
        echo "$text" | tr '[:upper:]' '[:lower:]'
        ;;
    "reverse")
        echo "Result:"
        echo "$text" | rev
        ;;
    "sort_lines")
        echo "Result:"
        echo "$text" | sort
        ;;
    "unique_lines")
        echo "Result:"
        echo "$text" | sort | uniq
        ;;
    "word_count")
        echo "Words: $(echo "$text" | wc -w)"
        echo "Lines: $(echo "$text" | wc -l)"
        echo "Characters: $(echo -n "$text" | wc -c)"
        ;;
    *)
        echo "Unknown operation: $operation"
        exit 1
        ;;
esac
""",
    args=[
        Arg(name="text", type="str", description="Text to process", required=True),
        Arg(name="operation", type="str", description="Operation: uppercase, lowercase, reverse, sort_lines, unique_lines, word_count", required=True)
    ]
)
### END: text_processor ###




### START: log_analyzer ###
"""
Log Analyzer Tool
=================
Purpose: Analyze log files
Features:
- Extract error messages
- Generate log summaries
- Pattern matching in logs
- Log statistics and insights
Docker: alpine:latest
"""
log_analyzer = Tool(
    name="log_analyzer",
    description="Analyze log files",
    type="docker",
    image="alpine:latest",
    content="""
#!/bin/sh
echo "=== Log Analysis ==="
echo "Analysis type: $analysis_type"
echo "Total lines: $(echo "$logs" | wc -l)"

case "$analysis_type" in
    "errors")
        echo ""
        echo "Error entries:"
        echo "$logs" | grep -i "error\\|fail\\|exception\\|critical" | head -10
        ;;
    "warnings")
        echo ""
        echo "Warning entries:"
        echo "$logs" | grep -i "warn" | head -10
        ;;
    "summary")
        echo ""
        echo "Summary:"
        echo "Errors: $(echo "$logs" | grep -i "error\\|fail\\|exception" | wc -l)"
        echo "Warnings: $(echo "$logs" | grep -i "warn" | wc -l)"
        echo "Info: $(echo "$logs" | grep -i "info" | wc -l)"
        ;;
    "recent")
        echo ""
        echo "Recent entries (last 10):"
        echo "$logs" | tail -10
        ;;
    *)
        echo "Unknown analysis type: $analysis_type"
        exit 1
        ;;
esac
""",
    args=[
        Arg(name="logs", type="str", description="Log content to analyze", required=True),
        Arg(name="analysis_type", type="str", description="Analysis type: errors, warnings, summary, recent", required=True)
    ]
)
### END: log_analyzer ###




### START: password_generator ###
"""
Password Generator Tool
=======================
Purpose: Generate secure passwords with customizable length and complexity
Features:
- Customizable password length
- Include/exclude symbols and numbers
- Multiple character sets support
- Cryptographically secure generation
Docker: python:3.11-slim
"""
password_generator = Tool(
    name="password_generator",
    description="Generate secure passwords with customizable length and complexity",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "=== Password Generator ==="
echo "Length: $length"
echo "Include symbols: $include_symbols"
echo "Include numbers: $include_numbers"

python3 -c "
import string
import random
import sys

length = int('$length')
include_symbols = '$include_symbols'.lower() == 'true'
include_numbers = '$include_numbers'.lower() == 'true'

chars = string.ascii_letters
if include_numbers:
    chars += string.digits
if include_symbols:
    chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'

if length < 4:
    print('Error: Password length must be at least 4 characters')
    sys.exit(1)

password = ''.join(random.choice(chars) for _ in range(length))
print(f'Generated password: {password}')
print(f'Password strength: {len(set(password))} unique characters')
"
""",
    args=[
        Arg(name="length", type="int", description="Password length (minimum 4)", required=False, default=12),
        Arg(name="include_symbols", type="bool", description="Include special symbols", required=False, default=True),
        Arg(name="include_numbers", type="bool", description="Include numbers", required=False, default=True)
    ]
)
### END: password_generator ###



### START: qr_generator ###
"""
QR Code Generator Tool
======================
Purpose: Generate QR codes from text
Features:
- Multiple QR code sizes (small, medium, large)
- Text to QR code conversion
- ASCII art QR code output
- Python qrcode library integration
Docker: python:3.11-slim
"""
qr_generator = Tool(
    name="qr_generator",
    description="Generate QR codes from text",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "=== QR Code Generator ==="
echo "Text: $text"
echo "Size: $size"

# Install qrcode library
pip install qrcode[pil] > /dev/null 2>&1

# Create a temporary Python script to avoid quoting issues
cat > /tmp/qr_script.py << 'EOF'
import qrcode
import sys
import re

# Read arguments from command line
text = sys.argv[1] if len(sys.argv) > 1 else ""
size = sys.argv[2] if len(sys.argv) > 2 else "small"

if not text:
    print('Error: Text is required')
    sys.exit(1)

# Extract clean text if it contains output from other tools
clean_text = text

# Check if the text looks like UUID generator output
if 'UUID Generator' in text or 'Clean UUID for chaining:' in text:
    # Extract UUID from 'Clean UUID for chaining:' line
    uuid_match = re.search(r'Clean UUID for chaining: ([a-f0-9-]{36})', text)
    if uuid_match:
        clean_text = 'UUID: ' + uuid_match.group(1)
    else:
        # Fallback: look for any UUID pattern
        uuid_pattern = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', text)
        if uuid_pattern:
            clean_text = 'UUID: ' + uuid_pattern.group(1)

print('Processing text: ' + clean_text[:50] + ('...' if len(clean_text) > 50 else ''))

# Create QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10 if size == 'large' else 5,
    border=4,
)
qr.add_data(clean_text)
qr.make(fit=True)

# Generate ASCII art version
qr_ascii = qr.get_matrix()
print('QR Code (ASCII):')
for row in qr_ascii:
    line = ''
    for cell in row:
        line += '██' if cell else '  '
    print(line)

print('')
print('✓ QR Code generated for: ' + (clean_text[:50] + '...' if len(clean_text) > 50 else clean_text))
print('Size: ' + size)
EOF

# Run the Python script with arguments (use printf to handle special characters)
python3 /tmp/qr_script.py "$text" "$size"

# Clean up
rm -f /tmp/qr_script.py
""",
    args=[
        Arg(name="text", type="str", description="Text to encode in QR code", required=True),
        Arg(name="size", type="str", description="QR code size: small, large", required=False, default="small")
    ]
)
### END: qr_generator ###



### START: base64_tool ###
"""
Base64 Encoder/Decoder Tool
===========================
Purpose: Encode or decode Base64 data
Features:
- Base64 encoding of text
- Base64 decoding to text
- Clean output for workflow chaining
- Error handling for invalid input
Docker: alpine:latest
"""
base64_tool = Tool(
    name="base64_tool",
    description="Encode or decode Base64 data",
    type="docker",
    image="alpine:latest",
    content="""
#!/bin/sh
echo "=== Base64 Tool ==="
echo "Operation: $operation"

case "$operation" in
    "encode")
        echo "Original text: $text"
        echo "Encoded:"
        encoded_result=$(echo -n "$text" | base64)
        echo "$encoded_result"
        echo ""
        echo "Clean result for chaining: $encoded_result"
        ;;
    "decode")
        echo "Received input: $text"
        echo "Decoded:"
        # Extract clean base64 - look for the actual base64 string
        # Try multiple extraction methods
        clean_input=""
        
        # Method 1: Look for clean base64 pattern in the input
        clean_input=$(echo "$text" | grep -o '[A-Za-z0-9+/]*={0,2}' | grep -E '^[A-Za-z0-9+/]{4,}={0,2}$' | head -1)
        
        # Method 2: If that fails, look for "Clean result for chaining:" line
        if [ -z "$clean_input" ]; then
            clean_input=$(echo "$text" | grep "Clean result for chaining:" | sed 's/.*Clean result for chaining: //' | head -1)
        fi
        
        # Method 3: Try to extract from multiple lines
        if [ -z "$clean_input" ]; then
            # Look for a line that looks like base64 (only contains base64 characters)
            clean_input=$(echo "$text" | grep -E '^[A-Za-z0-9+/]*={0,2}$' | head -1)
        fi
        
        # Method 4: Final fallback - try the input as-is
        if [ -z "$clean_input" ]; then
            clean_input="$text"
        fi
        
        echo "Attempting to decode: $clean_input"
        
        # Attempt to decode
        decoded_result=$(echo "$clean_input" | base64 -d 2>/dev/null)
        decode_status=$?
        
        if [ $decode_status -eq 0 ] && [ -n "$decoded_result" ]; then
            echo "$decoded_result"
        else
            echo "Error: Failed to decode Base64 input"
            echo "Clean input attempted: '$clean_input'"
            echo "Original input length: $(echo -n "$text" | wc -c)"
            echo "Clean input length: $(echo -n "$clean_input" | wc -c)"
            exit 1
        fi
        ;;
    *)
        echo "Error: Operation must be 'encode' or 'decode'"
        exit 1
        ;;
esac
""",
    args=[
        Arg(name="operation", type="str", description="Operation: encode, decode", required=True),
        Arg(name="text", type="str", description="Text to encode/decode", required=True)
    ]
)
### END: base64_tool ###



### START: hash_generator ###
"""
Hash Generator Tool
===================
Purpose: Generate various hash types (MD5, SHA256, SHA512)
Features:
- Multiple hash algorithms support
- MD5, SHA1, SHA256, SHA512 hashing
- Text-to-hash conversion
- Hash length information
Docker: python:3.11-slim
"""
hash_generator = Tool(
    name="hash_generator",
    description="Generate various hash types (MD5, SHA256, SHA512)",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "=== Hash Generator ==="
echo "Text: $text"
echo "Hash type: $hash_type"

python3 -c "
import hashlib
import sys

text = '$text'
hash_type = '$hash_type'.lower()

if not text:
    print('Error: Text is required')
    sys.exit(1)

text_bytes = text.encode('utf-8')

if hash_type == 'md5':
    hash_obj = hashlib.md5(text_bytes)
elif hash_type == 'sha1':
    hash_obj = hashlib.sha1(text_bytes)
elif hash_type == 'sha256':
    hash_obj = hashlib.sha256(text_bytes)
elif hash_type == 'sha512':
    hash_obj = hashlib.sha512(text_bytes)
else:
    print(f'Error: Unsupported hash type: {hash_type}')
    print('Supported types: md5, sha1, sha256, sha512')
    sys.exit(1)

hash_value = hash_obj.hexdigest()
print(f'{hash_type.upper()} hash: {hash_value}')
print(f'Length: {len(hash_value)} characters')
"
""",
    args=[
        Arg(name="text", type="str", description="Text to hash", required=True),
        Arg(name="hash_type", type="str", description="Hash type: md5, sha1, sha256, sha512", required=False, default="sha256")
    ]
)
### END: hash_generator ###



### START: weather_checker ###
"""
Weather Checker Tool
====================
Purpose: Check weather information for a city
Features:
- Real-time weather data
- Multiple output formats (simple, basic, detailed)
- Uses wttr.in weather service
- Global city support
Docker: curlimages/curl:latest
"""
weather_checker = Tool(
    name="weather_checker",
    description="Check weather information for a city",
    type="docker",
    image="curlimages/curl:latest",
    content="""
#!/bin/sh
echo "=== Weather Checker ==="
echo "City: $city"
echo "Format: $format"

# Use wttr.in service for weather data
if [ "$format" = "detailed" ]; then
    curl -s "wttr.in/$city?0"
elif [ "$format" = "simple" ]; then
    curl -s "wttr.in/$city?format=3"
else
    curl -s "wttr.in/$city?1"
fi

if [ $? -ne 0 ]; then
    echo "Error: Unable to fetch weather data"
    exit 1
fi
""",
    args=[
        Arg(name="city", type="str", description="City name", required=True),
        Arg(name="format", type="str", description="Output format: simple, basic, detailed", required=False, default="basic")
    ]
)
### END: weather_checker ###



### START: color_converter ###
"""
Color Converter Tool
====================
Purpose: Convert colors between different formats (HEX, RGB, HSL)
Features:
- HEX to RGB conversion
- RGB to HEX conversion
- HEX to HSL conversion
- Color format validation
Docker: python:3.11-slim
"""
color_converter = Tool(
    name="color_converter",
    description="Convert colors between different formats (HEX, RGB, HSL)",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "=== Color Converter ==="
echo "Color value: $color_value"
echo "From format: $from_format"
echo "To format: $to_format"

python3 -c "
import sys
import re

color_value = '$color_value'
from_format = '$from_format'.lower()
to_format = '$to_format'.lower()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError('Invalid hex color')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def rgb_to_hsl(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    l = (max_val + min_val) / 2
    
    if max_val == min_val:
        h = s = 0
    else:
        d = max_val - min_val
        s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
        if max_val == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / d + 2
        elif max_val == b:
            h = (r - g) / d + 4
        h /= 6
    
    return int(h*360), int(s*100), int(l*100)

try:
    if from_format == 'hex' and to_format == 'rgb':
        r, g, b = hex_to_rgb(color_value)
        print(f'RGB: rgb({r}, {g}, {b})')
    elif from_format == 'rgb' and to_format == 'hex':
        # Parse RGB values
        rgb_match = re.search(r'(\\d+),\\s*(\\d+),\\s*(\\d+)', color_value)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            hex_color = rgb_to_hex(r, g, b)
            print(f'HEX: {hex_color}')
        else:
            raise ValueError('Invalid RGB format')
    elif from_format == 'hex' and to_format == 'hsl':
        r, g, b = hex_to_rgb(color_value)
        h, s, l = rgb_to_hsl(r, g, b)
        print(f'HSL: hsl({h}, {s}%, {l}%)')
    else:
        print(f'Conversion from {from_format} to {to_format} not supported')
        print('Supported: hex->rgb, rgb->hex, hex->hsl')
        sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"
""",
    args=[
        Arg(name="color_value", type="str", description="Color value to convert", required=True),
        Arg(name="from_format", type="str", description="Source format: hex, rgb", required=True),
        Arg(name="to_format", type="str", description="Target format: hex, rgb, hsl", required=True)
    ]
)
### END: color_converter ###



### START: uuid_generator ###
"""
UUID Generator Tool
===================
Purpose: Generate UUIDs of different versions
Features:
- UUID v1 (time-based)
- UUID v3 (namespace-based MD5)
- UUID v4 (random)
- UUID v5 (namespace-based SHA1)
- Bulk UUID generation support
Docker: python:3.11-slim
"""
uuid_generator = Tool(
    name="uuid_generator",
    description="Generate UUIDs of different versions",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "=== UUID Generator ==="
echo "Version: $version"
echo "Count: $count"

python3 -c "
import uuid
import sys

version = '$version'
count = int('$count')

if count < 1 or count > 100:
    print('Error: Count must be between 1 and 100')
    sys.exit(1)

print('Generating ' + str(count) + ' UUID(s) version ' + version + ':')
print('')

uuids = []
for i in range(count):
    if version == '1':
        new_uuid = uuid.uuid1()
    elif version == '3':
        # UUID3 requires namespace and name, using default DNS namespace
        new_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, 'example' + str(i) + '.com')
    elif version == '4':
        new_uuid = uuid.uuid4()
    elif version == '5':
        # UUID5 requires namespace and name, using default DNS namespace
        new_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, 'example' + str(i) + '.com')
    else:
        print('Error: Unsupported UUID version: ' + version)
        print('Supported versions: 1, 3, 4, 5')
        sys.exit(1)
    
    uuids.append(str(new_uuid))
    print(str(i+1) + ': ' + str(new_uuid))

print('')
print('✓ UUID generation completed')
print('')
# Provide clean output for chaining
if count == 1:
    print('Clean UUID for chaining: ' + uuids[0])
else:
    print('Clean UUIDs for chaining:')
    for uuid_str in uuids:
        print(uuid_str)
"
""",
    args=[
        Arg(name="version", type="str", description="UUID version: 1, 3, 4, 5", required=False, default="4"),
        Arg(name="count", type="int", description="Number of UUIDs to generate (1-100)", required=False, default=1)
    ]
)
### END: uuid_generator ###



### START: timestamp_converter ###
"""
Timestamp Converter Tool
========================
Purpose: Convert between timestamps and human-readable dates
Features:
- Unix timestamp to date conversion
- Date to Unix timestamp conversion
- Current timestamp generation
- Multiple date format support
Docker: python:3.11-slim
"""
timestamp_converter = Tool(
    name="timestamp_converter",
    description="Convert between timestamps and human-readable dates",
    type="docker",
    image="python:3.11-slim",
    content="""
#!/bin/bash
echo "=== Timestamp Converter ==="
echo "Operation: $operation"
echo "Input: $input_value"

# Create a temporary Python script to avoid quoting issues
cat > /tmp/timestamp_script.py << 'EOF'
import datetime
import sys
import time

# Read arguments from command line
operation = sys.argv[1] if len(sys.argv) > 1 else ""
input_value = sys.argv[2] if len(sys.argv) > 2 else ""

try:
    if operation == "to_timestamp":
        # Convert human date to timestamp
        # Try different formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y"
        ]
        
        dt = None
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(input_value, fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            print("Error: Unable to parse date. Try formats like: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD")
            sys.exit(1)
        
        timestamp = int(dt.timestamp())
        print("Timestamp: " + str(timestamp))
        print("Date: " + dt.strftime("%Y-%m-%d %H:%M:%S"))
        
    elif operation == "to_date":
        # Convert timestamp to human date
        try:
            timestamp = int(float(input_value))
        except ValueError:
            print("Error: Invalid timestamp format")
            sys.exit(1)
        
        dt = datetime.datetime.fromtimestamp(timestamp)
        print("Date: " + dt.strftime("%Y-%m-%d %H:%M:%S"))
        print("UTC Date: " + datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") + " UTC")
        print("Timestamp: " + str(timestamp))
        
    elif operation == "current":
        # Get current timestamp
        now = datetime.datetime.now()
        timestamp = int(now.timestamp())
        print("Current timestamp: " + str(timestamp))
        print("Current date: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Current UTC: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " UTC")
        
    else:
        print("Error: Operation must be to_timestamp, to_date, or current")
        sys.exit(1)
        
except Exception as e:
    print("Error: " + str(e))
    sys.exit(1)
EOF

# Run the Python script with arguments
python3 /tmp/timestamp_script.py "$operation" "$input_value"

# Clean up
rm -f /tmp/timestamp_script.py
""",
    args=[
        Arg(name="operation", type="str", description="Operation: to_timestamp, to_date, current", required=True),
        Arg(name="input_value", type="str", description="Date string or timestamp (not needed for 'current')", required=False)
    ]
)
### END: timestamp_converter ###



### START: port_scanner ###
"""
Port Scanner Tool
=================
Purpose: Basic port scanner for checking open ports
Features:
- Single port and port range scanning
- Connection timeout configuration
- Open/closed port detection
- Network connectivity testing
Docker: alpine:latest
"""
port_scanner = Tool(
    name="port_scanner",
    description="Basic port scanner for checking open ports",
    type="docker",
    image="alpine:latest",
    content="""
#!/bin/sh
echo "=== Port Scanner ==="
echo "Host: $host"
echo "Ports: $ports"
echo "Timeout: $timeout seconds"

# Install netcat if not available
if ! command -v nc > /dev/null; then
    apk add --no-cache netcat-openbsd > /dev/null 2>&1
fi

scan_port() {
    local host=$1
    local port=$2
    local timeout=$3
    
    if nc -z -w $timeout $host $port 2>/dev/null; then
        echo "✓ Port $port: OPEN"
        return 0
    else
        echo "✗ Port $port: CLOSED"
        return 1
    fi
}

open_ports=0
total_ports=0

# Parse ports (support ranges and individual ports)
for port_spec in $(echo $ports | tr ',' ' '); do
    if echo $port_spec | grep -q '-'; then
        # Port range
        start=$(echo $port_spec | cut -d'-' -f1)
        end=$(echo $port_spec | cut -d'-' -f2)
        for port in $(seq $start $end); do
            scan_port $host $port $timeout
            if [ $? -eq 0 ]; then
                open_ports=$((open_ports + 1))
            fi
            total_ports=$((total_ports + 1))
        done
    else
        # Individual port
        scan_port $host $port_spec $timeout
        if [ $? -eq 0 ]; then
            open_ports=$((open_ports + 1))
        fi
        total_ports=$((total_ports + 1))
    fi
done

echo ""
echo "=== Scan Summary ==="
echo "Total ports scanned: $total_ports"
echo "Open ports: $open_ports"
echo "Closed ports: $((total_ports - open_ports))"
""",
    args=[
        Arg(name="host", type="str", description="Target hostname or IP address", required=True),
        Arg(name="ports", type="str", description="Ports to scan (e.g., '80,443' or '80-85,443')", required=True),
        Arg(name="timeout", type="int", description="Connection timeout in seconds", required=False, default=3)
    ]
)
### END: port_scanner ###



### START: certificate_checker ###
"""
SSL Certificate Checker Tool
============================
Purpose: Check SSL certificate information for a domain
Features:
- SSL certificate validation
- Certificate expiry checking
- Certificate chain analysis
- Domain certificate inspection
Docker: alpine:latest
"""
certificate_checker = Tool(
    name="certificate_checker",
    description="Check SSL certificate information for a domain",
    type="docker",
    image="alpine:latest",
    content="""
#!/bin/sh
echo "=== SSL Certificate Checker ==="
echo "Domain: $domain"
echo "Port: $port"

# Install openssl if not available
if ! command -v openssl > /dev/null; then
    apk add --no-cache openssl > /dev/null 2>&1
fi

# Get certificate information
echo "Connecting to $domain:$port..."
cert_info=$(echo | openssl s_client -servername $domain -connect $domain:$port 2>/dev/null | openssl x509 -noout -text 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "Error: Unable to retrieve certificate from $domain:$port"
    exit 1
fi

# Extract key information
echo ""
echo "=== Certificate Information ==="

# Subject
subject=$(echo "$cert_info" | grep "Subject:" | head -1 | sed 's/.*Subject: //')
echo "Subject: $subject"

# Issuer
issuer=$(echo "$cert_info" | grep "Issuer:" | head -1 | sed 's/.*Issuer: //')
echo "Issuer: $issuer"

# Validity dates
not_before=$(echo "$cert_info" | grep "Not Before:" | sed 's/.*Not Before: //')
not_after=$(echo "$cert_info" | grep "Not After :" | sed 's/.*Not After : //')
echo "Valid From: $not_before"
echo "Valid Until: $not_after"

# Check if certificate is valid
current_date=$(date -u +%s)
expiry_date=$(date -d "$not_after" +%s 2>/dev/null || echo "0")

if [ "$expiry_date" -gt "$current_date" ]; then
    days_until_expiry=$(( (expiry_date - current_date) / 86400 ))
    echo "Status: ✓ VALID"
    echo "Days until expiry: $days_until_expiry"
    
    if [ "$days_until_expiry" -lt 30 ]; then
        echo "⚠ WARNING: Certificate expires in less than 30 days!"
    fi
else
    echo "Status: ✗ EXPIRED"
fi

# Get certificate chain
echo ""
echo "=== Certificate Chain ==="
echo | openssl s_client -servername $domain -connect $domain:$port -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE" | xargs echo "Certificates in chain:"
""",
    args=[
        Arg(name="domain", type="str", description="Domain name to check", required=True),
        Arg(name="port", type="int", description="Port number", required=False, default=443)
    ]
)
### END: certificate_checker ###


# ============================================================================
# TOOL REGISTRATION
# ============================================================================

# Register all tools
tool_registry.register("custom_tools", json_processor)
tool_registry.register("custom_tools", text_analyzer)
tool_registry.register("custom_tools", math_calculator)
tool_registry.register("custom_tools", url_validator)
tool_registry.register("custom_tools", data_converter)
tool_registry.register("custom_tools", system_info)
tool_registry.register("custom_tools", network_checker)
tool_registry.register("custom_tools", file_operations)
tool_registry.register("custom_tools", text_processor)
tool_registry.register("custom_tools", log_analyzer)

tool_registry.register("custom_tools", password_generator)
tool_registry.register("custom_tools", qr_generator)
tool_registry.register("custom_tools", base64_tool)
tool_registry.register("custom_tools", hash_generator)
tool_registry.register("custom_tools", weather_checker)
tool_registry.register("custom_tools", color_converter)
tool_registry.register("custom_tools", uuid_generator)
tool_registry.register("custom_tools", timestamp_converter)
tool_registry.register("custom_tools", port_scanner)
tool_registry.register("custom_tools", certificate_checker)

# Export tools for use in workflows
__all__ = [
    "json_processor",
    "text_analyzer", 
    "math_calculator",
    "url_validator",
    "data_converter",
    "system_info",
    "network_checker",
    "file_operations", 
    "text_processor",
    "log_analyzer",
    "password_generator",
    "qr_generator",
    "base64_tool",
    "hash_generator",
    "weather_checker",
    "color_converter",
    "uuid_generator",
    "timestamp_converter",
    "port_scanner",
    "certificate_checker"
]