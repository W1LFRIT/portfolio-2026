#!/usr/bin/env python3
"""
Port scanner simple, multithreadé.
Usage:
    py port-scanner.py target_or_ip start_port end_port --threads 100 --timeout 1.0 --output results.csv [--verbose]
"""
import socket
import sys
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from datetime import datetime

def scan_port(target, port, timeout):
    """
    Tente une connexion TCP. Retourne (port, is_open, banner).
    Ne fait pas d'affichage ici : on laisse le caller imprimer (thread-safe enough).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        res = s.connect_ex((target, port))
        if res == 0:
            try:
                banner = s.recv(1024).decode(errors='ignore').strip()
            except Exception:
                banner = ""
            s.close()
            return (port, True, banner)
        else:
            s.close()
            return (port, False, "")
    except Exception:
        # si erreur réseau ponctuelle, considérer comme fermé
        return (port, False, "")

def main():
    parser = argparse.ArgumentParser(description="Simple multithread port scanner")
    parser.add_argument("target", help="Target hostname or IP")
    parser.add_argument("start", type=int, help="Start port (inclusive)")
    parser.add_argument("end", type=int, help="End port (inclusive)")
    parser.add_argument("--threads", type=int, default=100, help="Number of threads")
    parser.add_argument("--timeout", type=float, default=0.8, help="Socket timeout seconds")
    parser.add_argument("--output", type=str, default="", help="CSV output file (optional)")
    parser.add_argument("--verbose", action="store_true", help="Show every port tested (open or closed)")
    args = parser.parse_args()

    target = args.target
    start = max(1, args.start)
    end = min(65535, args.end)
    timeout = args.timeout
    threads = max(1, min(1000, args.threads))
    verbose = args.verbose

    ports = list(range(start, end+1))
    open_ports = []

    print(f"[+] Scanning {target} ports {start}-{end} with {threads} threads, timeout {timeout}s")
    start_time = datetime.now()

    # soumettre toutes les tâches
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_port, target, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            port, is_open, banner = fut.result()
            if is_open:
                # affiche toujours les ports ouverts
                print(f"[OPEN] {port}\t{banner}")
                open_ports.append((port, banner))
            else:
                # n'affiche que si verbose activé
                if verbose:
                    print(f"[CLOSED] {port}")

    elapsed = datetime.now() - start_time
    print(f"[+] Done in {elapsed.total_seconds():.2f}s. {len(open_ports)} open ports found.")

    if args.output:
        try:
            with open(args.output, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["target", "scan_time", "port", "banner"])
                for port, banner in open_ports:
                    writer.writerow([target, start_time.isoformat(), port, banner])
            print(f"[+] Results saved to {args.output}")
        except Exception as e:
            print(f"[-] Failed to write CSV: {e}")

if __name__ == "__main__":
    main()
