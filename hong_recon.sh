#!/bin/bash

# Check if URL argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <domain> [-d directory]"
    exit 1
fi

DOMAIN=$1
BASE_DIR=""
URL_ANALYZER_PATH="$HOME/tools/url_analyzer/url_analyzer.py"

# Parse -d option for custom directory
while getopts "d:" opt; do
    case $opt in
        d) BASE_DIR="$OPTARG"
           ;;
        ?) echo "Usage: $0 <domain> [-d directory]"
           exit 1
           ;;
    esac
done

# Shift past the options
shift $((OPTIND-1))

# Set default directory if not specified
if [ -z "$BASE_DIR" ]; then
    BASE_DIR="$(pwd)/${DOMAIN}_recon"
fi

# Create directory structure
mkdir -p "$BASE_DIR"
echo "[+] Working directory: $BASE_DIR"

# Run Sublist3r
echo "[+] Running Sublist3r..."
python3 Sublist3r/sublist3r.py -d "$DOMAIN" -o "$BASE_DIR/sublist3r.txt" > /dev/null 2>&1

# Run Subfinder
echo "[+] Running Subfinder..."
subfinder -d "$DOMAIN" -o "$BASE_DIR/subfinder.txt" > /dev/null 2>&1

# Run gau
echo "[+] Running gau..."
docker run gau "$DOMAIN" | tee "$BASE_DIR/gau.txt" > /dev/null 2>&1

# Analyze URLs with url_analyzer.py
echo "[+] Analyzing URLs with url_analyzer.py..."
python3 "$URL_ANALYZER_PATH" "$BASE_DIR/gau.txt" -o "$BASE_DIR/gau_analysis.txt" > /dev/null 2>&1

# Combine all subdomains and remove duplicates
echo "[+] Combining subdomains..."
cat "$BASE_DIR/sublist3r.txt" "$BASE_DIR/subfinder.txt" "$BASE_DIR/gau_analysis_subdomains.txt" 2>/dev/null | \
    sort -u > "$BASE_DIR/all_subdomains.txt"
echo "[+] Total unique subdomains: $(wc -l < "$BASE_DIR/all_subdomains.txt")"

# Analyze subdirectories
echo "[+] Analyzing subdirectories..."
SUBDIR_FILE="$BASE_DIR/gau_analysis_subdirs.txt"
if [ -f "$SUBDIR_FILE" ]; then
    # Count total unique subdirectories
    TOTAL_SUBDIRS=$(wc -l < "$SUBDIR_FILE")
    echo "    Total unique subdirectories: $TOTAL_SUBDIRS"
    
    # Find most common subdirectory patterns (top 5)
    echo "    Top 5 subdirectory patterns:" > "$BASE_DIR/subdir_summary.txt"
    sort "$SUBDIR_FILE" | uniq -c | sort -nr | head -n 5 | \
        awk '{print "    " $2 " (" $1 " occurrences)"}' >> "$BASE_DIR/subdir_summary.txt"
    cat "$BASE_DIR/subdir_summary.txt"
fi

# Analyze parameters
echo "[+] Analyzing parameters..."
PARAM_FILE="$BASE_DIR/gau_analysis_params.txt"
if [ -f "$PARAM_FILE" ]; then
    # Count total unique parameters
    TOTAL_PARAMS=$(wc -l < "$PARAM_FILE")
    echo "    Total unique parameters: $TOTAL_PARAMS"
    
    # Extract parameters without counts and find most common (top 5)
    echo "    Top 5 parameters by occurrence:" > "$BASE_DIR/param_summary.txt"
    sed 's/ ([0-9]* occurrences)//' "$PARAM_FILE" | sort | uniq -c | sort -nr | head -n 5 | \
        awk '{print "    " $2 " (" $1 " occurrences)"}' >> "$BASE_DIR/param_summary.txt"
    cat "$BASE_DIR/param_summary.txt"
    
    # Look for potentially interesting parameters
    echo "    Potentially sensitive parameters:" >> "$BASE_DIR/param_summary.txt"
    grep -iE "(key|token|pass|secret|auth|id|user|admin|config)" "$PARAM_FILE" | \
        sort -u >> "$BASE_DIR/param_summary.txt"
fi

# Run httpx to check availability
echo "[+] Checking availability with httpx..."
httpx -l "$BASE_DIR/all_subdomains.txt" -o "$BASE_DIR/live_subdomains.txt" > /dev/null 2>&1
echo "[+] Live subdomains found: $(wc -l < "$BASE_DIR/live_subdomains.txt")"

# Run EyeWitness for screenshots
echo "[+] Taking screenshots with EyeWitness..."
eyewitness -f "$BASE_DIR/live_subdomains.txt" --web -d "$BASE_DIR/screenshots" > /dev/null 2>&1

echo "[+] Reconnaissance completed!"
echo "Results stored in: $BASE_DIR"
