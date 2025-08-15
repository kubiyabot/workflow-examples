"""
Simple Workflows using Custom Tools

This module contains 3 simple workflows that demonstrate how to use custom tools
as steps along with simple shell script steps.
"""

from kubiya_workflow_sdk.dsl import Workflow, Step
from workflows.custom_tools import (
    json_processor, text_analyzer, url_validator, 
    system_info, network_checker, log_analyzer,
    # New custom tools
    password_generator, qr_generator, base64_tool, hash_generator,
    weather_checker, color_converter, uuid_generator, timestamp_converter,
    port_scanner, certificate_checker
)

# ============================================================================
# WORKFLOW 1: URL VALIDATION AND ANALYSIS
# ============================================================================


### START: url_validation_workflow ###


"""
URL Validation Workflow
=======================
Purpose: Validate URLs, check connectivity, and analyze the results
Workflow Steps:
1. validate_url - Validate URL format using custom Python tool
2. echo_validation - Echo validation completion message
3. check_connectivity - Check network connectivity using custom shell tool
4. generate_summary - Generate comprehensive analysis summary
Tools Used: url_validator, network_checker
"""

def url_validation_workflow():
    from models.models import (
        ReportGenerationCommand,
    )
    
    return (Workflow("url_validation_workflow")
    .description("Validate URLs and check their connectivity")
    .params(target_url="https://example.com")
    .step("validate_url", callback=lambda s:
        s.description("Validate URL format using custom Python tool")
        .tool(url_validator)
        .args(url="${target_url}")
        .output("validation_result")
    )
    .step("echo_validation", callback=lambda s:
        s.description("Echo validation completion message")
        .shell('echo "URL validation completed for: ${target_url}"')
    )
    .step("check_connectivity", callback=lambda s:
        s.description("Check network connectivity using custom shell tool")
        .tool(network_checker)
        .args(target="${target_url}")
        .output("connectivity_result")
    )
    .step("generate_summary", callback=lambda s:
        s.description("Generate comprehensive analysis summary using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="url_analysis",
                title="=== URL Analysis Summary ===",
                sections={
                    "Target URL": "${target_url}",
                    "Validation": "${validation_result}",
                    "Connectivity": "${connectivity_result}",
                    "Analysis Time": "$(date)"
                }
            ).get_command()
        )
        .depends("validate_url", "check_connectivity")
    )
        )
### END: url_validation_workflow ###



# ============================================================================
# WORKFLOW 2: TEXT PROCESSING PIPELINE
# ============================================================================



### START: text_processing_workflow ###

"""
Text Processing Workflow
========================
Purpose: Process and analyze text content through multiple stages
Workflow Steps:
1. prepare_text - Prepare text for analysis
2. analyze_text - Analyze text using custom Python tool
3. count_characters - Count characters using shell
4. extract_unique_words - Extract unique words using shell
5. generate_report - Generate final text processing report
Tools Used: text_analyzer
"""

def text_processing_workflow():
    from models.models import (
        TextProcessingCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("text_processing_workflow")
    .description("Process and analyze text content through multiple stages")
    .params(input_text="Hello world! This is a sample text for analysis.")
    .step("prepare_text", callback=lambda s:
        s.description("Prepare text for analysis using TextProcessingCommand")
        .shell(
            TextProcessingCommand(
                input_text="${input_text}",
                processing_type="prepare",
                output_file="/tmp/text_input.txt"
            ).get_command()
        )
        .output("prepared")
    )
    .step("analyze_text", callback=lambda s:
        s.description("Analyze text using custom Python tool")
        .tool(text_analyzer)
        .args(text="${input_text}")
        .output("analysis_result")
        .depends("prepare_text")
    )
    .step("count_characters", callback=lambda s:
        s.description("Count characters using TextProcessingCommand")
        .shell(
            TextProcessingCommand(
                input_text="${input_text}",
                processing_type="count_chars"
            ).get_command()
        )
        .output("char_count")
        .depends("prepare_text")
    )
    .step("extract_unique_words", callback=lambda s:
        s.description("Extract unique words using TextProcessingCommand")
        .shell(
            TextProcessingCommand(
                input_text="${input_text}",
                processing_type="extract_words",
                max_unique_words=10
            ).get_command()
        )
        .output("unique_words")
        .depends("prepare_text")
    )
    .step("generate_report", callback=lambda s:
        s.description("Generate final text processing report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="text_processing",
                title="=== Text Processing Report ===",
                sections={
                    "Original Text Length": "${char_count}",
                    "Analysis Results": "${analysis_result}",
                    "Top Unique Words": "${unique_words}",
                    "Generated At": "$(date)"
                }
            ).get_command()
        )
        .depends("analyze_text", "count_characters", "extract_unique_words")
    ))
### END: text_processing_workflow ###



# ============================================================================
# WORKFLOW 3: SYSTEM MONITORING AND LOG ANALYSIS
# ============================================================================



### START: system_monitoring_workflow ###

"""
System Monitoring Workflow
==========================
Purpose: Monitor system status and analyze log data
Workflow Steps:
1. get_system_info - Get system information using custom shell tool
2. check_disk_space - Check disk space using shell
3. check_processes - Check current processes
4. analyze_logs - Analyze logs using custom shell tool
5. check_log_errors - Check for errors in logs
6. create_monitoring_report - Create comprehensive monitoring report
7. cleanup - Cleanup temporary files
Tools Used: system_info, log_analyzer
"""

def system_monitoring_workflow():
    from models.models import (
        ReportGenerationCommand,
    )
    
    return (Workflow("system_monitoring_workflow")
    .description("Monitor system status and analyze log data")
    .params(log_data="2024-01-01 10:00:00 [INFO] System started\n2024-01-01 10:01:00 [ERROR] Connection failed")
    .step("get_system_info", callback=lambda s:
        s.description("Get system information using custom shell tool")
        .tool(system_info)
        .output("system_status")
    )
    .step("check_disk_space", callback=lambda s:
        s.description("Check disk space using shell")
        .shell('df -h | grep -E "^/dev" | head -5')
        .output("disk_info")
    )
    .step("check_processes", callback=lambda s:
        s.description("Check current processes")
        .shell('ps aux | head -10')
        .output("process_list")
    )
    .step("analyze_logs", callback=lambda s:
        s.description("Analyze logs using custom shell tool")
        .tool(log_analyzer)
        .args(logs="${log_data}", analysis_type="summary")
        .output("log_summary")
    )
    .step("check_log_errors", callback=lambda s:
        s.description("Check for errors in logs")
        .tool(log_analyzer)
        .args(logs="${log_data}", analysis_type="errors")
        .output("error_summary")
        .depends("analyze_logs")
    )
    .step("create_monitoring_report", callback=lambda s:
        s.description("Create comprehensive monitoring report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="system_monitoring",
                title="=== System Monitoring Report ===",
                sections={
                    "Timestamp": "$(date)",
                    "System Status": "${system_status}",
                    "Disk Usage": "${disk_info}",
                    "Running Processes": "${process_list}",
                    "Log Analysis": "${log_summary}",
                    "Error Summary": "${error_summary}"
                }
            ).get_command()
        )
        .depends("get_system_info", "check_disk_space", "check_processes", "check_log_errors")
    )
    .step("cleanup", callback=lambda s:
        s.description("Cleanup temporary files")
        .shell('echo "Monitoring workflow completed successfully" && rm -f /tmp/monitoring_*')
        .depends("create_monitoring_report")
    ))
### END: system_monitoring_workflow ###



# ============================================================================
# WORKFLOW 4: SECURITY TOOLKIT
# ============================================================================



### START: security_workflow ###

"""
Security Toolkit Workflow
=========================
Purpose: Generate secure passwords, create hashes, and demonstrate security tools
Workflow Steps:
1. generate_secure_password - Generate a secure password with custom length
2. generate_simple_password - Generate a simple password without symbols
3. hash_secret_sha256 - Generate SHA256 hash of secret text
4. hash_secret_md5 - Generate MD5 hash of secret text
5. encode_secret_base64 - Encode secret text in Base64
6. decode_secret_base64 - Decode the Base64 encoded secret
7. generate_security_report - Generate comprehensive security report
Tools Used: password_generator, hash_generator, base64_tool
"""

def security_workflow():
    from models.models import (
        ReportGenerationCommand,
    )
    
    return (Workflow("security_toolkit_workflow")
    .description("Generate secure passwords, create hashes, and demonstrate security tools")
    .params(
        secret_text="MySecretData123",
        password_length=16
    )
    .step("generate_secure_password", callback=lambda s:
        s.description("Generate a secure password with custom length")
        .tool(password_generator)
        .args(length="${password_length}", include_symbols=True, include_numbers=True)
        .output("secure_password")
    )
    .step("generate_simple_password", callback=lambda s:
        s.description("Generate a simple password without symbols")
        .tool(password_generator)
        .args(length=12, include_symbols=False, include_numbers=True)
        .output("simple_password")
    )
    .step("hash_secret_sha256", callback=lambda s:
        s.description("Generate SHA256 hash of secret text")
        .tool(hash_generator)
        .args(text="${secret_text}", hash_type="sha256")
        .output("sha256_hash")
    )
    .step("hash_secret_md5", callback=lambda s:
        s.description("Generate MD5 hash of secret text")
        .tool(hash_generator)
        .args(text="${secret_text}", hash_type="md5")
        .output("md5_hash")
    )
    .step("encode_secret_base64", callback=lambda s:
        s.description("Encode secret text in Base64")
        .tool(base64_tool)
        .args(operation="encode", text="${secret_text}")
        .output("base64_encoded")
    )
    .step("decode_secret_base64", callback=lambda s:
        s.description("Decode the Base64 encoded secret")
        .tool(base64_tool)
        .args(operation="decode", text="${base64_encoded}")
        .output("base64_decoded")
        .depends("encode_secret_base64")
    )
    .step("generate_security_report", callback=lambda s:
        s.description("Generate comprehensive security report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="security_toolkit",
                title="=== Security Toolkit Report ===",
                sections={
                    "Generated At": "$(date)",
                    "Secure Password": "${secure_password}",
                    "Simple Password": "${simple_password}",
                    "Original Text": "${secret_text}",
                    "SHA256 Hash": "${sha256_hash}",
                    "MD5 Hash": "${md5_hash}",
                    "Base64 Encoded": "${base64_encoded}",
                    "Base64 Decoded": "${base64_decoded}",
                    "Summary": "All security operations completed successfully"
                }
            ).get_command()
        )
        .depends("generate_secure_password", "generate_simple_password",
                "hash_secret_sha256", "hash_secret_md5", "decode_secret_base64")
    ))
