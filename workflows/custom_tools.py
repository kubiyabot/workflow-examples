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

# Tool 1: JSON Processor (Python image with shell script)
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

# Tool 2: Text Analyzer (Python image with shell script)
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

# Tool 3: Math Calculator (Python image with shell script)
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

# Tool 4: URL Validator (Alpine image with shell script)
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

# Tool 5: Data Converter (Debian image with shell script)
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

# Tool 6: System Info (Alpine image)
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

# Tool 7: Network Checker (Curl image)
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

# Tool 8: File Operations (BusyBox image)
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

# Tool 9: Text Processor (Debian image)
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

# Tool 10: Log Analyzer (Alpine image)
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
    "log_analyzer"
]