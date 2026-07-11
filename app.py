import streamlit as st
import pandas as pd
import random
import io
from datetime import datetime
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Registration Form / पंजीकरण फॉर्म", layout="wide")

# --- DATABASE CONNECTION ---
# Initialize connection to Supabase using Streamlit Secrets
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Database connection failed / डेटाबेस कनेक्शन विफल: {e}")

# --- HELPER FUNCTIONS ---
def generate_unique_code():
    """Generates a random 4-digit code."""
    return str(random.randint(1000, 9999))

def to_excel(df):
    """Converts a Pandas DataFrame to an Excel file in memory."""
    output = io.BytesIO()
    # openpyxl natively supports UTF-8 for Hindi text
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Registrations')
    processed_data = output.getvalue()
    return processed_data

# --- MAIN UI: REGISTRATION FORM ---
st.title("Event Registration / इवेंट पंजीकरण")
st.write("Please fill out the details below / कृपया नीचे विवरण भरें:")

with st.form("registration_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name / नाम")
        designation = st.text_input("Designation / पद")
        place = st.text_input("Place / स्थान")
        
    with col2:
        railway_zone = st.selectbox(
            "CR/WR / मध्य रेलवे/पश्चिम रेलवे", 
            ["Central Railway (CR)", "Western Railway (WR)", "Other / अन्य"]
        )
        competition = st.text_input("Competition Name / प्रतियोगिता का नाम")
        comp_date = st.date_input("Date / दिनांक", datetime.today())
        
    submit_button = st.form_submit_button("Submit / जमा करें")

    if submit_button:
        if not name or not designation or not place or not competition:
            st.warning("Please fill all fields / कृपया सभी फ़ील्ड भरें")
        else:
            # Generate Unique Code
            unique_code = generate_unique_code()
            
            # Prepare data payload
            data = {
                "name": name,
                "designation": designation,
                "place": place,
                "railway_zone": railway_zone,
                "competition": competition,
                "date": str(comp_date),
                "unique_code": unique_code
            }
            
            # Insert into Supabase
            try:
                response = supabase.table("registrations").insert(data).execute()
                
                # Check for successful insertion
                if len(response.data) > 0:
                    st.success(f"Registration Successful! / पंजीकरण सफल!")
                    st.info(f"### Your Unique Code / आपका विशिष्ट कोड: **{unique_code}**")
                else:
                    st.error("Failed to save data. Please try again. / डेटा सहेजने में विफल. कृपया पुनः प्रयास करें.")
            except Exception as e:
                st.error(f"Error / त्रुटि: {e}")


# --- SIDEBAR: ADMIN DASHBOARD ---
st.sidebar.title("Admin Access / व्यवस्थापक पहुंच")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")

# Check if password matches the one in secrets
if admin_password == st.secrets.get("ADMIN_PASSWORD", "admin123"):
    st.sidebar.success("Logged in successfully")
    
    st.divider()
    st.header("Admin Dashboard: Registration Data")
    
    # Fetch Data from Supabase
    try:
        response = supabase.table("registrations").select("*").order("created_at", desc=True).execute()
        data = response.data
        
        if data:
            # Convert to Pandas DataFrame for easy viewing and export
            df = pd.DataFrame(data)
            
            # Reorder columns for better readability (Optional)
            cols = ['unique_code', 'name', 'designation', 'place', 'railway_zone', 'competition', 'date', 'created_at']
            # Only keep columns that actually exist in the dataframe to avoid errors
            df = df[[c for c in cols if c in df.columns]]
            
            st.dataframe(df, use_container_width=True)
            
            # Excel Export Button
            excel_data = to_excel(df)
            st.download_button(
                label="Download Data as Excel / एक्सेल के रूप में डेटा डाउनलोड करें",
                data=excel_data,
                file_name=f'registrations_{datetime.today().strftime("%Y-%m-%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.info("No registrations found yet.")
            
    except Exception as e:
        st.error(f"Failed to fetch data / डेटा लाने में विफल: {e}")
elif admin_password:
    st.sidebar.error("Incorrect Password")