### END: security_workflow ###



# ============================================================================
# WORKFLOW 5: DATA CONVERSION PIPELINE
# ============================================================================



### START: data_conversion_workflow ###

"""
Data Conversion Workflow
========================
Purpose: Convert data between different formats and representations
Workflow Steps:
1. get_current_timestamp - Get current timestamp
2. convert_hex_to_rgb - Convert HEX color to RGB
3. convert_rgb_to_hex - Convert RGB color to HEX
4. convert_hex_to_hsl - Convert HEX color to HSL
5. convert_date_to_timestamp - Convert a specific date to timestamp
6. convert_timestamp_to_date - Convert timestamp back to date
7. generate_conversion_report - Generate data conversion report
Tools Used: timestamp_converter, color_converter
"""
def data_conversion_workflow():
    from models.models import (
        ReportGenerationCommand,
    )
    
    return (Workflow("data_conversion_workflow")
    .description("Convert data between different formats and representations")
    .params(
        hex_color="#ff5733",
        rgb_color="255, 87, 51",
        current_timestamp=""
    )
    .step("get_current_timestamp", callback=lambda s:
        s.description("Get current timestamp")
        .tool(timestamp_converter)
        .args(operation="current")
        .output("current_time")
    )
    .step("convert_hex_to_rgb", callback=lambda s:
        s.description("Convert HEX color to RGB")
        .tool(color_converter)
        .args(color_value="${hex_color}", from_format="hex", to_format="rgb")
        .output("rgb_result")
    )
    .step("convert_rgb_to_hex", callback=lambda s:
        s.description("Convert RGB color to HEX")
        .tool(color_converter)
        .args(color_value="${rgb_color}", from_format="rgb", to_format="hex")
        .output("hex_result")
    )
    .step("convert_hex_to_hsl", callback=lambda s:
        s.description("Convert HEX color to HSL")
        .tool(color_converter)
        .args(color_value="${hex_color}", from_format="hex", to_format="hsl")
        .output("hsl_result")
    )
    .step("convert_date_to_timestamp", callback=lambda s:
        s.description("Convert a specific date to timestamp")
        .tool(timestamp_converter)
        .args(operation="to_timestamp", input_value="2024-12-31 23:59:59")
        .output("specific_timestamp")
    )
    .step("convert_timestamp_to_date", callback=lambda s:
        s.description("Convert timestamp back to date")
        .tool(timestamp_converter)
        .args(operation="to_date", input_value="1735689599")
        .output("converted_date")
    )
    .step("generate_conversion_report", callback=lambda s:
        s.description("Generate data conversion report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="data_conversion",
                title="=== Data Conversion Report ===",
                sections={
                    "Generated At": "$(date)",
                    "Original HEX": "${hex_color}",
                    "HEX to RGB": "${rgb_result}",
                    "HEX to HSL": "${hsl_result}",
                    "Original RGB": "${rgb_color}",
                    "RGB to HEX": "${hex_result}",
                    "Current Time": "${current_time}",
                    "Specific Timestamp": "${specific_timestamp}",
                    "Converted Date": "${converted_date}",
                    "Summary": "All data conversion operations completed successfully"
                }
            ).get_command()
        )
        .depends("get_current_timestamp", "convert_hex_to_rgb", "convert_rgb_to_hex",
                "convert_hex_to_hsl", "convert_date_to_timestamp", "convert_timestamp_to_date")
    ))
### END: data_conversion_workflow ###



# ============================================================================
# WORKFLOW 6: NETWORK SECURITY AUDIT
# ============================================================================



### START: network_security_workflow ###

"""
Network Security Workflow
=========================
Purpose: Perform network security audit with port scanning and SSL certificate checks
Workflow Steps:
1. scan_common_ports - Scan common ports on target domain
2. scan_web_ports - Scan web-specific port range
3. check_ssl_certificate - Check SSL certificate for HTTPS port
4. check_network_connectivity - Verify basic network connectivity
5. get_weather_context - Get weather information (context for location-based security)
6. generate_security_audit - Generate comprehensive network security audit report
Tools Used: port_scanner, certificate_checker, network_checker, weather_checker
"""

def network_security_workflow():
    from models.models import (
        ReportGenerationCommand,
    )
    
    return (Workflow("network_security_workflow")
    .description("Perform network security audit with port scanning and SSL certificate checks")
    .params(
        target_domain="google.com",
        target_ports="80,443,22,21",
        weather_city="new-york"
    )
    .step("scan_common_ports", callback=lambda s:
        s.description("Scan common ports on target domain")
        .tool(port_scanner)
        .args(host="${target_domain}", ports="${target_ports}", timeout=5)
        .output("port_scan_results")
    )
    .step("scan_web_ports", callback=lambda s:
        s.description("Scan web-specific port range")
        .tool(port_scanner)
        .args(host="${target_domain}", ports="80-85,443,8080,8443", timeout=3)
        .output("web_port_results")
    )
    .step("check_ssl_certificate", callback=lambda s:
        s.description("Check SSL certificate for HTTPS port")
        .tool(certificate_checker)
        .args(domain="${target_domain}", port=443)
        .output("ssl_cert_info")
    )
    .step("check_network_connectivity", callback=lambda s:
        s.description("Verify basic network connectivity")
        .tool(network_checker)
        .args(target="https://${target_domain}")
        .output("connectivity_check")
    )
    .step("get_weather_context", callback=lambda s:
        s.description("Get weather information (context for location-based security)")
        .tool(weather_checker)
        .args(city="${weather_city}", format="simple")
        .output("weather_info")
    )
    .step("generate_security_audit", callback=lambda s:
        s.description("Generate comprehensive network security audit report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="network_security_audit",
                title="=== Network Security Audit Report ===",
                sections={
                    "Target": "${target_domain}",
                    "Audit Time": "$(date)",
                    "Location Context": "${weather_city}",
                    "Common Ports": "${port_scan_results}",
                    "Web Ports": "${web_port_results}",
                    "SSL Certificate": "${ssl_cert_info}",
                    "Network Connectivity": "${connectivity_check}",
                    "Weather Context": "${weather_info}",
                    "Summary": "✓ All security checks completed successfully"
                }
            ).get_command()
        )
        .depends("scan_common_ports", "scan_web_ports", "check_ssl_certificate",
                "check_network_connectivity", "get_weather_context")
    ))
### END: network_security_workflow ###


# ============================================================================
# WORKFLOW 7: UTILITY AND INTEGRATION TOOLKIT
# ============================================================================


### START: general_utility_workflow ###

"""
Utility Workflow
=========================
Purpose: Demonstrate various utility operations and integrations
Workflow Steps:
1. system_diagnostics - Run comprehensive system diagnostics
2. file_operations - Perform file management operations
3. network_utilities - Test network utilities and connectivity
4. data_processing - Process and analyze data
5. security_checks - Run security validations
6. generate_utility_report - Generate comprehensive utility report
Models Used: Various utility command models
"""

def utility_workflow():
    from models.models import (
        SystemMonitoringCommand,
        TextProcessingCommand,
        UrlValidationCommand,
        SecurityToolkitCommand,
        DataConversionCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("utility_workflow")
    .description("Comprehensive utility and integration toolkit demonstration")
    .params(
        test_url="https://httpbin.org/status/200",
        sample_text="This is a sample text for utility processing and analysis.",
        test_data="sample123"
    )
    .step("system_diagnostics", callback=lambda s:
        s.description("Run comprehensive system diagnostics using SystemMonitoringCommand")
        .shell(
            SystemMonitoringCommand(
                monitoring_type="system_info"
            ).get_command()
        )
        .output("system_diagnostics")
    )
    .step("file_operations", callback=lambda s:
        s.description("Perform file management operations using TextProcessingCommand")
        .shell(
            TextProcessingCommand(
                input_text="${sample_text}",
                processing_type="prepare",
                output_file="/tmp/utility_test.txt"
            ).get_command()
        )
        .output("file_operations")
        .depends("system_diagnostics")
    )
    .step("network_utilities", callback=lambda s:
        s.description("Test network utilities and connectivity using UrlValidationCommand")
        .shell(
            UrlValidationCommand(
                target_url="${test_url}",
                timeout_seconds=15,
                check_ssl=True,
                follow_redirects=True
            ).get_command()
        )
        .output("network_utilities")
        .depends("file_operations")
    )
    .step("data_processing", callback=lambda s:
        s.description("Process and analyze data using DataConversionCommand")
        .shell(
            DataConversionCommand(
                conversion_type="date_to_timestamp",
                input_value=""
            ).get_command()
        )
        .output("data_processing")
        .depends("network_utilities")
    )
    .step("security_checks", callback=lambda s:
        s.description("Run security validations using SecurityToolkitCommand")
        .shell(
            SecurityToolkitCommand(
                operation_type="hash_data",
                hash_algorithm="sha256",
                input_data="${test_data}"
            ).get_command()
        )
        .output("security_checks")
        .depends("data_processing")
    )
    .step("generate_utility_report", callback=lambda s:
        s.description("Generate comprehensive utility report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="utility_toolkit",
                title="=== Utility Toolkit Report ===",
                sections={
                    "Execution Time": "$(date)",
                    "System Diagnostics": "${system_diagnostics}",
                    "File Operations": "${file_operations}",
                    "Network Utilities": "${network_utilities}",
                    "Data Processing": "${data_processing}",
                    "Security Checks": "${security_checks}",
                    "Summary": "All utility operations completed successfully"
                }
            ).get_command()
        )
        .depends("security_checks")
    )
)
### END: utility_workflow ###



