"""
Simple Workflows using Custom Tools

This module contains 3 simple workflows that demonstrate how to use custom tools
as steps along with simple shell script steps.
"""

from kubiya_workflow_sdk.dsl import Workflow, Step
from workflows.custom_tools import (
    json_processor, text_analyzer, url_validator, 
    system_info, network_checker, log_analyzer
)

# ============================================================================
# WORKFLOW 1: URL VALIDATION AND ANALYSIS
# ============================================================================

def create_url_validation_workflow():
    """
    Workflow that validates URLs, checks connectivity, and analyzes the results.
    """
    
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
            s.description("Generate comprehensive analysis summary")
            .shell("""
echo "=== URL Analysis Summary ==="
echo "Target URL: ${target_url}"
echo "Validation: ${validation_result}"
echo "Connectivity: ${connectivity_result}"
echo "Analysis completed at: $(date)"
""")
            .depends("validate_url", "check_connectivity")
        )
            )


# ============================================================================
# WORKFLOW 2: TEXT PROCESSING PIPELINE
# ============================================================================

def create_text_processing_workflow():
    """
    Workflow that processes text through multiple stages of analysis.
    """
    
    return (Workflow("text_processing_workflow")
        .description("Process and analyze text content through multiple stages")
        .params(input_text="Hello world! This is a sample text for analysis.")
        .step("prepare_text", callback=lambda s:
            s.description("Prepare text for analysis")
            .shell('echo "Preparing text for analysis..." && echo "${input_text}" > /tmp/text_input.txt')
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
            s.description("Count characters using shell")
            .shell('echo "Character count: $(echo -n "${input_text}" | wc -c)"')
            .output("char_count")
            .depends("prepare_text")
        )
        .step("extract_unique_words", callback=lambda s:
            s.description("Extract unique words using shell")
            .shell("""
echo "${input_text}" | tr ' ' '\\n' | tr '[:upper:]' '[:lower:]' | sort | uniq | head -10
""")
            .output("unique_words")
            .depends("prepare_text")
        )
        .step("generate_report", callback=lambda s:
            s.description("Generate final text processing report")
            .shell("""
echo "=== Text Processing Report ==="
echo "Original text length: ${char_count}"
echo ""
echo "Analysis Results:"
echo "${analysis_result}"
echo ""
echo "Top unique words:"
echo "${unique_words}"
echo ""
echo "Report generated at: $(date)"
""")
            .depends("analyze_text", "count_characters", "extract_unique_words")
        ))


# ============================================================================
# WORKFLOW 3: SYSTEM MONITORING AND LOG ANALYSIS
# ============================================================================

def create_system_monitoring_workflow():
    """
    Workflow that monitors system status and analyzes logs.
    """
    
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
            s.description("Create comprehensive monitoring report")
            .shell("""
echo "=== System Monitoring Report ==="
echo "Timestamp: $(date)"
echo ""
echo "=== System Status ==="
echo "${system_status}"
echo ""
echo "=== Disk Usage ==="
echo "${disk_info}"
echo ""
echo "=== Running Processes (Top 10) ==="
echo "${process_list}"
echo ""
echo "=== Log Analysis ==="
echo "${log_summary}"
echo ""
echo "=== Error Summary ==="
echo "${error_summary}"
echo ""
echo "=== End of Report ==="
""")
            .depends("get_system_info", "check_disk_space", "check_processes", "check_log_errors")
        )
        .step("cleanup", callback=lambda s:
            s.description("Cleanup temporary files")
            .shell('echo "Monitoring workflow completed successfully" && rm -f /tmp/monitoring_*')
            .depends("create_monitoring_report")
        ))


# ============================================================================
# WORKFLOW REGISTRY
# ============================================================================

# Create workflow instances
url_validation_workflow = create_url_validation_workflow()
text_processing_workflow = create_text_processing_workflow()
system_monitoring_workflow = create_system_monitoring_workflow()

# Export workflows
__all__ = [
    "url_validation_workflow",
    "text_processing_workflow", 
    "system_monitoring_workflow",
    "create_url_validation_workflow",
    "create_text_processing_workflow",
    "create_system_monitoring_workflow"
]