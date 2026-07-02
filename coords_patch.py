"""
coords_patch.py  —  Run once (or whenever) to extract lat/lng from Google Maps links
and write them into your file as new columns (Latitude, Longitude).

Usage:
    python coords_patch.py clinics.xlsx          # reads & writes same file
    python coords_patch.py clinics.csv clinics_with_coords.csv
"""

import re, sys, urllib.parse, urllib.request
import pandas as pd

GMAPS_RE = re.compile(
    r"@(-?\d+\.\d+),(-?\d+\.\d+)"       # e.g. @40.7580,-73.9855
    r"|"
    r"[?&]q=(-?\d+\.\d+)%2C(-?\d+\.\d+)"  # ?q=lat%2Clng
    r"|"
    r"[?&]ll=(-?\d+\.\d+),(-?\d+\.\d+)",   # ?ll=lat,lng
)

PLACE_SEARCH = re.compile(r"/maps/place/([^/]+)")   # /maps/place/Name/...

def extract_coords(url: str):
    """Return (lat, lng) floats or (None, None)."""
    if not url:
        return None, None
    m = GMAPS_RE.search(url)
    if m:
        groups = [g for g in m.groups() if g is not None]
        if len(groups) >= 2:
            return float(groups[0]), float(groups[1])
    return None, None


def process(src: str, dst: str = None):
    dst = dst or src
    if src.endswith(".csv"):
        df = pd.read_csv(src, dtype=str)
    else:
        df = pd.read_excel(src, dtype=str)

    df = df.fillna("")

    if "Latitude" not in df.columns:
        df["Latitude"] = ""
    if "Longitude" not in df.columns:
        df["Longitude"] = ""

    updated = 0
    for i, row in df.iterrows():
        if row.get("Latitude") and row.get("Longitude"):
            continue   # already have coords
        lat, lng = extract_coords(row.get("Google Maps Link", ""))
        if lat is not None:
            df.at[i, "Latitude"]  = str(lat)
            df.at[i, "Longitude"] = str(lng)
            updated += 1

    print(f"Extracted coordinates for {updated} clinics.")

    if dst.endswith(".csv"):
        df.to_csv(dst, index=False)
    else:
        df.to_excel(dst, index=False)

    print(f"Saved → {dst}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "clinics.xlsx"
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    process(src, dst)
