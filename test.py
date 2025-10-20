#!/usr/bin/env python3
import csv
import ast
from pathlib import Path

OLD_CSV = "old_data.csv"
FILTERED_CSV = "FilteredData.csv"
OUT_CSV = "merged_data.csv"

def normalize_ip_list(ip_str):
    if not ip_str or ip_str == "[]":
        return ""
    try:
        ips = ast.literal_eval(ip_str)
        if isinstance(ips, list):
            return ", ".join(ip.replace(",", ".") for ip in ips)
    except Exception:
        pass
    return ip_str.replace(",", ".").strip()

def guess_columns(fieldnames):
    host_col = None
    ip_col = None
    env_col = None
    for fn in fieldnames:
        fl = fn.lower()
        if "host name" in fl:
            host_col = fn
        elif "host ip" in fl:
            ip_col = fn
        elif "environment" in fl:
            env_col = fn
    return host_col, ip_col, env_col

def main():
    if not Path(OLD_CSV).exists() or not Path(FILTERED_CSV).exists():
        print("Falta um dos arquivos: old_data.csv ou FilteredData.csv")
        return

    with open(FILTERED_CSV, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        filtered_data = {}
        for row in reader:
            name = row["MachineName"].strip()
            ips = normalize_ip_list(row["IPs"].strip())
            env = row.get("env", "").strip()
            filtered_data[name.lower()] = {"IPs": ips, "env": env}

    updated_rows = []
    processed = set()

    with open(OLD_CSV, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames.copy()
        host_col, ip_col, env_col = guess_columns(fieldnames)
        if "ALTEROU" not in fieldnames:
            fieldnames.append("ALTEROU")

        for row in reader:
            host = row[host_col].strip()
            lower = host.lower()
            if lower not in filtered_data:
                continue
            new_entry = filtered_data[lower]
            new_ip = new_entry["IPs"]
            old_ip = row[ip_col].strip()
            if old_ip != new_ip:
                row[ip_col] = new_ip
                row["ALTEROU"] = "1"
            else:
                row["ALTEROU"] = "0"
            if env_col:
                row[env_col] = new_entry.get("env", row.get(env_col, ""))
            updated_rows.append(row)
            processed.add(lower)

    for name, info in filtered_data.items():
        if name not in processed:
            new_row = {fn: "" for fn in fieldnames}
            new_row[host_col] = name.upper()
            new_row[ip_col] = info["IPs"]
            if env_col:
                new_row[env_col] = info["env"]
            new_row["ALTEROU"] = "NOVO"
            updated_rows.append(new_row)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"[+] Gerado '{OUT_CSV}' com {len(updated_rows)} linhas atualizadas e novas.")

if __name__ == "__main__":
    main()