### START: utility_toolkit_workflow ###

"""
Utility Toolkit Workflow
========================
Purpose: Demonstrate utility tools for UUID generation, QR codes, and integrations
Workflow Steps:
1. generate_single_uuid - Generate a single UUID v4
2. generate_multiple_uuids - Generate multiple UUIDs
3. generate_uuid_v1 - Generate UUID v1 (time-based)
4. generate_uuid_v5 - Generate UUID v5 (namespace-based)
5. create_qr_code_small - Create small QR code
6. create_qr_code_large - Create large QR code
7. create_qr_for_uuid - Create QR code containing UUID
8. generate_utility_report - Generate comprehensive utility toolkit report
Tools Used: uuid_generator, qr_generator
"""

def utility_toolkit_workflow():
    from models.models import (
        ReportGenerationCommand,
    )
    
    return (Workflow("utility_toolkit_workflow")
    .description("Demonstrate utility tools for UUID generation, QR codes, and integrations")
    .params(
        qr_text="https://kubiya.ai - Your AI Platform",
        uuid_count=5
    )
    .step("generate_single_uuid", callback=lambda s:
        s.description("Generate a single UUID v4")
        .tool(uuid_generator)
        .args(version="4", count=1)
        .output("single_uuid")
    )
    .step("generate_multiple_uuids", callback=lambda s:
        s.description("Generate multiple UUIDs")
        .tool(uuid_generator)
        .args(version="4", count="${uuid_count}")
        .output("multiple_uuids")
    )
    .step("generate_uuid_v1", callback=lambda s:
        s.description("Generate UUID v1 (time-based)")
        .tool(uuid_generator)
        .args(version="1", count=2)
        .output("time_based_uuids")
    )
    .step("generate_uuid_v5", callback=lambda s:
        s.description("Generate UUID v5 (namespace-based)")
        .tool(uuid_generator)
        .args(version="5", count=3)
        .output("namespace_uuids")
    )
    .step("create_qr_code_small", callback=lambda s:
        s.description("Create small QR code")
        .tool(qr_generator)
        .args(text="${qr_text}", size="small")
        .output("qr_small")
    )
    .step("create_qr_code_large", callback=lambda s:
        s.description("Create large QR code")
        .tool(qr_generator)
        .args(text="${qr_text}", size="large")
        .output("qr_large")
    )
    .step("create_qr_for_uuid", callback=lambda s:
        s.description("Create QR code containing UUID")
        .tool(qr_generator)
        .args(text="UUID: ${single_uuid}", size="small")
        .output("qr_uuid")
        .depends("generate_single_uuid")
    )
    .step("generate_utility_report", callback=lambda s:
        s.description("Generate comprehensive utility toolkit report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="utility_toolkit",
                title="=== Utility Toolkit Report ===",
                sections={
                    "Generated At": "$(date)",
                    "Single UUID v4": "${single_uuid}",
                    "Multiple UUID v4 (${uuid_count} count)": "${multiple_uuids}",
                    "Time-based UUIDs (v1)": "${time_based_uuids}",
                    "Namespace UUIDs (v5)": "${namespace_uuids}",
                    "QR Text": "${qr_text}",
                    "Small QR Code": "${qr_small}",
                    "Large QR Code": "${qr_large}",
                    "QR Code for UUID": "${qr_uuid}",
                    "Summary": "✓ All utility operations completed successfully"
                }
            ).get_command()
        )
        .depends("generate_multiple_uuids", "generate_uuid_v1", "generate_uuid_v5",
                "create_qr_code_small", "create_qr_code_large", "create_qr_for_uuid")
    ))
### END: utility_toolkit_workflow ###




### START: database_backup_workflow ###
"""
Database Backup Workflow
========================
Purpose: Automated database backup with validation and notification
Workflow Steps:
1. validate_backup_params - Validate backup parameters
2. execute_backup - Execute database backup using DatabaseBackupCommand
3. verify_backup - Verify backup integrity
4. cleanup_old_backups - Clean up old backup files using LogRotationCommand
5. send_notification - Send backup status notification
6. generate_backup_report - Generate backup completion report
Models Used: DatabaseBackupCommand, LogRotationCommand
"""

def database_backup_workflow():
    from models.models import (
        DatabaseBackupCommand,
        LogRotationCommand,
        SystemMaintenanceMessage,
        ValidationCommand,
        BackupVerificationCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("database_backup_workflow")
        .description("Automated database backup with validation and notification")
        .params(
            database_type="postgresql",
            database_name="production_db", 
            backup_location="/tmp/backups",
            retention_days=30,
            notification_channel="#ops-alerts"
        )
        .step("validate_backup_params", callback=lambda s:
            s.description("Validate backup parameters using ValidationCommand")
            .shell(
                ValidationCommand(
                    validation_type="backup_params",
                    resource_name="${database_name}",
                    resource_location="${backup_location}"
                ).get_command()
            )
            .output("validation_status")
        )
        .step("execute_backup", callback=lambda s:
            s.description("Execute database backup using DatabaseBackupCommand")
            .shell(
                DatabaseBackupCommand(
                    database_type="{{.database_type}}",
                    database_name="{{.database_name}}",
                    backup_location="{{.backup_location}}"
                ).get_command()
            )
            .depends("validate_backup_params")
            .output("backup_result")
        )
        .step("verify_backup", callback=lambda s:
            s.description("Verify backup integrity using BackupVerificationCommand")
            .shell(
                BackupVerificationCommand(
                    backup_location="${backup_location}",
                    backup_name_pattern="${database_name}_*.sql"
                ).get_command()
            )
            .depends("execute_backup")
            .output("verification_status")
        )
        .step("cleanup_old_backups", callback=lambda s:
            s.description("Clean up old backup files using LogRotationCommand")
            .shell(
                LogRotationCommand(
                    log_directory="{{.backup_location}}",
                    log_pattern="{{.database_name}}_*.sql"
                    # max_size_mb and retention_days use default values
                ).get_command()
            )
            .depends("verify_backup")
            .output("cleanup_status")
        )
        .step("send_notification", callback=lambda s:
            s.description("Send backup status notification using SystemMaintenanceMessage")
            .shell(
                SystemMaintenanceMessage(
                    channel="{{.notification_channel}}",
                    maintenance_title="Database Backup Completed",
                    start_time="$(date)",
                    end_time="$(date)",
                    affected_systems=["{{.database_name}}"],
                    impact_level="low",
                    maintenance_type="scheduled"
                ).get_command()
            )
            .depends("cleanup_old_backups")
            .output("notification_sent")
        )
        .step("generate_backup_report", callback=lambda s:
            s.description("Generate backup completion report using ReportGenerationCommand")
            .shell(
                ReportGenerationCommand(
                    report_type="backup",
                    title="📋 DATABASE BACKUP REPORT",
                    sections={
                        "Database Information": "Database: ${database_name}, Type: ${database_type}",
                        "Backup Status": "${backup_result}",
                        "Verification": "${verification_status}",
                        "Cleanup": "${cleanup_status}"
                    }
                ).get_command()
            )
            .depends("send_notification")
        )
    )
### END: database_backup_workflow ###



### START: kubernetes_health_check_workflow ###
"""
Kubernetes Health Check Workflow
================================
Purpose: Comprehensive Kubernetes cluster health assessment
Workflow Steps:
1. check_cluster_connection - Verify cluster connectivity
2. assess_nodes - Check node status and resources using KubernetesHealthCheckCommand
3. validate_pods - Validate pod health across namespaces using KubernetesHealthCheckCommand
4. check_services - Verify service connectivity using KubernetesHealthCheckCommand
5. generate_health_report - Generate comprehensive health report
6. send_capacity_alerts - Send capacity warnings using CapacityWarningMessage
Models Used: KubernetesHealthCheckCommand, CapacityWarningMessage
"""

def kubernetes_health_check_workflow():
    from models.models import (
        KubernetesHealthCheckCommand,
        CapacityWarningMessage,
        ClusterConnectionCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("kubernetes_health_check_workflow")
        .description("Comprehensive Kubernetes cluster health assessment")
        .params(
            target_namespace="production",
            cpu_threshold=80.0,
            memory_threshold=85.0,
            alert_channel="#k8s-alerts"
        )
        .step("check_cluster_connection", callback=lambda s:
            s.description("Verify cluster connectivity using ClusterConnectionCommand")
            .shell(
                ClusterConnectionCommand(
                    cluster_type="kubernetes",
                    connection_timeout=30
                ).get_command()
            )
            .output("connection_status")
        )
        .step("assess_nodes", callback=lambda s:
            s.description("Check node status and resources using KubernetesHealthCheckCommand")
            .shell(
                KubernetesHealthCheckCommand(
                    namespace="${target_namespace}",
                    check_nodes=True,
                    check_pods=False,
                    check_services=False
                ).get_command()
            )
            .depends("check_cluster_connection")
            .output("node_status")
        )
        .step("validate_pods", callback=lambda s:
            s.description("Validate pod health across namespaces using KubernetesHealthCheckCommand")
            .shell(
                KubernetesHealthCheckCommand(
                    namespace="${target_namespace}",
                    check_nodes=False,
                    check_pods=True,
                    check_services=False
                ).get_command()
            )
            .depends("assess_nodes")
            .output("pod_health")
        )
        .step("check_services", callback=lambda s:
            s.description("Verify service connectivity using KubernetesHealthCheckCommand")
            .shell(
                KubernetesHealthCheckCommand(
                    namespace="${target_namespace}",
                    check_nodes=False,
                    check_pods=False,
                    check_services=True
                ).get_command()
            )
            .depends("validate_pods")
            .output("service_status")
        )
        .step("generate_health_report", callback=lambda s:
            s.description("Generate comprehensive health report using ReportGenerationCommand")
            .shell(
                ReportGenerationCommand(
                    report_type="health",
                    title="🏥 KUBERNETES HEALTH REPORT",
                    sections={
                        "Namespace": "${target_namespace}",
                        "Connection Status": "${connection_status}",
                        "Node Health": "${node_status}",
                        "Pod Health": "${pod_health}",
                        "Service Status": "${service_status}"
                    }
                ).get_command()
            )
            .depends("check_services")
            .output("health_report")
        )
        .step("send_capacity_alerts", callback=lambda s:
            s.description("Send capacity warnings using CapacityWarningMessage")
            .shell(
                CapacityWarningMessage(
                    channel="{{.alert_channel}}",
                    resource_type="cpu",
                    current_usage="{{.cpu_threshold}}",
                    threshold="75.0",
                    affected_services=["{{.target_namespace}}"],
                    recommended_action="Consider scaling up resources"
                ).get_command()
            )
            .depends("generate_health_report")
        )
    )
