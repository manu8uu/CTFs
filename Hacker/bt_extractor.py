#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

DEFAULT_MAC = "MAC" //Poner la MAC que toca
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(BASE_DIR, "extraccion")
os.makedirs(WORK_DIR, exist_ok=True)


def run_cmd(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return p.returncode, (p.stdout + "\n" + p.stderr).strip()
    except Exception as e:
        return 1, str(e)


def list_obex_sessions():
    """Localiza los paths de sesión bajo /org/bluez/obex/client/ y sus interfaces."""
    rc, out = run_cmd(["busctl", "--user", "tree", "org.bluez.obex"])
    sessions = []
    if rc != 0:
        return sessions

    for line in out.splitlines():
        m = re.search(r"(/org/bluez/obex/client/session\d+)", line)
        if m:
            path = m.group(1)
            _, intro = run_cmd(["busctl", "--user", "introspect", "org.bluez.obex", path])
            sessions.append({
                "path": path,
                "has_pbap": "org.bluez.obex.PhonebookAccess1" in intro,
                "has_map": "org.bluez.obex.MessageAccess1" in intro,
            })
    return sessions


def parse_vcf_entries(vcf_path):
    entries = []
    if not os.path.isfile(vcf_path) or os.path.getsize(vcf_path) == 0:
        return entries

    unfolded = []
    with open(vcf_path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            if line.startswith((" ", "\t")) and unfolded:
                unfolded[-1] += line[1:]
            else:
                unfolded.append(line)

    cur = None
    for line in unfolded:
        up = line.upper()
        if up.startswith("BEGIN:VCARD"):
            cur = {"fn": "", "phones": [], "dt": "", "extra": []}
        elif up.startswith("FN") and ":" in line and cur is not None:
            cur["fn"] = line.split(":", 1)[1].strip()
        elif up.startswith("TEL") and ":" in line and cur is not None:
            num = line.split(":", 1)[1].strip()
            if num and num not in cur["phones"]:
                cur["phones"].append(num)
        elif up.startswith("X-IRMC-CALL-DATETIME") and ":" in line and cur is not None:
            cur["dt"] = line.split(":", 1)[1].strip()
        elif up.startswith("X-") and ":" in line and cur is not None:
            cur["extra"].append(line.strip())
        elif up.startswith("END:VCARD") and cur is not None:
            if cur["fn"] or cur["phones"] or cur["dt"] or cur["extra"]:
                entries.append(cur)
            cur = None
    return entries


def extract_pbap(session_path):
    folders = ["pb", "ich", "och", "mch", "cch"]
    data = {}
    for folder in folders:
        vcf_file = os.path.join(WORK_DIR, f"{folder}.vcf")
        if os.path.exists(vcf_file):
            os.remove(vcf_file)

        rc_sel, out_sel = run_cmd([
            "busctl", "--user", "call", "org.bluez.obex", session_path,
            "org.bluez.obex.PhonebookAccess1", "Select", "ss", "int", folder
        ])
        if rc_sel != 0:
            data[folder] = {"error": out_sel, "count": 0, "items": []}
            continue

        _, out_size = run_cmd([
            "busctl", "--user", "call", "org.bluez.obex", session_path,
            "org.bluez.obex.PhonebookAccess1", "GetSize"
        ])

        rc_pull, out_pull = run_cmd([
            "busctl", "--user", "call", "org.bluez.obex", session_path,
            "org.bluez.obex.PhonebookAccess1", "PullAll", "sa{sv}", vcf_file, "0"
        ], timeout=40)
        time.sleep(1.5)

        items = parse_vcf_entries(vcf_file)
        data[folder] = {
            "select_ok": rc_sel == 0,
            "pull_ok": rc_pull == 0,
            "size_raw": out_size,
            "pull_raw": out_pull,
            "count": len(items),
            "items": items,
        }
    return data


def extract_map(session_path):
    rc, out = run_cmd([
        "busctl", "--user", "call", "org.bluez.obex", session_path,
        "org.bluez.obex.MessageAccess1", "ListMessages", "sa{sv}", "", "0"
    ], timeout=25)
    return {
        "rc": rc,
        "raw_output": out,
    }


def main():
    mac = sys.argv[1].strip() if len(sys.argv) > 1 else DEFAULT_MAC
    _, bt_info = run_cmd(["bluetoothctl", "info", mac])
    sessions = list_obex_sessions()

    pbap_results = {}
    map_results = []

    for s in sessions:
        if s["has_pbap"]:
            print(f"[+] Extrayendo PBAP desde {s['path']}...")
            pbap_results[s["path"]] = extract_pbap(s["path"])
        if s["has_map"]:
            print(f"[+] Consultando MAP desde {s['path']}...")
            map_results.append({
                "session": s["path"],
                "data": extract_map(s["path"]),
            })

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "target_mac": mac,
        "connected": "Connected: yes" in bt_info,
        "sessions_found": sessions,
        "pbap": pbap_results,
        "map": map_results,
    }

    out_json = os.path.join(WORK_DIR, "resumen_bt.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Guardado en {out_json}")
    print(f"Sesiones OBEX detectadas: {len(sessions)}")
    for s in sessions:
        print(f"  - {s['path']} | PBAP={s['has_pbap']} | MAP={s['has_map']}")
    for spath, pdata in pbap_results.items():
        for fname, fval in pdata.items():
            print(f"  - {spath} [{fname}]: {fval.get('count', 0)} registros")


if __name__ == "__main__":
    main()
