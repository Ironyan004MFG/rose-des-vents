#!/usr/bin/env python3
"""Administration des quêtes de la Rose des Vents par le compte robot de Claude.

Le robot se connecte comme un utilisateur ordinaire : les règles Firestore s'appliquent
(il ne peut faire que ce qu'un admin peut faire sur le site). Aucun secret dans ce fichier :
le mot de passe est lu dans la variable d'environnement RDV_PASSWORD.

Exemples :
  RDV_PASSWORD=... python3 tools/rdv_admin.py list quetes
  RDV_PASSWORD=... python3 tools/rdv_admin.py get quetes/wa1
  RDV_PASSWORD=... python3 tools/rdv_admin.py set quetes/ne4 '{"bureau":"neverwinter","titre":"...","rang":"fer","statut":"ouverte"}'
  RDV_PASSWORD=... python3 tools/rdv_admin.py update quetes/lu2 '{"statut":"terminee"}'
  RDV_PASSWORD=... python3 tools/rdv_admin.py delete quetes/ne4 --oui
  RDV_PASSWORD=... python3 tools/rdv_admin.py export > sauvegarde.json
"""
import json, os, sys, urllib.request, urllib.error, datetime

API_KEY = "AIzaSyBd6DdnvzkmPxGB_aAjAgTc1P9jHAztI30"
PROJECT = "rose-des-vents-d98df"
EMAIL = os.environ.get("RDV_EMAIL", "claude@rose-des-vents.local")
EMU = os.environ.get("RDV_EMU")  # tests locaux seulement, ex. RDV_EMU=1
if EMU: PROJECT = "demo-rdv"
BASE = (f"http://127.0.0.1:8085/v1/projects/{PROJECT}/databases/(default)/documents" if EMU
        else f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents")
AUTH = "http://127.0.0.1:9099/identitytoolkit.googleapis.com" if EMU else "https://identitytoolkit.googleapis.com"

def http(method, url, body=None, token=None):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            t = r.read().decode(); return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Erreur {e.code} : {e.read().decode()[:400]}")

def login():
    pw = os.environ.get("RDV_PASSWORD") or sys.exit("RDV_PASSWORD manquant.")
    r = http("POST", f"{AUTH}/v1/accounts:signInWithPassword?key={API_KEY}",
             {"email": EMAIL, "password": pw, "returnSecureToken": True})
    return r["idToken"]

def enc(v):
    if v is None: return {"nullValue": None}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, list): return {"arrayValue": {"values": [enc(x) for x in v]}}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: enc(x) for k, x in v.items()}}}
    raise TypeError(type(v))

def dec(v):
    k, x = next(iter(v.items()))
    if k == "integerValue": return int(x)
    if k == "arrayValue": return [dec(y) for y in x.get("values", [])]
    if k == "mapValue": return {a: dec(b) for a, b in x.get("fields", {}).items()}
    if k == "nullValue": return None
    return x

def docjson(d):
    out = {"id": d["name"].split("/")[-1]}
    out.update({k: dec(v) for k, v in d.get("fields", {}).items()})
    return out

def now_ts():
    return {"timestampValue": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}

def list_coll(tok, coll):
    docs, page = [], ""
    while True:
        r = http("GET", f"{BASE}/{coll}?pageSize=300" + (f"&pageToken={page}" if page else ""), token=tok)
        docs += [docjson(d) for d in r.get("documents", [])]
        page = r.get("nextPageToken")
        if not page: return docs

def write(tok, path, data, mask=None):
    fields = {k: enc(v) for k, v in data.items()}
    if path.startswith("quetes/") or path.startswith("inscriptions/"):
        fields["majLe"] = now_ts()
        if mask is None and "creeLe" not in fields: fields["creeLe"] = now_ts()
    q = "".join(f"&updateMask.fieldPaths={k}" for k in (list(mask) + ["majLe"] if mask is not None else [])) if mask is not None else ""
    return http("PATCH", f"{BASE}/{path}?{q.lstrip('&')}", {"fields": fields}, tok)

def main(a):
    if not a: sys.exit(__doc__)
    cmd, tok = a[0], login()
    if cmd == "list":
        print(json.dumps(list_coll(tok, a[1]), ensure_ascii=False, indent=2))
    elif cmd == "get":
        print(json.dumps(docjson(http("GET", f"{BASE}/{a[1]}", token=tok)), ensure_ascii=False, indent=2))
    elif cmd == "set":
        data = json.loads(a[2])
        print(json.dumps(docjson(write(tok, a[1], data)), ensure_ascii=False, indent=2))
    elif cmd == "update":
        data = json.loads(a[2])
        print(json.dumps(docjson(write(tok, a[1], data, mask=data.keys())), ensure_ascii=False, indent=2))
    elif cmd == "delete":
        if "--oui" not in a: sys.exit("Suppression non confirmée : ajoute --oui.")
        http("DELETE", f"{BASE}/{a[1]}", token=tok); print("Supprimé :", a[1])
    elif cmd == "export":
        print(json.dumps({c: list_coll(tok, c) for c in ["bureaux", "quetes", "inscriptions", "aventuriers", "config"]}, ensure_ascii=False, indent=2))
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