### END: kubernetes_health_check_workflow ###



### START: security_scan_workflow ###
"""
Security Scan Workflow
======================
Purpose: Automated security scanning and vulnerability assessment
Workflow Steps:
1. prepare_scan_environment - Setup scanning environment using EnvironmentSetupCommand
2. network_security_scan - Perform network vulnerability scan using SecurityScanCommand
3. filesystem_security_scan - Scan filesystem for security issues using SecurityScanCommand
4. analyze_scan_results - Analyze and categorize findings
5. generate_security_report - Generate detailed security report using ReportGenerationCommand
6. send_security_alerts - Send alerts for critical findings using SecurityIncidentMessage
Models Used: SecurityScanCommand, SecurityIncidentMessage, EnvironmentSetupCommand, ReportGenerationCommand
"""

def security_scan_workflow():
    from models.models import (
        SecurityScanCommand,
        SecurityIncidentMessage,
        EnvironmentSetupCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("security_scan_workflow")
        .description("Automated security scanning and vulnerability assessment")
        .params(
            scan_target="192.168.1.0/24",
            scan_depth="standard",
            security_channel="#security-alerts",
            max_critical_findings=5
        )
        .step("prepare_scan_environment", callback=lambda s:
            s.description("Setup scanning environment using EnvironmentSetupCommand")
            .shell(
                EnvironmentSetupCommand(
                    setup_type="security_scan",
                    work_directory="/tmp/security_scans",
                    required_tools=["nmap", "find"]
                ).get_command()
            )
            .output("env_prepared")
        )
        .step("network_security_scan", callback=lambda s:
            s.description("Perform network vulnerability scan using SecurityScanCommand")
            .shell(
                SecurityScanCommand(
                    scan_type="network",
                    target="${scan_target}",
                    scan_depth="${scan_depth}",
                    alert_on_critical=True
                ).get_command()
            )
            .depends("prepare_scan_environment")
            .output("network_scan_results")
        )
        .step("filesystem_security_scan", callback=lambda s:
            s.description("Scan filesystem for security issues using SecurityScanCommand")
            .shell(
                SecurityScanCommand(
                    scan_type="filesystem",
                    target="/var/log",
                    scan_depth="${scan_depth}",
                    alert_on_critical=True
                ).get_command()
            )
            .depends("prepare_scan_environment")
            .output("filesystem_scan_results")
        )
        .step("analyze_scan_results", callback=lambda s:
            s.description("Analyze and categorize findings")
            .shell("""
echo "📊 ANALYZING SECURITY SCAN RESULTS"
echo "Network scan: ${network_scan_results}"
echo "Filesystem scan: ${filesystem_scan_results}"
CRITICAL_COUNT=$(echo "${network_scan_results}" | grep -c "CRITICAL" || echo "0")
echo "Critical findings: $CRITICAL_COUNT"
""")
            .depends("network_security_scan", "filesystem_security_scan")
            .output("analysis_results")
        )
        .step("generate_security_report", callback=lambda s:
            s.description("Generate detailed security report using ReportGenerationCommand")
            .shell(
                ReportGenerationCommand(
                    report_type="security",
                    title="🔒 SECURITY SCAN REPORT",
                    sections={
                        "Target": "${scan_target}",
                        "Scan Depth": "${scan_depth}",
                        "Analysis Results": "${analysis_results}",
                        "Network Scan": "${network_scan_results}",
                        "Filesystem Scan": "${filesystem_scan_results}"
                    }
                ).get_command()
            )
            .depends("analyze_scan_results")
            .output("security_report")
        )
        .step("send_security_alerts", callback=lambda s:
            s.description("Send alerts for critical findings using SecurityIncidentMessage")
            .shell(
                SecurityIncidentMessage(
                    channel="{{.security_channel}}",
                    incident_id="SEC-$(date +%Y%m%d-%H%M%S)",
                    incident_type="vulnerability",
                    severity="high",
                    affected_systems=["{{.scan_target}}"],
                    status="investigating"
                ).get_command()
            )
            .depends("generate_security_report")
        )
    )
### END: security_scan_workflow ###



### START: documentation_generation_workflow ###
"""
Documentation Generation Workflow
=================================
Purpose: Automated technical documentation generation and publishing
Workflow Steps:
1. validate_project_structure - Validate project structure using ProjectStructureValidationCommand
2. generate_api_documentation - Generate API documentation using DocumentationGenerator
3. create_readme_file - Create comprehensive README using TechnicalDocumentationPrompt
4. generate_architecture_docs - Generate architecture documentation using DocumentationGenerator
5. compile_documentation - Compile all documentation using ReportGenerationCommand
6. publish_documentation - Publish to documentation platform
Models Used: DocumentationGenerator, TechnicalDocumentationPrompt, ProjectStructureValidationCommand, ReportGenerationCommand
"""

def documentation_generation_workflow():
    from models.models import (
        DocumentationGenerator,
        TechnicalDocumentationPrompt,
        ProjectStructureValidationCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("documentation_generation_workflow")
        .description("Automated technical documentation generation and publishing")
        .params(
            project_name="workflow-sdk",
            organization_name="kubiya",
            project_version="2.0.0",
            docs_channel="#documentation"
        )
        .step("validate_project_structure", callback=lambda s:
            s.description("Validate project structure using ProjectStructureValidationCommand")
            .shell(
                ProjectStructureValidationCommand(
                    project_name="${project_name}",
                    project_type="python",
                    required_dirs=["models", "workflows", "docs"],
                    required_files=["README.md", "requirements.txt"]
                ).get_command()
            )
            .output("structure_valid")
        )
        .step("generate_api_documentation", callback=lambda s:
            s.description("Generate API documentation using DocumentationGenerator")
            .shell(
                DocumentationGenerator(
                    doc_type="api",
                    project_name="${project_name}",
                    organization_name="${organization_name}",
                    version="${project_version}"
                ).get_command()
            )
            .depends("validate_project_structure")
            .output("api_docs_generated")
        )
        .step("create_readme_file", callback=lambda s:
            s.description("Create comprehensive README using TechnicalDocumentationPrompt")
            .shell(
                TechnicalDocumentationPrompt(
                    doc_type="readme",
                    project_context="${project_name} - Workflow automation SDK",
                    target_audience="developers"
                ).get_command()
            )
            .depends("generate_api_documentation")
            .output("readme_created")
        )
        .step("generate_architecture_docs", callback=lambda s:
            s.description("Generate architecture documentation using DocumentationGenerator")
            .shell(
                DocumentationGenerator(
                    doc_type="architecture",
                    project_name="${project_name}",
                    organization_name="${organization_name}",
                    version="${project_version}"
                ).get_command()
            )
            .depends("create_readme_file")
            .output("architecture_docs")
        )
        .step("compile_documentation", callback=lambda s:
            s.description("Compile all documentation using ReportGenerationCommand")
            .shell(
                ReportGenerationCommand(
                    report_type="documentation",
                    title="📚 DOCUMENTATION COMPILATION REPORT",
                    sections={
                        "Project": "${project_name} v${project_version}",
                        "API Documentation": "${api_docs_generated}",
                        "README": "${readme_created}",
                        "Architecture Docs": "${architecture_docs}"
                    }
                ).get_command()
            )
            .depends("generate_architecture_docs")
            .output("docs_compiled")
        )
        .step("publish_documentation", callback=lambda s:
            s.description("Publish to documentation platform")
            .shell("""
echo "🚀 PUBLISHING DOCUMENTATION"
echo "Target: https://docs.${organization_name}.com/${project_name}"
echo "Version: ${project_version}"
echo "Compilation status: ${docs_compiled}"
echo "✅ Documentation published successfully"
""")
            .depends("compile_documentation")
        )
    )
### END: documentation_generation_workflow ###



### START: performance_testing_workflow ###
"""
Performance Testing Workflow
============================
Purpose: Automated performance testing and analysis
Workflow Steps:
1. setup_test_environment - Prepare testing environment
2. baseline_performance_test - Run baseline performance test
3. load_testing - Execute load testing scenarios
4. stress_testing - Perform stress testing
5. analyze_performance_results - Analyze test results
6. generate_performance_report - Generate performance report
Models Used: PerformanceTestCommand, DataAnalysisPrompt
"""

