#!/usr/bin/env python3
import csv
from pathlib import Path

OLD_CSV = "old_data.csv"
NEW_CSV = "new_data.csv"
OUT_CSV = "merged_data.csv"

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
    if not Path(OLD_CSV).exists() or not Path(NEW_CSV).exists():
        print("Falta um dos arquivos: old_data.csv ou new_data.csv")
        return

    with open(NEW_CSV, newline="", encoding="utf-8", errors="ignore") as f:
        new_reader = csv.DictReader(f, delimiter=";")
        new_data = {}
        for row in new_reader:
            name = row["MachineName"].strip()
            ips = row["IPs"].strip()
            env = row.get("env", "").strip()
            new_data[name.lower()] = {"IPs": ips, "env": env}

    updated_rows = []

    with open(OLD_CSV, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames.copy()
        host_col, ip_col, env_col = guess_columns(fieldnames)
        if not host_col or not ip_col:
            print("Não encontrei colunas 'Host name' e 'Host IP' no CSV antigo.")
            print("Colunas:", fieldnames)
            return
        if "ALTEROU" not in fieldnames:
            fieldnames.append("ALTEROU")

        processed_hosts = set()

        for row in reader:
            host = row[host_col].strip()
            host_lower = host.lower()
            if host_lower not in new_data:
                continue
            new_entry = new_data[host_lower]
            old_ip = row[ip_col].strip()
            new_ip = new_entry["IPs"]
            if old_ip != new_ip:
                row[ip_col] = new_ip
                row["ALTEROU"] = "1"
            else:
                row["ALTEROU"] = "0"
            if env_col:
                row[env_col] = new_entry.get("env", row.get(env_col, ""))
            updated_rows.append(row)
            processed_hosts.add(host_lower)

        for name, info in new_data.items():
            if name not in processed_hosts:
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

    print(f"[+] Gerado '{OUT_CSV}' com {len(updated_rows)} linhas (atualizadas e novas).")

if __name__ == "__main__":
    main()
