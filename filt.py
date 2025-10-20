import csv

# Lê old_data.csv com separador ';'
with open("old_data.csv", newline='', encoding='utf-8') as f:
    old_data = list(csv.DictReader(f, delimiter=';'))

# Lê filtered_data normalmente (usa vírgula)
with open("FilteredData.csv", newline='', encoding='utf-8') as f:
    filtered = list(csv.DictReader(f))

old_map = {row["Host name"].strip().lower(): row for row in old_data}
merged = []

for new_row in filtered:
    name = new_row["MachineName"].strip()
    name_l = name.lower()
    ips = new_row["IPs"].strip()
    env = new_row["env"].strip()

    if name_l in old_map:
        old = old_map[name_l]
        if old["Host IP"].strip() != ips:
            old["Host IP"] = ips
            old["ALTEROU"] = "1"
        else:
            old["ALTEROU"] = "0"
        merged.append(old)
    else:
        merged.append({
            "Host name": name,
            "Host IP": ips,
            "Environment": env,
            "ALTEROU": "NOVO"
        })

with open("merged_data.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=merged[0].keys(),
        delimiter=';'
    )
    writer.writeheader()
    writer.writerows(merged)