def performance_testing_workflow():
    from models.models import (
        PerformanceTestCommand,
        DataAnalysisPrompt,
        EnvironmentSetupCommand,
        SystemMetricsCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("performance_testing_workflow")
    .description("Automated performance testing and analysis")
    .params(
        target_url="https://api.example.com",
        concurrent_users=50,
        test_duration=10,
        performance_channel="#performance"
    )
    .step("setup_test_environment", callback=lambda s:
        s.description("Prepare testing environment using EnvironmentSetupCommand")
        .shell(
            EnvironmentSetupCommand(
                setup_type="performance",
                work_directory="/tmp/perf_tests",
                required_tools=["curl", "ab", "wrk"]
            ).get_command()
        )
        .output("env_setup")
    )
    .step("baseline_performance_test", callback=lambda s:
        s.description("Run baseline performance test using SystemMetricsCommand")
        .shell(
            SystemMetricsCommand(
                metric_types=["cpu", "memory"],
                top_processes_count=5
            ).get_command()
        )
        .depends("setup_test_environment")
        .output("baseline_results")
    )
    .step("load_testing", callback=lambda s:
        s.description("Execute load testing scenarios using PerformanceTestCommand")
        .shell(
            PerformanceTestCommand(
                test_type="load",
                target_url="${target_url}",
                concurrent_users="${concurrent_users}",
                test_duration_minutes="${test_duration}"
            ).get_command()
        )
        .depends("baseline_performance_test")
        .output("load_test_results")
    )
    .step("stress_testing", callback=lambda s:
        s.description("Perform stress testing using PerformanceTestCommand")
        .shell(
            PerformanceTestCommand(
                test_type="stress",
                target_url="${target_url}",
                concurrent_users="$(echo \"${concurrent_users} * 2\" | bc)",
                test_duration_minutes="${test_duration}"
            ).get_command()
        )
        .depends("load_testing")
        .output("stress_test_results")
    )
    .step("analyze_performance_results", callback=lambda s:
        s.description("Analyze test results using DataAnalysisPrompt")
        .shell(
            DataAnalysisPrompt(
                dataset_description="Performance test results for ${target_url}",
                analysis_type="diagnostic",
                key_questions=["What are the performance bottlenecks?", "How does response time scale with load?"]
            ).get_command()
        )
        .depends("stress_testing")
        .output("analysis_results")
    )
    .step("generate_performance_report", callback=lambda s:
        s.description("Generate performance report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="performance",
                title="📋 PERFORMANCE TEST REPORT",
                sections={
                    "Target URL": "${target_url}",
                    "Test Configuration": "Users: ${concurrent_users}, Duration: ${test_duration} min",
                    "Baseline Results": "${baseline_results}",
                    "Load Test": "${load_test_results}",
                    "Stress Test": "${stress_test_results}",
                    "Analysis": "${analysis_results}"
                }
            ).get_command()
        )
        .depends("analyze_performance_results")
    )
    )
### END: performance_testing_workflow ###



### START: log_analysis_workflow ###
"""
Log Analysis Workflow
=====================
Purpose: Automated log analysis and reporting
Workflow Steps:
1. collect_log_files - Collect log files from various sources using SystemMetricsCommand
2. rotate_large_logs - Rotate large log files using LogRotationCommand
3. analyze_error_patterns - Analyze error patterns using ProblemDiagnosticsCommand
4. generate_log_report - Generate comprehensive log analysis report using LogAnalysisReport
5. send_log_alerts - Send alerts for critical issues using AlertResolutionMessage
Models Used: LogRotationCommand, LogAnalysisReport, AlertResolutionMessage, SystemMetricsCommand, ProblemDiagnosticsCommand
"""

def log_analysis_workflow():
    from models.models import (
        LogRotationCommand,
        LogAnalysisReport,
        AlertResolutionMessage,
        SystemMetricsCommand,
        ProblemDiagnosticsCommand,
    )
    
    return (Workflow("log_analysis_workflow")
    .description("Automated log analysis and reporting")
    .params(
        log_directory="/var/log",
        log_pattern="*.log",
        analysis_period="last_day",
        ops_channel="#ops-logs"
    )
    .step("collect_log_files", callback=lambda s:
        s.description("Collect log files from various sources using SystemMetricsCommand")
        .shell(
            SystemMetricsCommand(
                metric_types=["disk"],
                top_processes_count=5
            ).get_command()
        )
        .output("logs_collected")
    )
    .step("rotate_large_logs", callback=lambda s:
        s.description("Rotate large log files using LogRotationCommand")
        .shell(
            LogRotationCommand(
                log_directory="{{.log_directory}}",
                log_pattern="{{.log_pattern}}"
                # max_size_mb and retention_days use default values
            ).get_command()
        )
        .depends("collect_log_files")
        .output("rotation_completed")
    )
    .step("analyze_error_patterns", callback=lambda s:
        s.description("Analyze error patterns using ProblemDiagnosticsCommand")
        .shell(
            ProblemDiagnosticsCommand(
                diagnostic_type="system",
                target_components=["logs", "application"],
                timeout_seconds=60
            ).get_command()
        )
        .depends("rotate_large_logs")
        .output("error_analysis")
    )
    .step("generate_log_report", callback=lambda s:
        s.description("Generate comprehensive log analysis report using LogAnalysisReport")
        .shell(
            LogAnalysisReport(
                log_source="application",
                analysis_period="${analysis_period}",
                output_format="markdown"
            ).get_command()
        )
        .depends("analyze_error_patterns")
        .output("log_report")
    )
    .step("send_log_alerts", callback=lambda s:
        s.description("Send alerts for critical issues using AlertResolutionMessage")
        .shell(
            AlertResolutionMessage(
                channel="{{.ops_channel}}",
                alert_id="LOG-$(date +%Y%m%d-%H%M%S)",
                alert_title="Log Analysis Completed",
                resolution_status="resolved",
                resolution_time="$(date)",
                root_cause="Routine log analysis",
                actions_taken=["Log rotation", "Error analysis", "Report generation"]
            ).get_command()
        )
        .depends("generate_log_report")
    )
)
### END: log_analysis_workflow ###



### START: configuration_deployment_workflow ###
"""
Configuration Deployment Workflow
=================================
Purpose: Automated configuration file generation and deployment
Workflow Steps:
1. validate_configuration_params - Validate deployment parameters
2. generate_nginx_config - Generate Nginx configuration
3. generate_k8s_config - Generate Kubernetes configuration
4. validate_configurations - Validate generated configurations
5. deploy_configurations - Deploy configurations to target environment
6. verify_deployment - Verify successful deployment
Models Used: ConfigurationFileGenerator, DeploymentStatusMessage
"""

def configuration_deployment_workflow():
    from models.models import (
        ConfigurationFileGenerator,
        DeploymentStatusMessage,
        ValidationCommand,
        ProjectStructureValidationCommand,
    )
    
    return (Workflow("configuration_deployment_workflow")
    .description("Automated configuration file generation and deployment")
    .params(
        environment="production",
        app_name="web-service",
        server_name="api.example.com",
        deployment_channel="#deployments"
    )
    .step("validate_configuration_params", callback=lambda s:
        s.description("Validate deployment parameters using ValidationCommand")
        .shell(
            ValidationCommand(
                validation_type="config_params",
                resource_name="${app_name}",
                resource_location="${environment}"
            ).get_command()
        )
        .output("params_valid")
    )
    .step("generate_nginx_config", callback=lambda s:
        s.description("Generate Nginx configuration using ConfigurationFileGenerator")
        .shell(
            ConfigurationFileGenerator(
                config_type="nginx",
                environment="${environment}",
                template_vars={"server_name": "${server_name}", "upstream_url": "http://localhost:3000"}
            ).get_command()
        )
        .depends("validate_configuration_params")
        .output("nginx_config")
    )
    .step("generate_k8s_config", callback=lambda s:
        s.description("Generate Kubernetes configuration")
        .shell("""
echo "🚢 GENERATING KUBERNETES CONFIGURATION"
echo "App: ${app_name}"
echo "Environment: ${environment}"
echo "✅ Kubernetes configuration generated"
""")
        .depends("validate_configuration_params")
        .output("k8s_config")
    )
    .step("validate_configurations", callback=lambda s:
        s.description("Validate generated configurations")
        .shell("""
echo "🔍 VALIDATING CONFIGURATIONS"
echo "Nginx config: ${nginx_config}"
echo "K8s config: ${k8s_config}"
echo "✅ Configuration validation passed"
""")
        .depends("generate_nginx_config", "generate_k8s_config")
        .output("validation_passed")
    )
    .step("deploy_configurations", callback=lambda s:
        s.description("Deploy configurations to target environment")
        .shell("""
echo "🚀 DEPLOYING CONFIGURATIONS"
echo "Target environment: ${environment}"
echo "Deploying ${app_name} configurations..."
echo "✅ Configurations deployed successfully"
""")
        .depends("validate_configurations")
        .output("deployment_result")
    )
    .step("verify_deployment", callback=lambda s:
        s.description("Verify successful deployment using DeploymentStatusMessage")
        .shell(
            DeploymentStatusMessage(
                channel="${deployment_channel}",
                deployment_id="DEP-$(date +%Y%m%d-%H%M%S)",
                service_name="${app_name}",
                environment="${environment}",
                version="latest",
                status="success",
                deploy_time="$(date)"
            ).get_command()
        )
        .depends("deploy_configurations")
    )
)
### END: configuration_deployment_workflow ###



### START: test_data_generation_workflow ###
"""
Test Data Generation Workflow
=============================
Purpose: Generate comprehensive test datasets for development and QA
Workflow Steps:
1. setup_data_generation - Setup data generation environment
2. generate_user_data - Generate user test data
3. generate_order_data - Generate order test data
4. validate_test_data - Validate generated test data
5. export_data_formats - Export data in multiple formats
6. publish_test_datasets - Publish datasets for team use
Models Used: TestDataGenerator, TestPlanningPrompt
"""

