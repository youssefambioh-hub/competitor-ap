# config.py

# ─────────────────────────────────────────────────────────────────────────────
#  SNOWFLAKE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
import os
import tempfile
SF_USER       = "YOUSEF_24"
SF_ACCOUNT    = "DWDONOX-HK36448"
SF_WAREHOUSE  = "COMPUTE_WH"
SF_DATABASE   = "EXTERNAL_DATA"
SF_SCHEMA     = "LOGGING"
SF_ROLE       = "BI_TEAM_MEMBER"
SF_TABLE      = "CLINICS_DATA"


#  
env_key = os.environ.get("SNOWFLAKE_PRIVATE_KEY")

if env_key:
    #  
    temp_key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    
    #  
    formatted_key = env_key.replace("\\n", "\n") 
    
    temp_key_file.write(formatted_key.encode('utf-8'))
    temp_key_file.close()
    
    #  
    PRIVATE_KEY_PATH = temp_key_file.name
else:
    #  
    PRIVATE_KEY_PATH = r"D:\yousef\Downloads\data_Keys_private_key_pkcs8.pem"
# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY BASE LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
PL = dict(
    font_family="Inter, sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=14, b=14, l=10, r=10),
    font_color="#374151",
)

# ─────────────────────────────────────────────────────────────────────────────
#  TOP 7 DATA
# ─────────────────────────────────────────────────────────────────────────────
TOP7_DATA = [
    {
        "rank": 1, "name": "Hands-On PT — Astoria", "area": "Astoria, Queens",
        "rating": "4.9", "reviews": "1,339", "threat": 5,
        "strengths": [
            "1,339 reviews — 10× more than most competitors",
            "MSKUS & EMG diagnostic imaging on-site (unique differentiator)",
            "Partnered with MOTION Sports Medicine / Montefiore Einstein",
            "Open 7:30 AM daily + Saturdays 8 AM–4 PM",
            "Hospital referral pipeline since 1992 — deep community loyalty",
        ],
        "weaknesses": [
            "Recent merger into MOTION chain may dilute boutique identity",
            "Primarily Queens-focused — limited Manhattan/Brooklyn reach",
            "Large chain feel may reduce personalized care perception",
            "No Sunday hours",
        ],
    },
    {
        "rank": 2, "name": "Therapy-In-Motion PC", "area": "Sunset Park, Brooklyn",
        "rating": "5.0", "reviews": "1,009", "threat": 5,
        "strengths": [
            "Perfect 5.0 rating with 1,009 reviews — #1 Brooklyn by Consumer Reports 10 yrs",
            "PT + OT + home care under one roof (unique full-spectrum offering)",
            "Multilingual: Yiddish, Russian, Hebrew — strong immigrant community ties",
            "Open Sundays — rare competitive advantage",
            "Owner Dr. Abe Kopolovich holds DPT/MBA/JD-IP — elite credential",
            "Direct EMR integration with Montefiore via Epic for seamless referrals",
        ],
        "weaknesses": [
            "Single location — no geographic expansion yet",
            "Owner-dependent model: risk if founder steps back",
            "Very niche language focus may limit broader NYC appeal",
        ],
    },
    {
        "rank": 3, "name": "NY Therapy & Wellness", "area": "Sheepshead Bay, Brooklyn",
        "rating": "5.0", "reviews": "828", "threat": 5,
        "strengths": [
            "Perfect 5.0 rating with 828 reviews — dominant in Sheepshead Bay",
            "PT + OT + wellness whole-body model drives higher retention",
            "Telehealth + in-clinic + home visit — most delivery modes covered",
            "Multi-specialty rehabilitation attracts diverse patient base",
        ],
        "weaknesses": [
            "1–2 locations only — limited scalability",
            "No weekend hours listed — accessibility gap",
            "Wellness brand may confuse PT-seeking patients in search",
            "Less known outside southern Brooklyn",
        ],
    },
    {
        "rank": 4, "name": "Evolve PT — Marine Park", "area": "Midwood / Marine Park, Brooklyn",
        "rating": "5.0", "reviews": "676", "threat": 5,
        "strengths": [
            "676 reviews + perfect 5.0 across 4–5 Brooklyn locations",
            "Uses Prompt EMR + self-service kiosks — evals reduced to 10 mins",
            "Open until 8 PM weekdays + walk-ins welcome — highest convenience",
            "Pelvic floor + running/gait analysis + pediatric PT — high-demand niches",
            "20-provider practice with owner Lou Ezrick — strong local SEO",
        ],
        "weaknesses": [
            "Rapid expansion risks quality consistency across locations",
            "No telehealth — missing post-COVID digital patient base",
            "No Sunday or Saturday hours despite high volume",
            "Kiosk model may feel impersonal vs. boutique competitors",
        ],
    },
    {
        "rank": 5, "name": "Phoenix Physical Therapy", "area": "Bay Ridge, Brooklyn",
        "rating": "5.0", "reviews": "488", "threat": 5,
        "strengths": [
            "DPT-owned boutique — patients trust physician-run practice",
            "Mulligan + McKenzie methods — advanced manual therapy credentials",
            "Pelvic floor specialty with dedicated waitlist for postpartum rehab",
            "3 locations (Bay Ridge, Rosedale, Dix Hills) + 61 hrs/week open",
            "Open until 8 PM + Saturdays — strong access advantage",
        ],
        "weaknesses": [
            "Limited insurance panel (Aetna, BCBS, Cigna, Medicare, Emblem only)",
            "No telehealth — losing digital-first patients",
            "Boutique model caps patient volume vs. chain competitors",
            "Dix Hills location outside NYC core market",
        ],
    },
    {
        "rank": 6, "name": "Evolve PT — Upper East Side", "area": "Upper East Side, Manhattan",
        "rating": "5.0", "reviews": "301", "threat": 5,
        "strengths": [
            "Perfect 5.0 with 301 reviews — strongest on UES",
            "ONLY competitor open Saturdays 7 AM–2:30 PM in area",
            "Walk-ins accepted, no appointment needed — top convenience",
            "Open 7 AM all 6 days — earliest hours in neighborhood",
            "Multiple NYC locations + Syosset LI — broad geographic coverage",
        ],
        "weaknesses": [
            "No telehealth listed — digital gap",
            "High-end UES location means premium pricing expectations",
            "301 reviews lower than top Brooklyn competitors",
            "Chain model may reduce boutique appeal vs. independent practices",
        ],
    },
    {
        "rank": 7, "name": "Therapy-In-Motion (Sensory / OT)", "area": "Sunset Park / Sensory Clinic",
        "rating": "5.0", "reviews": "828", "threat": 5,
        "strengths": [
            "Dedicated pediatric sensory gym — top referral for local pediatricians",
            "High cash-pay conversion for out-of-network pediatric services",
            "PT + OT integration: birth-to-adult care pathway",
            "Parkinson's + cardiac rehab + geriatric PT — rare specializations",
        ],
        "weaknesses": [
            "Highly niche — pediatric sensory limits adult PT volume",
            "Out-of-network model excludes insurance-dependent patients",
            "Single location caps growth potential",
            "Niche brand name may not surface in standard PT searches",
        ],
    },
]

