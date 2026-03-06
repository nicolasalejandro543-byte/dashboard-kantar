"""
Dashboard Kantar - Center Zone KPIs
Coca-Cola Corporate Dashboard
"""
import os
import json
import math
import pandas as pd
from flask import Flask, Response, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)


def clean_for_json(obj):
    """Recursively replace NaN/Inf with None for valid JSON."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    return obj


def json_response(data):
    """Return a valid JSON response with NaN handled."""
    cleaned = clean_for_json(data)
    return Response(json.dumps(cleaned, ensure_ascii=False), mimetype='application/json')


def load_data():
    """Load and clean all CSV data."""
    dfs = {}
    files = {
        "kpis": "base_plana_kpis.csv",
        "incidence": "base_plana_incidence.csv",
        "channels": "base_plana_channels.csv",
        "incidence_sub": "base_plana_incidence_subcategorias.csv",
        "channels_detail": "base_plana_channels_detalle.csv",
    }
    for key, fname in files.items():
        path = os.path.join(BASE_DIR, fname)
        if os.path.exists(path):
            df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
            if "Variacion_vs_PY" in df.columns:
                df["Variacion_vs_PY"] = pd.to_numeric(df["Variacion_vs_PY"], errors="coerce")
            dfs[key] = df
    return dfs


DATA = load_data()


def df_to_records(df):
    """Convert DataFrame to list of dicts with NaN -> None."""
    records = df.to_dict(orient="records")
    for rec in records:
        for k, v in rec.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                rec[k] = None
    return records


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "dashboard.html")


@app.route("/api/filters")
def api_filters():
    df = DATA.get("kpis", pd.DataFrame())
    if df.empty:
        return json_response({})
    return json_response({
        "paises": sorted(df["Pais"].dropna().unique().tolist()),
        "categorias": sorted(df["Categoria"].dropna().unique().tolist()),
        "kpis": sorted(df["KPI"].dropna().unique().tolist()),
        "canales": sorted(df["Canal"].dropna().unique().tolist()),
        "periodos": sorted(df["Periodo"].dropna().unique().tolist()),
    })


@app.route("/api/kpis")
def api_kpis():
    df = DATA.get("kpis", pd.DataFrame())
    if df.empty:
        return json_response([])
    return json_response(df_to_records(df))


@app.route("/api/incidence")
def api_incidence():
    df = DATA.get("incidence", pd.DataFrame())
    if df.empty:
        return json_response([])
    return json_response(df_to_records(df))


@app.route("/api/channels")
def api_channels():
    df = DATA.get("channels", pd.DataFrame())
    if df.empty:
        return json_response([])
    return json_response(df_to_records(df))


@app.route("/api/incidence_sub")
def api_incidence_sub():
    df = DATA.get("incidence_sub", pd.DataFrame())
    if df.empty:
        return json_response([])
    return json_response(df_to_records(df))


@app.route("/api/channels_detail")
def api_channels_detail():
    df = DATA.get("channels_detail", pd.DataFrame())
    if df.empty:
        return json_response([])
    return json_response(df_to_records(df))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 60)
    print("  KANTAR CENTER ZONE DASHBOARD")
    print(f"  http://localhost:{port}")
    print("=" * 60 + "\n")
    app.run(debug=False, port=port, host="0.0.0.0")