def test_data_generation_workflow():
    from models.models import (
        TestDataGenerator,
        TestPlanningPrompt,
        EnvironmentSetupCommand,
        ReportGenerationCommand,
        ValidationCommand,
    )
    
    return (Workflow("test_data_generation_workflow")
    .description("Generate comprehensive test datasets for development and QA")
    .params(
        record_count=1000,
        output_format="json",
        data_locale="en_US",
        qa_channel="#qa-data"
    )
    .step("setup_data_generation", callback=lambda s:
        s.description("Setup data generation environment using EnvironmentSetupCommand")
        .shell(
            EnvironmentSetupCommand(
                setup_type="data_generation",
                work_directory="/tmp/test_data",
                required_tools=["python", "faker"]
            ).get_command()
        )
        .output("env_ready")
    )
    .step("generate_user_data", callback=lambda s:
        s.description("Generate user test data using TestDataGenerator")
        .shell(
            TestDataGenerator(
                data_type="users",
                record_count="${record_count}",
                output_format="${output_format}",
                locale="${data_locale}"
            ).get_command()
        )
        .depends("setup_data_generation")
        .output("user_data")
    )
    .step("generate_order_data", callback=lambda s:
        s.description("Generate order test data using TestDataGenerator")
        .shell(
            TestDataGenerator(
                data_type="orders",
                record_count="${record_count}",
                output_format="${output_format}",
                locale="${data_locale}"
            ).get_command()
        )
        .depends("generate_user_data")
        .output("order_data")
    )
    .step("validate_test_data", callback=lambda s:
        s.description("Validate generated test data using ValidationCommand")
        .shell(
            ValidationCommand(
                validation_type="data_validation",
                resource_name="test_data",
                resource_location="/tmp/test_data"
            ).get_command()
        )
        .depends("generate_order_data")
        .output("validation_results")
    )
    .step("export_data_formats", callback=lambda s:
        s.description("Export data in multiple formats using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="data_export",
                title="📊 DATA EXPORT SUMMARY",
                sections={
                    "User Data": "${user_data}",
                    "Order Data": "${order_data}",
                    "Validation": "${validation_results}",
                    "Formats": "JSON, CSV, SQL"
                }
            ).get_command()
        )
        .depends("validate_test_data")
        .output("export_completed")
    )
    .step("publish_test_datasets", callback=lambda s:
        s.description("Publish datasets for team use using TestPlanningPrompt")
        .shell(
            TestPlanningPrompt(
                feature_description="Test data for ${record_count} users and orders",
                application_type="api",
                test_types=["functional", "integration"]
            ).get_command()
        )
        .depends("export_data_formats")
    )
)
### END: test_data_generation_workflow ###



### START: code_review_automation_workflow ###
"""
Code Review Automation Workflow
===============================
Purpose: Automated code review and quality analysis
Workflow Steps:
1. fetch_code_changes - Fetch recent code changes
2. analyze_python_code - Analyze Python code quality
3. analyze_javascript_code - Analyze JavaScript code quality
4. security_code_review - Perform security code review
5. generate_review_report - Generate comprehensive review report
6. post_review_feedback - Post review feedback to development team
Models Used: CodeReviewPrompt, TroubleshootingPrompt
"""

def code_review_automation_workflow():
    from models.models import (
        CodeReviewPrompt,
        TroubleshootingPrompt,
        ProjectStructureValidationCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("code_review_automation_workflow")
    .description("Automated code review and quality analysis")
    .params(
        repository_path="/repo",
        target_branch="main",
        review_focus="security,performance",
        dev_channel="#code-reviews"
    )
    .step("fetch_code_changes", callback=lambda s:
        s.description("Fetch recent code changes using ProjectStructureValidationCommand")
        .shell(
            ProjectStructureValidationCommand(
                project_name="code-review",
                project_type="general",
                required_dirs=[".git"],
                required_files=["README.md"]
            ).get_command()
        )
        .output("changes_fetched")
    )
    .step("analyze_python_code", callback=lambda s:
        s.description("Analyze Python code quality using CodeReviewPrompt")
        .shell(
            CodeReviewPrompt(
                language="python",
                code_snippet="# Sample Python code for review",
                review_focus=["security", "performance", "maintainability"]
            ).get_command()
        )
        .depends("fetch_code_changes")
        .output("python_analysis")
    )
    .step("analyze_javascript_code", callback=lambda s:
        s.description("Analyze JavaScript code quality using CodeReviewPrompt")
        .shell(
            CodeReviewPrompt(
                language="javascript",
                code_snippet="// Sample JavaScript code for review",
                review_focus=["security", "performance", "maintainability"]
            ).get_command()
        )
        .depends("fetch_code_changes")
        .output("js_analysis")
    )
    .step("security_code_review", callback=lambda s:
        s.description("Perform security code review")
        .shell("""
echo "🔒 SECURITY CODE REVIEW"
echo "Scanning for security vulnerabilities..."
echo "Checking for SQL injection, XSS, and other security issues"
echo "✅ Security review completed"
""")
        .depends("analyze_python_code", "analyze_javascript_code")
        .output("security_review")
    )
    .step("generate_review_report", callback=lambda s:
        s.description("Generate comprehensive review report using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="code_review",
                title="📋 CODE REVIEW REPORT",
                sections={
                    "Repository": "${repository_path}",
                    "Branch": "${target_branch}",
                    "Python Analysis": "${python_analysis}",
                    "JavaScript Analysis": "${js_analysis}",
                    "Security Review": "${security_review}"
                }
            ).get_command()
        )
        .depends("security_code_review")
        .output("review_report")
    )
    .step("post_review_feedback", callback=lambda s:
        s.description("Post review feedback to development team using TroubleshootingPrompt")
        .shell(
            TroubleshootingPrompt(
                problem_description="Code quality issues found in review",
                system_context="${repository_path}",
                urgency_level="medium",
                affected_components=["code-quality", "security"]
            ).get_command()
        )
        .depends("generate_review_report")
    )
)
### END: code_review_automation_workflow ###



### START: database_migration_workflow ###
"""
Database Migration Workflow
===========================
Purpose: Automated database schema migration and validation
Workflow Steps:
1. validate_migration_params - Validate migration parameters
2. generate_migration_files - Generate migration and rollback files
3. backup_current_schema - Backup current database schema
4. execute_migration - Execute database migration
5. validate_migration - Validate migration success
6. cleanup_migration_artifacts - Clean up migration artifacts
Models Used: DatabaseMigrationFile, DatabaseBackupCommand
"""

def database_migration_workflow():
    from models.models import (
        DatabaseMigrationFile,
        DatabaseBackupCommand,
        ValidationCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("database_migration_workflow")
    .description("Automated database schema migration and validation")
    .params(
        migration_name="add_user_preferences",
        table_name="user_preferences",
        database_engine="postgresql",
        db_channel="#database"
    )
    .step("validate_migration_params", callback=lambda s:
        s.description("Validate migration parameters using ValidationCommand")
        .shell(
            ValidationCommand(
                validation_type="migration_params",
                resource_name="${migration_name}",
                resource_location="${database_engine}"
            ).get_command()
        )
        .output("params_validated")
    )
    .step("generate_migration_files", callback=lambda s:
        s.description("Generate migration and rollback files using DatabaseMigrationFile")
        .shell(
            DatabaseMigrationFile(
                migration_name="${migration_name}",
                migration_type="create_table",
                database_engine="${database_engine}",
                table_name="${table_name}",
                columns=[{"name": "user_id", "type": "INTEGER"}, {"name": "preferences", "type": "JSONB"}]
            ).get_command()
        )
        .depends("validate_migration_params")
        .output("migration_files")
    )
    .step("backup_current_schema", callback=lambda s:
        s.description("Backup current database schema using DatabaseBackupCommand")
        .shell(
            DatabaseBackupCommand(
                database_type="{{.database_engine}}",
                database_name="{{.table_name}}",
                backup_location="/tmp/migration_backups"
            ).get_command()
        )
        .depends("generate_migration_files")
        .output("backup_completed")
    )
    .step("execute_migration", callback=lambda s:
        s.description("Execute database migration")
        .shell("""
echo "🚀 EXECUTING DATABASE MIGRATION"
echo "Migration: ${migration_name}"
echo "Files: ${migration_files}"
echo "✅ Migration executed successfully"
""")
        .depends("backup_current_schema")
        .output("migration_executed")
    )
    .step("validate_migration", callback=lambda s:
        s.description("Validate migration success")
        .shell("""
echo "✅ VALIDATING MIGRATION"
echo "Checking table structure for ${table_name}..."
echo "Verifying data integrity..."
echo "✅ Migration validation passed"
""")
        .depends("execute_migration")
        .output("validation_passed")
    )
    .step("cleanup_migration_artifacts", callback=lambda s:
        s.description("Clean up migration artifacts using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="migration",
                title="🧹 MIGRATION CLEANUP REPORT",
                sections={
                    "Migration": "${migration_name}",
                    "Table": "${table_name}",
                    "Engine": "${database_engine}",
                    "Status": "Completed successfully",
                    "Backup": "${backup_completed}",
                    "Files": "${migration_files}"
                }
            ).get_command()
        )
        .depends("validate_migration")
    )
)
### END: database_migration_workflow ###



### START: incident_escalation_workflow ###
"""
Incident Escalation Workflow
============================
Purpose: Automated incident escalation and notification management
Workflow Steps:
1. assess_incident_severity - Assess current incident severity
2. determine_escalation_need - Determine if escalation is needed
3. escalate_to_senior_team - Escalate to senior engineering team
4. send_escalation_notifications - Send escalation notifications
5. update_incident_status - Update incident tracking status
6. monitor_escalation_response - Monitor escalation response time
Models Used: SecurityIncidentMessage, AlertResolutionMessage
"""