SF_COL_RENAMES = {
    "CLINIC_NAME": "Clinic Name",
    "IS_PT_OF_THE_CITY": "Is PT of The City?",
    "NEIGHBORHOOD_AREA": "Neighborhood / Area",
    "ADDRESS": "Address",
    "GOOGLE_RATING": "Google Rating",
    "REVIEWS": "# Reviews",
    "FOUNDED_EST": "Founded / Est.",
    "PARENT_ORGANIZATION": "Parent Organization",
    "MON_HOURS": "Mon Hours",
    "MON_CLOSE": "Mon Close",
    "TUE_HOURS": "Tue Hours",
    "TUE_CLOSE": "Tue Close",
    "WED_HOURS": "Wed Hours",
    "WED_CLOSE": "Wed Close",
    "THU_HOURS": "Thu Hours",
    "THU_CLOSE": "Thu Close",
    "FRI_HOURS": "Fri Hours",
    "FRI_CLOSE": "Fri Close",
    "SAT_HOURS": "Sat Hours",
    "SAT_CLOSE": "Sat Close",
    "SUN_HOURS": "Sun Hours",
    "SUN_CLOSE": "Sun Close",
    "WEEKDAY_HRS_WK": "Weekday Hrs/Wk",
    "WEEKEND_HRS_WK": "Weekend Hrs/Wk",
    "TOTAL_HRS_WK": "Total Hrs/Wk",
    "FULL_WEEKLY_SCHEDULE": "Full Weekly Schedule",
    "SPECIALIZATIONS": "Specializations",
    "WEBSITE": "Website",
    "WEBSITE_STATUS": "Website_Status",
    "WEBSITE_LINK": "Website_Link",
    "PHONE": "Phone",
    "COMPETITOR_NOTES": "Competitor Notes",
    "GOOGLE_MAPS_LINK": "Google Maps Link",
    "DISTANCE_FROM_PTOTC_MI": "Distance from PTotC (mi)",
    "OWNER_FOUNDER": "Owner_Founder",
    "CHAIN_SIZE": "Chain_Size",
    "TELEHEALTH": "Telehealth",
    "LANGUAGES_SPOKEN": "Languages_Spoken",
    "YELP_RATING": "Yelp_Rating",
    "YELP_REVIEWS": "Yelp_Reviews",
    "SOCIAL_MEDIA": "Social_Media",
    "KEY_EQUIPMENT": "Key_Equipment",
    "HOME_CARE": "Home_Care",
    "COMPETITIVE_THREAT_1TO5": "Competitive_Threat_1to5",
    "RAG_SUMMARY": "RAG_Summary",
    "INFORMATION_SOURCES_URLS": "Information_Sources (URLs)",
    "UNIQUE_SELLING_PROPOSITION_USP": "Unique_Selling_Proposition_USP",
    "DEEP_SEARCH_EXTRA_NOTES": "Deep_Search_Extra_Notes",
    "ESTIMATED_DAILY_VOLUME": "Estimated_Daily_Volume",
    "TOP_THREAT_FLAG": "Top_Threat_Flag",
    "WEEKEND_ADVANTAGE": "Weekend_Advantage",
    "LATITUDE": "Latitude",
    "LONGITUDE": "Longitude",
    "ZIP_CODE": "Zip_Code",
    "GOOGLE_SCORE": "Google Score",
    "NEAREST_PT_OF_THE_CITY": "Nearest_PT_of_The_City",
    "DISTANCE_TO_NEAREST_PTOTC_MILES": "Distance_to_Nearest_PTotC_miles",
    "INSURANCES_ACCEPTED_CLEAN": "Insurances_Accepted_Clean",
    "INSURANCE_VERIFICATION_NOTES": "Insurance_Verification_Notes",
    "STRENGTHS": "Strengths",
    "WEAKNESSES": "Weaknesses",
}