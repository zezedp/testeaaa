#!/usr/bin/env python3
import csv
import ast

csv_file = "ntnxCap.csv"

def parse_ips_field(s):
    if not s:
        return ""
    s = s.strip()
    if s in ("", "[]"):
        return ""
    try:
        val = ast.literal_eval(s)
        if isinstance(val, (list, tuple)):
            return ", ".join(ip.replace(",", ".").strip() for ip in val)
    except Exception:
        pass
    s2 = s.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    parts = [p.strip().replace(",", ".") for p in s2.split() if p.strip()]
    return ", ".join(parts)

with open(csv_file, encoding="utf-8") as f:
    # detectar delimitador ( ; ou , )
    sample = f.read(2048)
    f.seek(0)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,")
    except Exception:
        dialect = csv.get_dialect("excel")
        dialect.delimiter = ";"

    reader = csv.DictReader(f, dialect=dialect)

    # encontrar nomes corretos de colunas
    fnames = {name.lower(): name for name in reader.fieldnames}
    col_machine = fnames.get("machinename")
    col_ips = fnames.get("ips")
    col_env = fnames.get("env") or fnames.get("environment")

    if not col_machine:
        print("❌ Coluna 'MachineName' não encontrada.")
        exit(1)

    found = False
    for row in reader:
        name = (row.get(col_machine) or "").strip()
        if "gold" in name.lower():
            ips = parse_ips_field(row.get(col_ips, ""))
            env = (row.get(col_env, "") or "").strip()
            print(f"{name} | {ips} | {env}")
            found = True

    if not found:
        print("⚠️ Nenhum MachineName contendo 'GOLD' encontrado.")
