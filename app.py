
import streamlit as st
import pandas as pd
from datetime import date
from strava_utils import (

try:
    st.write("🔐 Client ID (test access):", st.secrets["STRAVA_CLIENT_ID"])
except Exception as e:
    st.error(f"❌ Could not read STRAVA_CLIENT_ID: {e}")

    refresh_strava_token,
    download_gpx_from_strava_route,
    extract_landmarks_from_gpx,
    describe_gpx_route
)

@st.cache_data
def load_data():
    df = pd.read_excel("RTR route schedule.xlsx")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

# Get access token from Streamlit secrets

client_id = st.secrets["STRAVA_CLIENT_ID"]
client_secret = st.secrets["STRAVA_CLIENT_SECRET"]
refresh_token = st.secrets["STRAVA_REFRESH_TOKEN"]

# Debug: display secret values (lengths only)
st.write("🔐 Client ID:", client_id)
st.write("🔐 Secret length:", len(client_secret))
st.write("🔐 Refresh token length:", len(refresh_token))

try:
    # removed lowercase client_id
    # removed lowercase client_secret
    # removed lowercase refresh_token
    token_data = refresh_strava_token(client_id, client_secret, refresh_token)
    access_token = token_data.get("access_token")
    st.success("✅ Strava token acquired.")
except Exception as e:
    access_token = None
    st.warning("⚠️ Could not acquire Strava token. GPX functionality will be skipped.")

# Load and preview schedule
df = load_data()
preview_cols = ["Week", "Date", "Meeting point", "8k Route", "8k Strava link", "5k Route", "5k Strava link"]
st.subheader("📅 Schedule Preview")
st.dataframe(df[preview_cols])

# Select run week
upcoming_weeks = df[df["Date"] >= date.today()]
if not upcoming_weeks.empty:
    default_date = upcoming_weeks.iloc[0]["Date"]
    selected_date = st.selectbox("Choose run date", df["Date"].unique(), index=df["Date"].tolist().index(default_date))
else:
    selected_date = st.selectbox("Choose run date", df["Date"].unique())

selected_row = df[df["Date"] == selected_date].iloc[0]

# Generate route messages
def build_route_description(route_link, route_name):
    if access_token and pd.notna(route_link):
        gpx_data = download_gpx_from_strava_route(route_link, access_token)
        if gpx_data:
            landmarks = extract_landmarks_from_gpx(gpx_data, access_token)
            desc = describe_gpx_route(gpx_data)
            if landmarks:
                return f"{desc}. It passes {landmarks}."
            else:
                return desc
    return ""

route_8k = selected_row["8k Route"]
link_8k = selected_row["8k Strava link"]
desc_8k = build_route_description(link_8k, route_8k)

route_5k = selected_row["5k Route"]
link_5k = selected_row["5k Strava link"]
desc_5k = build_route_description(link_5k, route_5k)

# Assemble message
lines = [
    "🌟 It’s nearly time to lace up! Here's what we’ve got planned:",
    f"📍 Meeting at: {selected_row['Meeting point']}",
    "🕖 We set off at 7:00pm",
    "",
    "🛣️ This week we’ve got two route options to choose from:",
    f"• 8k – {route_8k}: {link_8k}" + (f"\n   {desc_8k}" if desc_8k else ""),
    f"• 5k – {route_5k}: {link_5k}" + (f"\n   {desc_5k}" if desc_5k else ""),
    "",
    "📲 Book now: https://groups.runtogether.co.uk/RunTogetherRadcliffe/Runs",
    "❌ Can’t make it? Cancel at least 1 hour before: https://groups.runtogether.co.uk/My/BookedRuns",
    "",
    "Grab your shoes, bring your smiles – see you Thursday! 👟"
]

# Output
st.subheader("📧 Email Message")
email_msg = "\n".join(lines)
st.code(email_msg, language="text")

st.subheader("📱 WhatsApp Message")
whatsapp_msg = "\n".join(lines)
st.code(whatsapp_msg, language="text")

st.subheader("📣 Facebook Message")
facebook_msg = "\n".join(lines)
st.code(facebook_msg, language="text")