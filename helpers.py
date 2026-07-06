# helpers.py
import pandas as pd

def v(r, key, fallback="—"):
    val = r.get(key, "")
    s = str(val).strip()
    return s if s and s not in ("nan", "None", "") else fallback

def day_hours(r, day):
    return v(r, f"_{day}_hours", "Closed")

def fmt_gscore(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    try:
        return f"{float(val):.2f}"
    except Exception:
        return "—"

def threat_badge(t, is_us=False):
    if is_us:
        return '<span class="badge bus">Our Clinic</span>'
    if t is None or (isinstance(t, float) and pd.isna(t)):
        return '<span class="badge bna">Unknown</span>'
    try:
        ti = int(float(t))
    except Exception:
        return '<span class="badge bna">Unknown</span>'
    # Emojis removed for cleaner UI
    labels = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"}
    return f'<span class="badge b{ti}">{labels.get(ti, str(ti))}</span>'

def flag_badge(r):
    f = v(r, "Top_Threat_Flag")
    if f not in ("Normal", "—"):
        return f'<span class="badge" style="background:#FFF7ED;color:#C2410C;border:1px solid #FED7AA;">⚑ {f}</span>'
    return ""

def tags_html(text, sb=False):
    if not text or text == "—":
        return '<span style="color:#94A3B8;font-size:12px;">No data</span>'
    items = [x.strip() for x in text.replace(";", ",").split(",") if x.strip()]
    cls = "sb-tag" if sb else "tag"
    return "".join(f'<span class="{cls}">{i}</span>' for i in items)

def star_bar(rating, color="#2563EB"):
    try:
        pct = (float(rating) / 5) * 100
        return (
            f'<div class="rb-wrap"><div class="rb-row">'
            f'<div class="rb-lbl">Google</div>'
            f'<div class="rb-bg"><div class="rb-fill" style="width:{pct:.1f}%;background:{color};"></div></div>'
            f'<div class="rb-val">{rating}</div></div></div>'
        )
    except Exception:
        return ""

def generate_insights(r, comp_df):
    ins = []
    try:
        rat = float(r["_rating"]) if pd.notna(r["_rating"]) else None
        if rat:
            avg = comp_df["_rating"].mean()
            diff = rat - avg
            ins.append(f"⭐ Rated {rat:.1f} — {'above' if diff > 0 else 'below'} competitor avg ({avg:.1f}) by {abs(diff):.2f} pts.")
    except Exception:
        pass
    try:
        gs = float(r["_google_score"]) if pd.notna(r["_google_score"]) else None
        if gs is not None and comp_df["_google_score"].notna().any():
            avg_gs = comp_df["_google_score"].mean()
            diff_gs = gs - avg_gs
            ins.append(f"📊 Google Score {gs:.2f} — {'above' if diff_gs >= 0 else 'below'} competitor avg ({avg_gs:.2f}) by {abs(diff_gs):.2f}.")
    except Exception:
        pass
    area = r.get("Neighborhood / Area", "")
    if area:
        n = len(comp_df[comp_df["Neighborhood / Area"] == area])
        if n:
            ins.append(f"📍 {n} competitor(s) in same neighborhood ({area}).")
    try:
        t = int(float(r["_threat"])) if pd.notna(r["_threat"]) else None
        if t:
            desc = {1: "Minimal", 2: "Low", 3: "Medium", 4: "High — watch closely", 5: "Critical — top priority"}
            ins.append(f"🎯 Threat level {t}/5: {desc.get(t, '')}")
    except Exception:
        pass
    if v(r, "Top_Threat_Flag") not in ("Normal", "—"):
        ins.append(f"⚑ Flagged: {v(r, 'Top_Threat_Flag')}")
    if v(r, "Weekend_Advantage") not in ("No", "—"):
        ins.append(f"📅 Weekend Advantage: {v(r, 'Weekend_Advantage')}")
    nearest = v(r, "Nearest_PT_of_The_City")
    dist = v(r, "Distance_to_Nearest_PTotC_miles")
    if nearest != "—":
        ins.append(f"🏥 Nearest PT of the City: {nearest} ({dist} mi away).")
    return ins

def apply_filters(df_in, search_q, f_area, f_threat, f_ins, show_us, sort_by):
    fdf = df_in.copy()
    if search_q:
        fdf = fdf[
            fdf["Clinic Name"].str.contains(search_q, case=False, na=False) |
            fdf["Neighborhood / Area"].str.contains(search_q, case=False, na=False)
        ]
    if f_area != "All Areas":
        fdf = fdf[fdf["Neighborhood / Area"] == f_area]
    if f_threat != "All Threats":
        try:
            fdf = fdf[fdf["_threat"] == float(f_threat[0])]
        except Exception:
            pass
    if f_ins != "All Insurances":
        fdf = fdf[fdf["_insurance"].str.contains(f_ins, case=False, na=False, regex=False)]
    if show_us:
        fdf = fdf[fdf["_is_us"]]
    if sort_by == "Sort: Threat ↓":
        fdf = fdf.sort_values("_threat", ascending=False, na_position="last")
    elif sort_by == "Sort: Rating ↓":
        fdf = fdf.sort_values("_rating", ascending=False, na_position="last")
    elif sort_by == "Sort: Reviews ↓":
        fdf = fdf.sort_values("_reviews", ascending=False, na_position="last")
    elif sort_by == "Sort: Score ↓":
        fdf = fdf.sort_values("_google_score", ascending=False, na_position="last")
    else:
        fdf = fdf.sort_values("Clinic Name", ascending=True, na_position="last")
    return fdf