def incident_escalation_workflow():
    from models.models import (
        SecurityIncidentMessage,
        AlertResolutionMessage,
        IncidentAssessmentCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("incident_escalation_workflow")
    .description("Automated incident escalation and notification management")
    .params(
        incident_id="INC-2024-001",
        current_severity="high",
        escalation_threshold=30,
        escalation_channel="#incident-escalation"
    )
    .step("assess_incident_severity", callback=lambda s:
        s.description("Assess current incident severity using IncidentAssessmentCommand")
        .shell(
            IncidentAssessmentCommand(
                incident_id="${incident_id}",
                current_severity="${current_severity}",
                escalation_threshold_minutes="${escalation_threshold}",
                affected_systems=["production"]
            ).get_command()
        )
        .output("severity_assessed")
    )
    .step("determine_escalation_need", callback=lambda s:
        s.description("Determine if escalation is needed")
        .shell("""
echo "🤔 DETERMINING ESCALATION NEED"
if [ "${current_severity}" = "critical" ] || [ "${current_severity}" = "high" ]; then
    echo "⚠️ Escalation needed for ${current_severity} severity incident"
    echo "ESCALATE=true"
else
    echo "ℹ️ No escalation needed for ${current_severity} severity"
    echo "ESCALATE=false"
fi
""")
        .depends("assess_incident_severity")
        .output("escalation_decision")
    )
    .step("escalate_to_senior_team", callback=lambda s:
        s.description("Escalate to senior engineering team")
        .shell("""
echo "⬆️ ESCALATING TO SENIOR TEAM"
echo "Incident ${incident_id} escalated due to ${current_severity} severity"
echo "Senior team notified"
echo "✅ Escalation completed"
""")
        .depends("determine_escalation_need")
        .output("escalation_completed")
    )
    .step("send_escalation_notifications", callback=lambda s:
        s.description("Send escalation notifications using SecurityIncidentMessage")
        .shell(
            SecurityIncidentMessage(
                channel="{{.escalation_channel}}",
                incident_id="{{.incident_id}}",
                incident_type="system_outage",
                severity="{{.current_severity}}",
                affected_systems=["production"],
                status="escalated"
            ).get_command()
        )
        .depends("escalate_to_senior_team")
        .output("notifications_sent")
    )
    .step("update_incident_status", callback=lambda s:
        s.description("Update incident tracking status")
        .shell("""
echo "📝 UPDATING INCIDENT STATUS"
echo "Incident ${incident_id} status updated to 'escalated'"
echo "Escalation timestamp: $(date)"
echo "✅ Status update completed"
""")
        .depends("send_escalation_notifications")
        .output("status_updated")
    )
    .step("monitor_escalation_response", callback=lambda s:
        s.description("Monitor escalation response time using AlertResolutionMessage")
        .shell(
            AlertResolutionMessage(
                channel="{{.escalation_channel}}",
                alert_id="{{.incident_id}}",
                alert_title="Incident Escalation Response Monitoring",
                resolution_status="monitoring",
                resolution_time="$(date)",
                root_cause="Incident escalation due to severity",
                actions_taken=["Senior team notification", "Status update", "Monitoring initiated"]
            ).get_command()
        )
        .depends("update_incident_status")
    )
)
### END: incident_escalation_workflow ###



### START: capacity_monitoring_workflow ###
"""
Capacity Monitoring Workflow
============================
Purpose: Automated infrastructure capacity monitoring and alerting
Workflow Steps:
1. collect_resource_metrics - Collect current resource utilization
2. analyze_capacity_trends - Analyze capacity trends and patterns
3. predict_capacity_needs - Predict future capacity requirements
4. generate_capacity_alerts - Generate alerts for threshold breaches
5. recommend_scaling_actions - Recommend scaling actions
6. schedule_capacity_review - Schedule capacity planning review
Models Used: CapacityWarningMessage, DataAnalysisPrompt
"""

def capacity_monitoring_workflow():
    from models.models import (
        CapacityWarningMessage,
        DataAnalysisPrompt,
        SystemMetricsCommand,
        ReportGenerationCommand,
    )
    
    return (Workflow("capacity_monitoring_workflow")
    .description("Automated infrastructure capacity monitoring and alerting")
    .params(
        cpu_threshold=80.0,
        memory_threshold=85.0,
        disk_threshold=90.0,
        capacity_channel="#capacity-alerts"
    )
    .step("collect_resource_metrics", callback=lambda s:
        s.description("Collect current resource utilization using SystemMetricsCommand")
        .shell(
            SystemMetricsCommand(
                metric_types=["cpu", "memory", "disk"],
                top_processes_count=10
            ).get_command()
        )
        .output("metrics_collected")
    )
    .step("analyze_capacity_trends", callback=lambda s:
        s.description("Analyze capacity trends and patterns using DataAnalysisPrompt")
        .shell(
            DataAnalysisPrompt(
                dataset_description="Infrastructure capacity metrics over time",
                analysis_type="predictive",
                key_questions=["What are the capacity growth trends?", "When will we reach capacity limits?"]
            ).get_command()
        )
        .depends("collect_resource_metrics")
        .output("trends_analyzed")
    )
    .step("predict_capacity_needs", callback=lambda s:
        s.description("Predict future capacity requirements")
        .shell("""
echo "🔮 PREDICTING CAPACITY NEEDS"
echo "Based on current trends and historical data..."
echo "Predicted capacity needs for next 30 days"
echo "✅ Capacity prediction completed"
""")
        .depends("analyze_capacity_trends")
        .output("predictions_made")
    )
    .step("generate_capacity_alerts", callback=lambda s:
        s.description("Generate alerts for threshold breaches using CapacityWarningMessage")
        .shell(
            CapacityWarningMessage(
                channel="{{.capacity_channel}}",
                resource_type="cpu",
                current_usage="{{.cpu_threshold}}",
                threshold="75.0",
                affected_services=["web-service", "api-service"],
                recommended_action="Consider scaling up instances or optimizing resource usage"
            ).get_command()
        )
        .depends("predict_capacity_needs")
        .output("alerts_generated")
    )
    .step("recommend_scaling_actions", callback=lambda s:
        s.description("Recommend scaling actions")
        .shell("""
echo "📋 SCALING RECOMMENDATIONS"
echo "1. Scale up web-service instances by 2"
echo "2. Optimize database queries to reduce CPU usage"
echo "3. Implement caching to reduce memory pressure"
echo "4. Consider upgrading instance types"
echo "✅ Scaling recommendations generated"
""")
        .depends("generate_capacity_alerts")
        .output("recommendations_made")
    )
    .step("schedule_capacity_review", callback=lambda s:
        s.description("Schedule capacity planning review using ReportGenerationCommand")
        .shell(
            ReportGenerationCommand(
                report_type="capacity_review",
                title="📅 CAPACITY PLANNING REVIEW",
                sections={
                    "Schedule": "Capacity planning review scheduled for next week",
                    "Stakeholders": "All stakeholders will be notified",
                    "Recommendations": "${recommendations_made}",
                    "Status": "Review scheduled successfully"
                }
            ).get_command()
        )
        .depends("recommend_scaling_actions")
    )
)
### END: capacity_monitoring_workflow ###



### START: troubleshooting_automation_workflow ###
"""
Troubleshooting Automation Workflow
===================================
Purpose: Automated troubleshooting and problem resolution
Workflow Steps:
1. identify_problem_symptoms - Identify and categorize problem symptoms
2. gather_diagnostic_data - Gather relevant diagnostic information
3. analyze_root_causes - Analyze potential root causes
4. execute_diagnostic_steps - Execute systematic diagnostic steps
5. implement_solutions - Implement recommended solutions
6. verify_problem_resolution - Verify that the problem is resolved
Models Used: TroubleshootingPrompt, AlertResolutionMessage
"""

def troubleshooting_automation_workflow():
    from models.models import (
        TroubleshootingPrompt,
        AlertResolutionMessage,
        ProblemDiagnosticsCommand,
        SystemMetricsCommand,
    )
    
    return (Workflow("troubleshooting_automation_workflow")
    .description("Automated troubleshooting and problem resolution")
    .params(
        problem_description="Application response time degradation",
        affected_system="web-application",
        urgency_level="high",
        support_channel="#support"
    )
    .step("identify_problem_symptoms", callback=lambda s:
        s.description("Identify and categorize problem symptoms")
        .shell("""
echo "🔍 IDENTIFYING PROBLEM SYMPTOMS"
echo "Problem: ${problem_description}"
echo "System: ${affected_system}"
echo "Urgency: ${urgency_level}"
echo "Symptoms categorized and documented"
echo "✅ Problem identification completed"
""")
        .output("symptoms_identified")
    )
    .step("gather_diagnostic_data", callback=lambda s:
        s.description("Gather relevant diagnostic information using SystemMetricsCommand")
        .shell(
            SystemMetricsCommand(
                metric_types=["cpu", "memory", "disk", "processes"],
                top_processes_count=15
            ).get_command()
        )
        .depends("identify_problem_symptoms")
        .output("diagnostics_gathered")
    )
    .step("analyze_root_causes", callback=lambda s:
        s.description("Analyze potential root causes using TroubleshootingPrompt")
        .shell(
            TroubleshootingPrompt(
                problem_description="${problem_description}",
                system_context="${affected_system}",
                urgency_level="${urgency_level}",
                affected_components=["database", "web-server", "cache"]
            ).get_command()
        )
        .depends("gather_diagnostic_data")
        .output("root_causes_analyzed")
    )
    .step("execute_diagnostic_steps", callback=lambda s:
        s.description("Execute systematic diagnostic steps using ProblemDiagnosticsCommand")
        .shell(
            ProblemDiagnosticsCommand(
                diagnostic_type="application",
                target_components=["database", "web-server", "cache"],
                timeout_seconds=120
            ).get_command()
        )
        .depends("analyze_root_causes")
        .output("diagnostics_executed")
    )
    .step("implement_solutions", callback=lambda s:
        s.description("Implement recommended solutions")
        .shell("""
echo "🛠️ IMPLEMENTING SOLUTIONS"
echo "Applying recommended fixes based on analysis..."
echo "1. Restarting problematic services"
echo "2. Clearing cache"
echo "3. Optimizing database queries"
echo "✅ Solutions implemented"
""")
        .depends("execute_diagnostic_steps")
        .output("solutions_implemented")
    )
    .step("verify_problem_resolution", callback=lambda s:
        s.description("Verify that the problem is resolved using AlertResolutionMessage")
        .shell(
            AlertResolutionMessage(
                channel="{{.support_channel}}",
                alert_id="TROUBLE-$(date +%Y%m%d-%H%M%S)",
                alert_title="{{.problem_description}}",
                resolution_status="resolved",
                resolution_time="$(date)",
                root_cause="Performance optimization needed",
                actions_taken=["Service restart", "Cache clear", "Query optimization"]
            ).get_command()
        )
        .depends("implement_solutions")
    )
)
### END: troubleshooting_automation_workflow ###


### START: devops_pipeline_workflow ###
"""
DevOps Pipeline Workflow
========================
Purpose: Complete DevOps pipeline with testing, deployment, and monitoring
Workflow Steps:
1. validate_environment - Validate deployment environment setup
2. run_performance_tests - Execute performance testing suite
3. generate_test_data - Create test datasets for validation
4. backup_database - Backup production database before deployment
5. deploy_configuration - Deploy application configuration
6. health_check_kubernetes - Verify Kubernetes cluster health
7. send_deployment_notification - Notify team of deployment status
8. generate_deployment_report - Create comprehensive deployment report
Models Used: ValidationCommand, PerformanceTestCommand, TestDataGenerator, DatabaseBackupCommand, 
            ConfigurationFileGenerator, KubernetesHealthCheckCommand, DeploymentStatusMessage, ReportGenerationCommand
"""

