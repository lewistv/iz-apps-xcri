#!/bin/bash
#
# XCRI Rankings Real-Time Monitor
# Monitors API performance, traffic, resource usage, and errors
#
# Usage: ./xcri_monitor.sh [interval_seconds]
#

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REFRESH_INTERVAL=${1:-10}  # Default 10 seconds
XCRI_DIR="/home/web4ustfccca/public_html/iz/xcri"
API_PROCESS_NAME="uvicorn main:app"
API_PORT=8001
API_URL="http://127.0.0.1:8001"

# Apache log paths
APACHE_ACCESS_LOG="/var/log/apache2/access.log"
APACHE_ERROR_LOG="/var/log/apache2/error.log"

# MySQL defaults file
MYSQL_CONFIG="$HOME/.mysql/web4.cnf"
DB_NAME="web4ustfccca_iz"

# Stats tracking
declare -A prev_stats
prev_stats[requests]=0
prev_stats[errors]=0
prev_stats[time]=$(date +%s)

#================================================================
# Helper Functions
#================================================================

check_requirements() {
    local missing=()

    command -v curl >/dev/null 2>&1 || missing+=("curl")
    command -v mysql >/dev/null 2>&1 || missing+=("mysql")

    if [ ${#missing[@]} -gt 0 ]; then
        echo "Error: Missing required commands: ${missing[*]}"
        exit 1
    fi

    if [ ! -f "$MYSQL_CONFIG" ]; then
        echo "Warning: MySQL config not found at $MYSQL_CONFIG"
        echo "Database metrics will be unavailable"
    fi
}

get_api_pid() {
    # Get the master uvicorn process (not the bash wrapper or workers)
    ps aux | grep "uvicorn main:app --host 127.0.0.1 --port 8001" | grep -v grep | grep -v "bash -c" | head -1 | awk '{print $2}'
}

get_worker_count() {
    # Count all Python processes related to uvicorn (master + workers)
    # Includes: master, resource tracker, and spawned workers
    ps aux | grep -E "(uvicorn main:app|multiprocessing.*spawn_main)" | grep -v grep | grep -v "bash -c" | wc -l
}

get_worker_stats() {
    # Get all worker PIDs and their stats (including master and spawned workers)
    local pids=$(ps aux | grep -E "(uvicorn main:app|multiprocessing.*spawn_main)" | grep -v grep | grep -v "bash -c" | awk '{print $2}')
    local total_cpu=0
    local total_mem=0
    local count=0

    while read -r pid; do
        if [ -n "$pid" ]; then
            local stats=$(ps -p "$pid" -o %cpu,rss 2>/dev/null | tail -1)
            if [ -n "$stats" ]; then
                local cpu=$(echo "$stats" | awk '{print $1}')
                local mem_kb=$(echo "$stats" | awk '{print $2}')

                total_cpu=$(echo "$total_cpu + $cpu" | bc)
                total_mem=$((total_mem + mem_kb))
                ((count++))
            fi
        fi
    done <<< "$pids"

    local avg_mem_mb=$(echo "scale=1; $total_mem / 1024" | bc)

    echo "$count|$total_cpu|$avg_mem_mb"
}

get_api_health() {
    local response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$API_URL/health" 2>/dev/null)
    local http_code=$(echo "$response" | tail -2 | head -1)
    local time_total=$(echo "$response" | tail -1)

    if [ "$http_code" = "200" ]; then
        echo "HEALTHY|$time_total"
    else
        echo "DOWN|0"
    fi
}

get_process_stats() {
    local pid=$1
    if [ -z "$pid" ]; then
        echo "0|0|0"
        return
    fi

    # Get CPU%, Memory(MB), and uptime
    local stats=$(ps -p "$pid" -o %cpu,rss,etime | tail -1)
    local cpu=$(echo "$stats" | awk '{print $1}')
    local mem_kb=$(echo "$stats" | awk '{print $2}')
    local mem_mb=$(echo "scale=1; $mem_kb / 1024" | bc)
    local uptime=$(echo "$stats" | awk '{print $3}')

    echo "$cpu|$mem_mb|$uptime"
}

get_apache_stats() {
    local since_seconds=${1:-60}

    # Count XCRI requests in last N seconds
    local since_time=$(date -d "$since_seconds seconds ago" "+%d/%b/%Y:%H:%M:%S" 2>/dev/null || date -v-${since_seconds}S "+%d/%b/%Y:%H:%M:%S")

    if [ ! -r "$APACHE_ACCESS_LOG" ]; then
        echo "0|0|0|0"
        return
    fi

    # XCRI requests, unique IPs, avg response time, status codes
    local xcri_requests=$(grep -c "/iz/xcri" "$APACHE_ACCESS_LOG" 2>/dev/null || echo 0)
    local unique_ips=$(grep "/iz/xcri" "$APACHE_ACCESS_LOG" 2>/dev/null | awk '{print $1}' | sort -u | wc -l)
    local errors_5xx=$(grep "/iz/xcri" "$APACHE_ACCESS_LOG" 2>/dev/null | grep -c '" 5[0-9][0-9] ' || echo 0)
    local errors_4xx=$(grep "/iz/xcri" "$APACHE_ACCESS_LOG" 2>/dev/null | grep -c '" 4[0-9][0-9] ' || echo 0)

    echo "$xcri_requests|$unique_ips|$errors_5xx|$errors_4xx"
}

get_database_stats() {
    if [ ! -f "$MYSQL_CONFIG" ]; then
        echo "0|0|0"
        return
    fi

    # Query counts, connection count, slow queries
    local connections=$(mysql --defaults-file="$MYSQL_CONFIG" -sN -e "
        SELECT COUNT(*) FROM information_schema.PROCESSLIST
        WHERE DB = '$DB_NAME' OR COMMAND != 'Sleep'
    " 2>/dev/null || echo 0)

    local query_count=$(mysql --defaults-file="$MYSQL_CONFIG" -sN -e "
        SELECT COUNT(*) FROM information_schema.PROCESSLIST
        WHERE DB = '$DB_NAME' AND COMMAND = 'Query'
    " 2>/dev/null || echo 0)

    local slow_queries=$(mysql --defaults-file="$MYSQL_CONFIG" -sN -e "
        SELECT COUNT(*) FROM information_schema.PROCESSLIST
        WHERE DB = '$DB_NAME' AND TIME > 5
    " 2>/dev/null || echo 0)

    echo "$connections|$query_count|$slow_queries"
}

get_system_resources() {
    # Load average, disk usage, memory usage
    local load=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | xargs)
    local disk=$(df -h "$XCRI_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
    local mem=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')

    echo "$load|$disk|$mem"
}

calculate_rate() {
    local current=$1
    local prev=$2
    local time_diff=$3

    if [ "$time_diff" -gt 0 ]; then
        echo "scale=1; ($current - $prev) / $time_diff" | bc
    else
        echo "0"
    fi
}

#================================================================
# Display Functions
#================================================================

display_header() {
    echo "========================================================================"
    echo "XCRI Rankings - Real-Time Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================================================"
}

display_api_status() {
    local pid=$(get_api_pid)
    local worker_count=$(get_worker_count)
    local health=$(get_api_health)
    local status=$(echo "$health" | cut -d'|' -f1)
    local response_time=$(echo "$health" | cut -d'|' -f2)

    echo -e "\n${CYAN}📊 API Status (Async + Multi-Worker)${NC}"
    echo "----------------------------------------"

    if [ "$status" = "HEALTHY" ]; then
        echo -e "Status:         ${GREEN}● HEALTHY${NC}"
        echo -e "Response Time:  ${GREEN}${response_time}s${NC}"
    else
        echo -e "Status:         ${RED}● DOWN${NC}"
    fi

    if [ -n "$pid" ]; then
        local worker_stats=$(get_worker_stats)
        local count=$(echo "$worker_stats" | cut -d'|' -f1)
        local total_cpu=$(echo "$worker_stats" | cut -d'|' -f2)
        local total_mem=$(echo "$worker_stats" | cut -d'|' -f3)

        # Show process info
        local stats=$(get_process_stats "$pid")
        local uptime=$(echo "$stats" | cut -d'|' -f3)

        echo "Master PID:     $pid"
        echo "Workers:        $count processes"
        echo "Uptime:         $uptime"
        echo "Architecture:   Async + Connection Pool (10 conn/worker)"

        # Color code CPU usage
        if (( $(echo "$total_cpu > 80" | bc -l) )); then
            echo -e "Total CPU:      ${RED}${total_cpu}%${NC}"
        elif (( $(echo "$total_cpu > 50" | bc -l) )); then
            echo -e "Total CPU:      ${YELLOW}${total_cpu}%${NC}"
        else
            echo -e "Total CPU:      ${GREEN}${total_cpu}%${NC}"
        fi

        # Color code memory usage
        if (( $(echo "$total_mem > 500" | bc -l) )); then
            echo -e "Total Memory:   ${RED}${total_mem} MB${NC}"
        elif (( $(echo "$total_mem > 300" | bc -l) )); then
            echo -e "Total Memory:   ${YELLOW}${total_mem} MB${NC}"
        else
            echo -e "Total Memory:   ${GREEN}${total_mem} MB${NC}"
        fi
    else
        echo -e "${RED}Process not found!${NC}"
    fi
}

display_traffic_stats() {
    local stats=$(get_apache_stats)
    local requests=$(echo "$stats" | cut -d'|' -f1)
    local unique_ips=$(echo "$stats" | cut -d'|' -f2)
    local errors_5xx=$(echo "$stats" | cut -d'|' -f3)
    local errors_4xx=$(echo "$stats" | cut -d'|' -f4)

    echo -e "\n${CYAN}🌐 Traffic Statistics (Total)${NC}"
    echo "----------------------------------------"
    echo "Total Requests: $requests"
    echo "Unique IPs:     $unique_ips"

    # Calculate request rate
    local current_time=$(date +%s)
    local time_diff=$((current_time - prev_stats[time]))

    if [ "$time_diff" -gt 0 ]; then
        local req_rate=$(calculate_rate "$requests" "${prev_stats[requests]}" "$time_diff")
        echo -e "Request Rate:   ${GREEN}${req_rate} req/s${NC}"

        # Update previous stats
        prev_stats[requests]=$requests
        prev_stats[time]=$current_time
    fi

    # Error rates
    if [ "$errors_5xx" -gt 0 ]; then
        echo -e "5xx Errors:     ${RED}$errors_5xx${NC}"
    else
        echo "5xx Errors:     $errors_5xx"
    fi

    if [ "$errors_4xx" -gt 0 ]; then
        echo -e "4xx Errors:     ${YELLOW}$errors_4xx${NC}"
    else
        echo "4xx Errors:     $errors_4xx"
    fi
}

display_database_stats() {
    local stats=$(get_database_stats)
    local connections=$(echo "$stats" | cut -d'|' -f1)
    local queries=$(echo "$stats" | cut -d'|' -f2)
    local slow=$(echo "$stats" | cut -d'|' -f3)

    echo -e "\n${CYAN}💾 Database Activity${NC}"
    echo "----------------------------------------"
    echo "Connections:    $connections"
    echo "Active Queries: $queries"

    if [ "$slow" -gt 0 ]; then
        echo -e "Slow Queries:   ${YELLOW}$slow (>5s)${NC}"
    else
        echo "Slow Queries:   $slow"
    fi
}

display_system_resources() {
    local stats=$(get_system_resources)
    local load=$(echo "$stats" | cut -d'|' -f1)
    local disk=$(echo "$stats" | cut -d'|' -f2)
    local mem=$(echo "$stats" | cut -d'|' -f3)

    echo -e "\n${CYAN}⚙️  System Resources${NC}"
    echo "----------------------------------------"

    # Color code load (assume 4 core system)
    if (( $(echo "$load > 4" | bc -l) )); then
        echo -e "Load Average:   ${RED}${load}${NC}"
    elif (( $(echo "$load > 2" | bc -l) )); then
        echo -e "Load Average:   ${YELLOW}${load}${NC}"
    else
        echo -e "Load Average:   ${GREEN}${load}${NC}"
    fi

    # Color code disk usage
    if [ "$disk" -gt 90 ]; then
        echo -e "Disk Usage:     ${RED}${disk}%${NC}"
    elif [ "$disk" -gt 80 ]; then
        echo -e "Disk Usage:     ${YELLOW}${disk}%${NC}"
    else
        echo -e "Disk Usage:     ${GREEN}${disk}%${NC}"
    fi

    # Color code memory usage
    if [ "$mem" -gt 90 ]; then
        echo -e "Memory Usage:   ${RED}${mem}%${NC}"
    elif [ "$mem" -gt 80 ]; then
        echo -e "Memory Usage:   ${YELLOW}${mem}%${NC}"
    else
        echo -e "Memory Usage:   ${GREEN}${mem}%${NC}"
    fi
}

display_recent_errors() {
    if [ ! -r "$APACHE_ERROR_LOG" ]; then
        return
    fi

    local recent_errors=$(grep "xcri" "$APACHE_ERROR_LOG" 2>/dev/null | tail -3)

    if [ -n "$recent_errors" ]; then
        echo -e "\n${CYAN}⚠️  Recent Errors (Last 3)${NC}"
        echo "----------------------------------------"
        echo "$recent_errors" | while read -r line; do
            echo -e "${RED}${line:0:100}${NC}"
        done
    fi
}

display_endpoints_usage() {
    if [ ! -r "$APACHE_ACCESS_LOG" ]; then
        return
    fi

    echo -e "\n${CYAN}🔗 Top Endpoints (Last 100 requests)${NC}"
    echo "----------------------------------------"

    # Get top 5 XCRI endpoints
    grep "/iz/xcri" "$APACHE_ACCESS_LOG" 2>/dev/null | tail -100 | \
        awk '{print $7}' | grep -o '/iz/xcri[^ ]*' | \
        sort | uniq -c | sort -rn | head -5 | \
        awk '{printf "%-6s %s\n", $1, $2}'
}

#================================================================
# Main Monitor Loop
#================================================================

main() {
    check_requirements

    # Trap Ctrl+C for clean exit
    trap 'echo -e "\n\n${GREEN}Monitor stopped.${NC}"; exit 0' INT

    while true; do
        clear
        display_header
        display_api_status
        display_traffic_stats
        display_database_stats
        display_system_resources
        display_endpoints_usage
        display_recent_errors

        echo -e "\n========================================================================"
        echo -e "Refreshing in ${REFRESH_INTERVAL} seconds... (Press Ctrl+C to exit)"
        sleep "$REFRESH_INTERVAL"
    done
}

# Run the monitor
main
