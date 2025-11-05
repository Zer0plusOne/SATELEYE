from flask import Flask, render_template, jsonify, request
import requests, pandas as pd, json, os, time, re, io
from urllib.parse import unquote
from datetime import datetime

app = Flask(__name__)
PORT = 1610

UCS_CSV = "ucs_satellites.csv"
USAGE_FILE = "usage.json"

DEFAULT_LIMITS = {
    "verb_limit": 1000,
    "positions": 1000,
    "visualpasses": 100,
    "radiopasses": 100,
    "above": 100,
}

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"count": 0, "last_reset": time.time()}

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

usage = load_usage()

def increment_usage():
    global usage
    usage["count"] += 1
    if time.time() - usage.get("last_reset", 0) > 30 * 24 * 3600:
        usage = {"count": 1, "last_reset": time.time()}
    save_usage(usage)

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

N2YO_KEY = CONFIG["n2yo_api_key"]
LAT, LNG, ALT = CONFIG["latitude"], CONFIG["longitude"], CONFIG["altitude"]

def fetch_ucs_from_office_viewer():
    """Descarga automáticamente el Excel UCS desde el visor Office (view.officeapps.live.com)."""
    viewer_url = (
        "https://view.officeapps.live.com/op/view.aspx?"
        "src=https%3A%2F%2Fwww.ucs.org%2Fsites%2Fdefault%2Ffiles%2F2024-01%2F"
        "UCS-Satellite-Database%25205-1-2023.xlsx&wdOrigin=BROWSELINK"
    )
    try:
        print("🛰️ Consultando visor Office de UCS...")
        r = requests.get(viewer_url, timeout=25, allow_redirects=True)

        match = re.search(r"src=(https[^&]+)", r.url)
        if not match:
            print("⚠️ No se pudo extraer el parámetro src del visor de Office.")
            return False

        real_url = unquote(match.group(1))
        if not real_url.endswith(".xlsx"):
            print(f"⚠️ URL extraída no parece un Excel: {real_url}")
            return False

        print(f"📡 Enlace Excel real detectado: {real_url}")
        r2 = requests.get(real_url, timeout=40)
        if r2.status_code != 200:
            print(f"❌ Error HTTP {r2.status_code} al descargar el Excel UCS.")
            return False

        df = pd.read_excel(io.BytesIO(r2.content))
        df.to_csv(UCS_CSV, index=False)
        print(f"✅ UCS descargada y convertida a CSV ({len(df)} registros).")
        return True

    except Exception as e:
        print(f"❌ Error al obtener Excel desde visor Office: {e}")
        return False


def ensure_ucs_database(force=False):
    """Verifica si existe y si tiene menos de 30 días; si no, la descarga."""
    if os.path.exists(UCS_CSV) and not force:
        age_days = (time.time() - os.path.getmtime(UCS_CSV)) / 86400
        if age_days < 30 and os.path.getsize(UCS_CSV) > 100000:
            print(f"✅ Base UCS actual detectada ({age_days:.1f} días de antigüedad).")
            return True
        else:
            print("♻️ Base UCS desactualizada, renovando...")
    return fetch_ucs_from_office_viewer()


ensure_ucs_database()

def load_sat_database():
    if not os.path.exists(UCS_CSV):
        print("⚠️ No se encontró ucs_satellites.csv.")
        return pd.DataFrame(), "none"

    try:
        df = pd.read_csv(UCS_CSV)
        df.columns = [c.strip().lower() for c in df.columns]
        print(f"📊 Cargado {UCS_CSV} con {len(df)} filas.")
        if any("country" in c for c in df.columns) and "purpose" in df.columns:
            print("✅ Modo enriquecido (UCS completo).")
            return df, "ucs"
        else:
            print("⚠️ Base sin columnas UCS; modo lite.")
            return df, "gp"
    except Exception as e:
        print(f"⚠️ No se pudo leer {UCS_CSV}: {e}")
        return pd.DataFrame(), "none"

