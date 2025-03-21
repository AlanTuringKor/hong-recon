# Hong Recon Tools

This repository contains two scripts designed for domain reconnaissance:

1. **hong_recon.sh**: A Bash script that automates the discovery and analysis of subdomains associated with a given domain.
2. **hong_recon2.py**: A Python script that performs in-depth security assessments on identified subdomains, including DNS takeover checks, port scanning, and web vulnerability analysis.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Running `hong_recon.sh`](#running-hong_reconsh)
  - [Running `hong_recon2.py`](#running-hong_recon2py)
- [Output](#output)
- [Disclaimer](#disclaimer)

## Overview

The **`hong_recon.sh`** script initiates the reconnaissance process by:

- Identifying subdomains using tools like Sublist3r and Subfinder.
- Gathering URLs with gau (GetAllURLs).
- Analyzing the collected URLs to extract subdomains, subdirectories, and parameters.
- Checking the availability of discovered subdomains using httpx.
- Capturing screenshots of live subdomains with EyeWitness.

The **`hong_recon2.py`** script further assesses the security posture of the discovered subdomains by:

- Scanning for potential S3 bucket misconfigurations using S3Scanner.
- Detecting DNS takeover vulnerabilities with dnsrecon.
- Performing aggressive port scans using Nmap.
- Identifying web vulnerabilities through Wapiti scans.

## Prerequisites

Ensure the following tools are installed and accessible in your system's PATH:

- **Sublist3r**
- **Subfinder**
- **gau**
- **httpx**
- **EyeWitness**
- **S3Scanner**
- **dnsrecon**
- **Nmap**
- **Wapiti**

Additionally, Python 3.x is required to run `hong_recon2.py`.

## Usage

### Running `hong_recon.sh`

1. Ensure the script has execute permissions:

   ```bash
   chmod +x hong_recon.sh
   ```

2. Execute the script with the target domain:

   ```bash
   ./hong_recon.sh <domain> [-d directory]
   ```

   - `<domain>`: The target domain for reconnaissance.
   - `-d directory`: (Optional) Specify a custom directory to store results. If not provided, a default directory named `<domain>_recon` will be created in the current working directory.

   Example:

   ```bash
   ./hong_recon.sh example.com -d /path/to/results
   ```

   This command will perform reconnaissance on `example.com` and store the results in `/path/to/results`.

### Running `hong_recon2.py`

1. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute the script with the necessary arguments:

   ```bash
   python3 hong_recon2.py [-s subdomains.txt] [-o output.log] [-r report.txt]
   ```

   - `-s subdomains.txt`: File containing a list of subdomains to test (default: `subdomains.txt`).
   - `-o output.log`: Log output file (default: `hong_recon2_results.log`).
   - `-r report.txt`: Report output file (default: `pentest_report.txt`).

   Example:

   ```bash
   python3 hong_recon2.py -s live_subdomains.txt -o pentest.log -r final_report.txt
   ```

   This command will perform penetration testing on the subdomains listed in `live_subdomains.txt`, log the detailed output to `pentest.log`, and generate a summary report in `final_report.txt`.

## Output

- **`hong_recon.sh`**:

  - `sublist3r.txt`: Subdomains discovered by Sublist3r.
  - `subfinder.txt`: Subdomains discovered by Subfinder.
  - `gau.txt`: URLs gathered by gau.
  - `gau_analysis.txt`: Analysis of URLs, including subdomains, subdirectories, and parameters.
  - `all_subdomains.txt`: Combined list of unique subdomains.
  - `live_subdomains.txt`: List of live subdomains confirmed by httpx.
  - `screenshots/`: Directory containing screenshots of live subdomains captured by EyeWitness.

- **`hong_recon2.py`**:

  - `hong_recon2_results.log`: Detailed log of the penetration testing process.
  - `pentest_report.txt`: Summary report of findings, including potential vulnerabilities and recommendations.

## Disclaimer

These scripts are intended for educational and authorized testing purposes only. Unauthorized use against systems without explicit permission is illegal and unethical. Always obtain proper authorization before conducting any security assessments.

---

*Note: This README is inspired by best practices for documenting Python projects.* citeturn0search2 
