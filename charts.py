# charts.py
import plotly.graph_objects as go
import pandas as pd
from config import PL

def chart_threat_donut(df_in):
    tm = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"}
    counts = {}
    for _, row in df_in.iterrows():
        if row["_is_us"]:
            continue
        t = row["_threat"]
        key = tm.get(int(t), "Unknown") if pd.notna(t) and t is not None else "Unknown"
        counts[key] = counts.get(key, 0) + 1
    order = ["Critical", "High", "Medium", "Low", "Minimal", "Unknown"]
    colors = ["#DC2626", "#F59E0B", "#EAB308", "#60A5FA", "#10B981", "#CBD5E1"]
    labs = [l for l in order if l in counts]
    vals = [counts[l] for l in labs]
    cols = [colors[order.index(l)] for l in labs]
    fig = go.Figure(go.Pie(
        labels=labs, values=vals, hole=0.6,
        marker=dict(colors=cols, line=dict(color="#fff", width=2)),
        textinfo="label+percent", textfont_size=11,
        hovertemplate="<b>%{label}</b><br>%{value} clinics (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{sum(vals)}</b>", showarrow=False,
                       font=dict(size=22, color="#0F1E3D", family="Inter"), x=0.5, y=0.55)
    fig.add_annotation(text="Competitors", showarrow=False,
                       font=dict(size=10, color="#94A3B8", family="Inter"), x=0.5, y=0.42)
    fig.update_layout(**PL, showlegend=False, height=260)
    return fig

def chart_borough_breakdown(df_in):
    BM = {
        "brooklyn": "Brooklyn", "park slope": "Brooklyn", "williamsburg": "Brooklyn",
        "bushwick": "Brooklyn", "bed-stuy": "Brooklyn", "bedford": "Brooklyn",
        "greenpoint": "Brooklyn", "crown heights": "Brooklyn", "flatbush": "Brooklyn",
        "cobble hill": "Brooklyn", "boerum hill": "Brooklyn", "fort greene": "Brooklyn",
        "bay ridge": "Brooklyn", "sunset park": "Brooklyn", "prospect": "Brooklyn",
        "downtown brooklyn": "Brooklyn", "sheepshead": "Brooklyn", "brighton": "Brooklyn",
        "coney island": "Brooklyn", "canarsie": "Brooklyn", "borough park": "Brooklyn",
        "ditmas": "Brooklyn", "marine park": "Brooklyn", "midwood": "Brooklyn",
        "manhattan": "Manhattan", "midtown": "Manhattan", "chelsea": "Manhattan",
        "soho": "Manhattan", "tribeca": "Manhattan", "lower east": "Manhattan",
        "east village": "Manhattan", "west village": "Manhattan", "gramercy": "Manhattan",
        "flatiron": "Manhattan", "murray hill": "Manhattan", "kips bay": "Manhattan",
        "hell's kitchen": "Manhattan", "hells kitchen": "Manhattan",
        "upper east": "Upper Manhattan", "upper west": "Upper Manhattan",
        "harlem": "Upper Manhattan", "morningside": "Upper Manhattan",
        "washington heights": "Upper Manhattan", "inwood": "Upper Manhattan",
        "queens": "Queens", "astoria": "Queens", "long island city": "Queens",
        "flushing": "Queens", "jackson heights": "Queens", "forest hills": "Queens",
        "corona": "Queens", "elmhurst": "Queens", "woodside": "Queens",
        "sunnyside": "Queens", "rego park": "Queens", "jamaica": "Queens",
        "ridgewood": "Queens", "maspeth": "Queens", "bayside": "Queens",
        "bronx": "Bronx", "riverdale": "Bronx", "fordham": "Bronx", "pelham": "Bronx",
        "staten island": "Staten Island",
    }
    def to_boro(a):
        al = str(a).lower().strip()
        for k, b in BM.items():
            if k in al: return b
        return "Other"
    df2 = df_in.copy()
    df2["_boro"] = df2["Neighborhood / Area"].apply(to_boro)
    boros = ["Brooklyn", "Manhattan", "Upper Manhattan", "Queens", "Bronx", "Staten Island", "Other"]
    labs, us_c, co_c = [], [], []
    for b in boros:
        sub = df2[df2["_boro"] == b]
        if sub.empty: continue
        labs.append(b)
        us_c.append(int(sub["_is_us"].sum()))
        co_c.append(int((~sub["_is_us"]).sum()))
    if not labs: return None
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="PT of the City", x=labs, y=us_c, marker_color="#2563EB", marker_opacity=0.92,
        text=us_c, textposition="outside", textfont=dict(size=11, color="#2563EB"),
        hovertemplate="<b>%{x}</b><br>PT of the City: <b>%{y}</b><extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Competitors", x=labs, y=co_c,
        marker_color="#E2E8F0", marker_line_color="#94A3B8", marker_line_width=1,
        text=co_c, textposition="outside", textfont=dict(size=11, color="#64748B"),
        hovertemplate="<b>%{x}</b><br>Competitors: <b>%{y}</b><extra></extra>",
    ))
    fig.update_layout(
        **PL, barmode="group", height=260, bargap=0.22, bargroupgap=0.06,
        xaxis=dict(tickfont_size=11, showgrid=False),
        yaxis=dict(tickfont_size=10, gridcolor="#F1F5F9", zeroline=False),
        legend=dict(orientation="h", y=-0.25, font_size=11, bgcolor="rgba(0,0,0,0)"),
    )
    return fig

def chart_top20_reviews(df_in):
    comp = df_in[~df_in["_is_us"] & df_in["_reviews"].notna()].nlargest(20, "_reviews")
    threat_colors = {5: "#DC2626", 4: "#F59E0B", 3: "#EAB308", 2: "#60A5FA", 1: "#10B981"}
    colors = [threat_colors.get(int(r["_threat"]), "#CBD5E1") if pd.notna(r["_threat"]) else "#CBD5E1" for _, r in comp.iterrows()]
    
    fig = go.Figure(go.Bar(
        x=comp["_reviews"].tolist(), y=comp["Clinic Name"].tolist(), orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.4)", width=0.5)),
        text=[f"{int(r):,}" for r in comp["_reviews"].tolist()],
        textposition="outside", textfont=dict(size=10, color="#374151"),
        hovertemplate="<b>%{y}</b><br>Reviews: <b>%{x:,}</b><extra></extra>",
    ))
    
    # Create a local copy of PL so we can safely overwrite 'margin' without throwing a Multiple Values TypeError
    custom_layout = PL.copy()
    custom_layout["margin"] = dict(l=150, r=20, t=14, b=14)
    custom_layout["height"] = 480
    custom_layout["xaxis"] = dict(tickfont_size=10, gridcolor="#F1F5F9", zeroline=False)
    custom_layout["yaxis"] = dict(tickfont_size=10, autorange="reversed", automargin=True)
    custom_layout["bargap"] = 0.28
    custom_layout["showlegend"] = False
    
    fig.update_layout(**custom_layout)
    return fig