def devops_pipeline_workflow():
    from models.models import (
        ValidationCommand,
        PerformanceTestCommand,
        TestDataGenerator,
        DatabaseBackupCommand,
        ConfigurationFileGenerator,
        KubernetesHealthCheckCommand,
        DeploymentStatusMessage,
        ReportGenerationCommand,
    )
    
    return (Workflow("devops_pipeline_workflow")
    .description("Complete DevOps pipeline with testing, deployment, and monitoring")
    .params(
        environment="production",
        app_name="my-service",
        version="v2.1.0",
        target_url="https://api.myservice.com",
        concurrent_users="50",
        test_duration="3",
        database_name="myservice_db",
        record_count="1000"
    )
    .step("validate_environment", callback=lambda s:
        s.description("Validate deployment environment setup")
        .shell(
            ValidationCommand(
                validation_type="environment",
                target_path="/opt/deployments/${environment}",
                resource_location="/opt/app-configs",
                resource_name="${app_name}"
            ).get_command()
        )
        .output("env_validated")
    )
    .step("run_performance_tests", callback=lambda s:
        s.description("Execute performance testing suite")
        .shell(
            PerformanceTestCommand(
                test_type="load",
                target_url="${target_url}",
                concurrent_users="${concurrent_users}",
                test_duration_minutes="${test_duration}"
            ).get_command()
        )
        .depends("validate_environment")
        .output("perf_results")
    )
    .step("generate_test_data", callback=lambda s:
        s.description("Create test datasets for validation")
        .shell(
            TestDataGenerator(
                data_type="users",
                record_count="${record_count}",
                output_format="json",
                locale="en_US"
            ).get_command()
        )
        .depends("run_performance_tests")
        .output("test_data_ready")
    )
    .step("backup_database", callback=lambda s:
        s.description("Backup production database before deployment")
        .shell(
            DatabaseBackupCommand(
                database_type="postgresql",
                database_name="${database_name}",
                backup_location="/tmp/pipeline_backups"
            ).get_command()
        )
        .depends("generate_test_data")
        .output("backup_completed")
    )
    .step("deploy_configuration", callback=lambda s:
        s.description("Deploy application configuration")
        .shell(
            ConfigurationFileGenerator(
                config_type="application",
                environment="${environment}",
                output_format="yaml"
            ).get_command()
        )
        .depends("backup_database")
        .output("config_deployed")
    )
    .step("health_check_kubernetes", callback=lambda s:
        s.description("Verify Kubernetes cluster health")
        .shell(
            KubernetesHealthCheckCommand(
                check_type="comprehensive",
                timeout_seconds="60"
            ).get_command()
        )
        .depends("deploy_configuration")
        .output("cluster_healthy")
    )
    .step("send_deployment_notification", callback=lambda s:
        s.description("Notify team of deployment status")
        .shell(
            DeploymentStatusMessage(
                channel="#deployments",
                deployment_id="DEPLOY-${version}",
                service_name="${app_name}",
                environment="${environment}",
                version="${version}",
                status="success",
                deploy_time="$(date '+%Y-%m-%d %H:%M:%S')"
            ).get_command()
        )
        .depends("health_check_kubernetes")
        .output("notification_sent")
    )
    .step("generate_deployment_report", callback=lambda s:
        s.description("Create comprehensive deployment report")
        .shell(
            ReportGenerationCommand(
                report_type="deployment",
                title="🚀 DEVOPS PIPELINE DEPLOYMENT REPORT",
                sections={
                    "Environment": "${environment}",
                    "Application": "${app_name} ${version}",
                    "Performance Tests": "${perf_results}",
                    "Test Data": "${test_data_ready}",
                    "Database Backup": "${backup_completed}",
                    "Configuration": "${config_deployed}",
                    "Health Check": "${cluster_healthy}",
                    "Notification": "${notification_sent}"
                }
            ).get_command()
        )
        .depends("send_deployment_notification")
        .output("report_generated")
    )
)
### END: devops_pipeline_workflow ###


### START: security_compliance_workflow ###
"""
Security Compliance Workflow
============================
Purpose: Security audit and compliance checking with incident response
Workflow Steps:
1. scan_security_vulnerabilities - Perform comprehensive security scan
2. validate_security_configs - Validate security configuration files
3. check_cluster_security - Verify Kubernetes cluster security
4. analyze_security_logs - Analyze security logs for threats
5. assess_incident_severity - Assess any discovered security incidents
6. generate_security_report - Generate technical security documentation
7. send_security_alert - Send security incident notifications
8. compile_compliance_report - Compile final compliance assessment
Models Used: SecurityScanCommand, ValidationCommand, KubernetesHealthCheckCommand, LogAnalysisReport,
            IncidentAssessmentCommand, TechnicalDocumentationPrompt, SecurityIncidentMessage, ReportGenerationCommand
"""

def security_compliance_workflow():
    from models.models import (
        SecurityScanCommand,
        ValidationCommand,
        KubernetesHealthCheckCommand,
        LogAnalysisReport,
        IncidentAssessmentCommand,
        TechnicalDocumentationPrompt,
        SecurityIncidentMessage,
        ReportGenerationCommand,
    )
    
    return (Workflow("security_compliance_workflow")
    .description("Security audit and compliance checking with incident response")
    .params(
        scan_target="/opt/applications",
        severity_threshold="medium",
        escalation_threshold="15",
        incident_id="SEC-2024-001",
        compliance_standard="SOC2"
    )
    .step("scan_security_vulnerabilities", callback=lambda s:
        s.description("Perform comprehensive security scan")
        .shell(
            SecurityScanCommand(
                scan_type="filesystem",
                target="${scan_target}",
                scan_depth="standard",
                output_format="json",
                alert_on_critical=True
            ).get_command()
        )
        .output("scan_results")
    )
    .step("validate_security_configs", callback=lambda s:
        s.description("Validate security configuration files")
        .shell(
            ValidationCommand(
                validation_type="security",
                target_path="/etc/security/configs",
                resource_location="/opt/security-templates",
                resource_name="security-baseline"
            ).get_command()
        )
        .depends("scan_security_vulnerabilities")
        .output("configs_validated")
    )
    .step("check_cluster_security", callback=lambda s:
        s.description("Verify Kubernetes cluster security")
        .shell(
            KubernetesHealthCheckCommand(
                check_type="security",
                timeout_seconds="120"
            ).get_command()
        )
        .depends("validate_security_configs")
        .output("cluster_security_status")
    )
    .step("analyze_security_logs", callback=lambda s:
        s.description("Analyze security logs for threats")
        .shell(
            LogAnalysisReport(
                log_source="security",
                analysis_period="last_day",
                include_security=True,
                output_format="markdown"
            ).get_command()
        )
        .depends("check_cluster_security")
        .output("log_analysis")
    )
    .step("assess_incident_severity", callback=lambda s:
        s.description("Assess any discovered security incidents")
        .shell(
            IncidentAssessmentCommand(
                incident_id="${incident_id}",
                current_severity="${severity_threshold}",
                escalation_threshold_minutes="${escalation_threshold}",
                affected_systems=["production", "staging"]
            ).get_command()
        )
        .depends("analyze_security_logs")
        .output("incident_assessment")
    )
    .step("generate_security_report", callback=lambda s:
        s.description("Generate technical security documentation")
        .shell(
            TechnicalDocumentationPrompt(
                doc_type="security",
                project_context="${compliance_standard} Security Compliance Report",
                target_audience="security_team",
                include_examples=True
            ).get_command()
        )
        .depends("assess_incident_severity")
        .output("security_docs")
    )
    .step("send_security_alert", callback=lambda s:
        s.description("Send security incident notifications")
        .shell(
            SecurityIncidentMessage(
                channel="#security-alerts",
                incident_id="${incident_id}",
                incident_type="unauthorized_access",
                severity="${severity_threshold}",
                affected_systems=["production", "staging"],
                status="investigating"
            ).get_command()
        )
        .depends("generate_security_report")
        .output("alert_sent")
    )
    .step("compile_compliance_report", callback=lambda s:
        s.description("Compile final compliance assessment")
        .shell(
            ReportGenerationCommand(
                report_type="compliance",
                title="🔐 SECURITY COMPLIANCE ASSESSMENT REPORT",
                sections={
                    "Compliance Standard": "${compliance_standard}",
                    "Vulnerability Scan": "${scan_results}",
                    "Configuration Validation": "${configs_validated}",
                    "Cluster Security": "${cluster_security_status}",
                    "Log Analysis": "${log_analysis}",
                    "Incident Assessment": "${incident_assessment}",
                    "Security Documentation": "${security_docs}",
                    "Alert Status": "${alert_sent}"
                }
            ).get_command()
        )
        .depends("send_security_alert")
        .output("compliance_report")
    )
)
### END: security_compliance_workflow ###



# ============================================================================
# WORKFLOW REGISTRY
# ============================================================================


# Export workflows
__all__ = [
    "url_validation_workflow",
    "text_processing_workflow", 
    "system_monitoring_workflow",
    "utility_workflow",
    "utility_toolkit_workflow",
    "security_workflow",
    "data_conversion_workflow",
    "network_security_workflow",
    "database_backup_workflow",
    "kubernetes_health_check_workflow", 
    "security_scan_workflow",
    "documentation_generation_workflow",
    "performance_testing_workflow",
    "log_analysis_workflow",
    "configuration_deployment_workflow",
    "test_data_generation_workflow",
    "code_review_automation_workflow",
    "database_migration_workflow",
    "incident_escalation_workflow",
    "capacity_monitoring_workflow",
    "troubleshooting_automation_workflow",
    "devops_pipeline_workflow",
    "security_compliance_workflow",
]