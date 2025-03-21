#!/usr/bin/env python3

import subprocess
import os
import logging
import argparse
from multiprocessing import Pool
from datetime import datetime

def setup_logging(output_file):
    """Set up logging with the specified output file."""
    logging.basicConfig(filename=output_file, level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

def check_s3_buckets(subdomain_file):
    """Use S3Scanner to aggressively scan for S3 buckets."""
    if not os.path.exists(subdomain_file):
        logging.error(f"{subdomain_file} not found.")
        return
    
    logging.info("Scanning for S3 buckets with S3Scanner...")
    try:
        subprocess.run(['s3scanner', '-f', subdomain_file, '-e'], check=True)  # -e for extended checks
        logging.info("S3Scanner results logged to console or its default output")
    except subprocess.CalledProcessError as e:
        logging.error(f"S3Scanner failed: {e}")

def check_dns_takeover(subdomain):
    """Use dnsrecon for takeover detection."""
    logging.info(f"Checking DNS takeover for {subdomain} with dnsrecon...")
    try:
        result_dr = subprocess.run(['dnsrecon', '-d', subdomain, '-t', 'axfr'], 
                                  capture_output=True, text=True)  # AXFR for zone transfer
        if "Takeover" in result_dr.stdout or "AXFR" in result_dr.stdout:
            logging.warning(f"dnsrecon detected takeover or AXFR for {subdomain}: {result_dr.stdout}")
        else:
            logging.info(f"No takeover detected for {subdomain}")
    except subprocess.CalledProcessError as e:
        logging.error(f"DNS takeover check failed for {subdomain}: {e}")

def scan_ports(subdomain):
    """Use Nmap for aggressive port scanning."""
    logging.info(f"Scanning ports on {subdomain} with Nmap...")
    try:
        result = subprocess.run(['nmap', '-Pn', '-A', '-T4', subdomain], 
                               capture_output=True, text=True)  # -A for aggressive, -T4 for speed
        logging.info(f"Nmap results for {subdomain}:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Nmap failed for {subdomain}: {e}")
        return ""

def check_web_vulns(subdomain):
    """Use Wapiti to scan for web vulnerabilities."""
    for protocol in ['http', 'https']:
        url = f"{protocol}://{subdomain}"
        logging.info(f"Scanning {url} for vulnerabilities with Wapiti...")
        try:
            result = subprocess.run(['wapiti', '-u', url, '--flush-session', '-m', 'common'], 
                                   capture_output=True, text=True)
            logging.info(f"Wapiti results for {url}:\n{result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Wapiti failed for {url}: {e}")
            return ""

def process_subdomain(subdomain):
    """Process a single subdomain with all checks."""
    print(f"Processing {subdomain}...")
    logging.info(f"--- Processing {subdomain} ---")
    
    check_dns_takeover(subdomain)
    nmap_result = scan_ports(subdomain)
    wapiti_result = check_web_vulns(subdomain)
    
    return {
        'subdomain': subdomain,
        'ports': nmap_result,
        'web_vulns': wapiti_result
    }

def generate_report(results, report_file):
    """Generate a structured report from results."""
    with open(report_file, 'w') as f:
        f.write(f"Extreme Pentest Report - {datetime.now()}\n")
        f.write(f"Subdomains tested: {len(results)}\n\n")
        
        for result in results:
            f.write(f"Subdomain: {result['subdomain']}\n")
            f.write(f"Port Scan Results:\n{result['ports'] or 'N/A'}\n")
            f.write(f"Web Vulnerabilities:\n{result['web_vulns'] or 'N/A'}\n")
            f.write("-" * 50 + "\n")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extreme AWS subdomain pentesting script (no CloudFail)")
    parser.add_argument('-s', '--subdomains', default='subdomains.txt', 
                        help='File containing subdomains (default: subdomains.txt)')
    parser.add_argument('-o', '--output', default='extreme_pentest_results.log', 
                        help='Log output file (default: extreme_pentest_results.log)')
    parser.add_argument('-r', '--report', default='pentest_report.txt', 
                        help='Report output file (default: pentest_report.txt)')
    args = parser.parse_args()

    # Set up logging with the provided output file
    setup_logging(args.output)

    # Load subdomains
    if not os.path.exists(args.subdomains):
        logging.error(f"Subdomain file '{args.subdomains}' not found.")
        print(f"Error: '{args.subdomains}' not found.")
        return

    with open(args.subdomains, 'r') as f:
        subdomains = [line.strip() for line in f if line.strip()]

    if not subdomains:
        logging.error("No subdomains found in the file.")
        print("Error: No subdomains found in the file.")
        return

    print(f"Starting extreme pentest on {len(subdomains)} subdomains...")
    logging.info(f"Starting extreme pentest on {len(subdomains)} subdomains.")

    # Step 1: Run S3 bucket scan
    check_s3_buckets(args.subdomains)

    # Step 2: Process subdomains in parallel
    with Pool(processes=4) as pool:  # Adjust processes based on your CPU
        results = pool.map(process_subdomain, subdomains)

    # Step 3: Generate report
    generate_report(results, args.report)

    print(f"\nExtreme pentest complete. Check '{args.output}' for logs and '{args.report}' for summary.")
    logging.info("Extreme pentest completed.")

if __name__ == "__main__":
    main()
