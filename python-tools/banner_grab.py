#!/usr/bin/env python3
# banner_grab.py
import socket
import argparse

def grab(target, port, timeout=2.0, recv_bytes=2048):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((target, port))
        try:
            data = s.recv(recv_bytes)
            return data.decode(errors='ignore').strip()
        except Exception:
            return ""
    except Exception as e:
        return f"<connect error: {e}>"
    finally:
        try:
            s.close()
        except:
            pass

def main():
    p = argparse.ArgumentParser(description="Simple banner grabber")
    p.add_argument("target", help="IP or hostname")
    p.add_argument("ports", nargs="+", type=int, help="Ports to test (1 or more)")
    p.add_argument("--timeout", type=float, default=2.0, help="Socket timeout (s)")
    args = p.parse_args()

    for port in args.ports:
        b = grab(args.target, port, timeout=args.timeout)
        print(f"[{args.target}:{port}] -> {b}")

if __name__ == "__main__":
    main()
