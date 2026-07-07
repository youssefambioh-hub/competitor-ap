# data_loader.py
import os
import pandas as pd
import snowflake.connector
import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import config

def _load_private_key() -> bytes:
    # 1. Check if we are in production (Railway Environment Variable)
    pem_env = os.environ.get("SNOWFLAKE_PRIVATE_KEY")
    
    if pem_env:
        # Railway might pass newlines as literal '\n', so we fix them and encode to bytes
        pem_data = pem_env.replace("\\n", "\n").encode("utf-8")
    else:
        # 2. Fallback to local file path for local development
        with open(config.PRIVATE_KEY_PATH, "rb") as f:
            pem_data = f.read()

    private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())
    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
    return private_key.private_bytes(
        encoding=Encoding.DER,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

def _combine_hours(open_val, close_val) -> str:
    o = str(open_val).strip()
    c = str(close_val).strip()
    closed_tokens = {"", "nan", "none", "closed", "n/a", "-"}
    if o.lower() in closed_tokens and c.lower() in closed_tokens:
        return "Closed"
    if o.lower() in closed_tokens:
        return c
    if c.lower() in closed_tokens:
        return o
    return f"{o} – {c}"

@st.cache_data(show_spinner="Loading clinic data…", ttl=300)
def load_data():
    pkb = _load_private_key()
    
    # Using 'with' forces the connection to fully close and clear immediately after getting data
    with snowflake.connector.connect(
        user=config.SF_USER,
        account=config.SF_ACCOUNT,
        warehouse=config.SF_WAREHOUSE,
        database=config.SF_DATABASE,
        schema=config.SF_SCHEMA,
        role=config.SF_ROLE,
        private_key=pkb,
    ) as conn:
        query = f'SELECT * FROM "{config.SF_DATABASE}"."{config.SF_SCHEMA}"."{config.SF_TABLE}"'
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

    # At this point, the connection to Snowflake is 100% closed safely.
    df = pd.DataFrame(rows, columns=columns).fillna("")
    df = df.rename(columns=config.SF_COL_RENAMES)

    def to_float(v):
        try:
            return float(str(v).replace(",", ""))
        except Exception:
            return None

    df["_rating"] = df["Google Rating"].apply(to_float)
    df["_reviews"] = df["# Reviews"].apply(to_float)
    df["_threat"] = df["Competitive_Threat_1to5"].apply(to_float)
    df["_google_score"] = df["Google Score"].apply(to_float)
    df["Latitude"] = df["Latitude"].apply(to_float)
    df["Longitude"] = df["Longitude"].apply(to_float)
    df["_is_us"] = df["Is PT of The City?"].str.strip().str.lower().isin(["yes", "y", "true", "1"])

    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        open_col = f"{day} Hours"
        close_col = f"{day} Close"
        combo_col = f"_{day}_hours"
        if open_col in df.columns and close_col in df.columns:
            df[combo_col] = df.apply(lambda r, oc=open_col, cc=close_col: _combine_hours(r[oc], r[cc]), axis=1)
        elif open_col in df.columns:
            df[combo_col] = df[open_col]
        else:
            df[combo_col] = ""

    df["_insurance"] = df["Insurances_Accepted_Clean"]
    return df