satdb, satdb_mode = load_sat_database()

def get_ucs_info():
    """Devuelve estado y fecha de actualización de la base UCS."""
    if not os.path.exists(UCS_CSV):
        return {"status": "No encontrada", "date": "N/A", "mode": "none"}

    ts = os.path.getmtime(UCS_CSV)
    date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    age_days = (time.time() - ts) / 86400
    return {
        "status": "Activa" if satdb_mode == "ucs" else "Lite",
        "date": date,
        "age_days": round(age_days, 1),
        "mode": satdb_mode,
        "records": len(satdb) if not satdb.empty else 0,
    }

def normalize_text(value):
    if pd.isna(value):
        return None
    val = str(value).strip()
    if not val or val.lower() in ["nan", "none", "null"]:
        return None
    val = val.title()
    val = val.replace("Usa", "United States").replace("U.S.A.", "United States")
    val = val.replace("Prc", "China").replace("People'S Republic Of China", "China")
    return val

def get_satellites_above(radius=30):
    url = f"https://api.n2yo.com/rest/v1/satellite/above/{LAT}/{LNG}/{ALT}/{radius}/0/&apiKey={N2YO_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
    except Exception as e:
        return [{"error": f"Error al consultar N2YO: {e}"}]

    sats = data.get("above", [])
    if not sats:
        return [{"info": "No se detectaron satélites sobre tu zona."}]

    sats = sorted(sats, key=lambda s: s.get("satalt", 0))[:100]
    result = []

    if satdb_mode == "ucs" and not satdb.empty:
        cols = satdb.columns
        col_country = next((c for c in cols if "country" in c), None)
        col_purpose = next((c for c in cols if "purpose" in c), None)
        col_user = next((c for c in cols if "user" in c or "operator" in c), None)
        col_norad = next((c for c in cols if "norad" in c), None)

        for s in sats:
            entry = {
                "name": s["satname"],
                "norad": s["satid"],
                "lat": s["satlat"],
                "lng": s["satlng"],
                "alt": s["satalt"],
                "country": "Desconocido",
                "purpose": "N/A",
                "user": "N/A"
            }
            if col_norad:
                match = satdb[satdb[col_norad] == s["satid"]]
                if not match.empty:
                    row = match.iloc[0]
                    if col_country:
                        entry["country"] = normalize_text(row.get(col_country))
                    if col_purpose:
                        entry["purpose"] = normalize_text(row.get(col_purpose))
                    if col_user:
                        entry["user"] = normalize_text(row.get(col_user))
            result.append(entry)
        return result

    # Modo lite
    for s in sats:
        result.append({
            "name": s["satname"],
            "norad": s["satid"],
            "lat": s["satlat"],
            "lng": s["satlng"],
            "alt": s["satalt"],
            "country": "Desconocido",
            "purpose": "N/A",
            "user": "N/A"
        })
    return result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/satellites")
def api_satellites():
    radius = request.args.get("radius", 30, type=int)
    sats = get_satellites_above(radius)
    increment_usage()
    remaining = DEFAULT_LIMITS["verb_limit"] - usage["count"]

    info = get_ucs_info()

    return jsonify({
        "usage": {
            "count": usage["count"],
            "remaining": max(0, remaining),
            "limit": DEFAULT_LIMITS["verb_limit"]
        },
        "ucs_info": info,
        "satellites": sats
    })

@app.route("/api/update_ucs", methods=["POST"])
def api_update_ucs():
    """Fuerza actualización manual desde el panel web."""
    ok = ensure_ucs_database(force=True)
    global satdb, satdb_mode
    satdb, satdb_mode = load_sat_database()
    return jsonify({
        "success": ok,
        "ucs_info": get_ucs_info()
    })

if __name__ == "__main__":
    print(f"🌐 Servidor iniciado en http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
