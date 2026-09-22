import os
import base64
import streamlit as stre
import google.generativeai as gemini
from datetime import datetime, date

stre.set_page_config(
    page_title="Flight Fare Prediction",
    page_icon="✈️",
    layout="centered"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data=f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_of_bin_file("bgimage.jpg") 

stre.markdown(f"""
    <style>
    .stApp {{
    background-image:url("data:image/jpg;base64,{img_base64}");
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
    }}

    [data-testid="block-container"] {{
        background-color: rgba(255, 255, 255,0.3);
        backdrop-filter:blur(8px);
        padding:2rem;
        border-radius:20px;
        margin-top:2rem;
        margin-bottom:2rem;
    }}

    label, p {{
        color: white !important;
        font-weight:600 !important;
    }}

    .hero_title {{
    color:black;
    font-size: 2.6rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0px;
    }}

    .hero_subtitle {{
    text-align: center;
    color: black !important;
    font-size: 1.1rem;
    margin-bottom: 25px;
    font-weight:600;
    }}

    .stButton>button {{
    width: 100%;
    background: linear-gradient(90deg, #2563EB, #7C3AED);
    color: white !important;
    font-size: 1.1rem;
    font-weight: 600;
    padding: 0.65rem 1rem;
    border-radius: 10px;
    border: none;
    box-shadow: 0 4px 14px rgba(37, 99, 235,0.3);
    transition: all 0.3s ease-in-out;
    }}

    .stButton>button:hover{{
    transform:translateY(-2px);
    box-shadow: 0 6px 20px rgba(124, 58, 237,0.4);
    }}
    div[data-testid="stForm"]{{
    border-radius: 12px;
    padding: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

stre.markdown('<h1 class="hero_title">Flight Fare Predictor</h1>', unsafe_allow_html=True)
stre.markdown('<p class="hero_subtitle">Enter you travel details below to get a price prediction of your flight.</p>', unsafe_allow_html=True)

API_KEY = os.environ.get("GEMINI_KEY")
stre.markdown("---")

flight_type = stre.radio("Select Flight Type:", ["Domestic (India)", "International"], horizontal=True)
trip_type = stre.radio("Select Trip Type:", ["One-Way", "Round-Trip"], horizontal=True)
domestic_cities = sorted([
    'Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad', 'Chennai', 'Ahmedabad', 'Pune', 'Goa', 'Kochi', 'Jaipur', 'Lucknow', 'Guwahati', 'Chandigarh', 'Indore', 'Varanasi', 'Bhubaneswar', 'Patna'
])
international_cities = sorted([
    'Delhi, India', 'Mumbai, India', 'Bangalore, India', 'Chennai, India', 'New York, USA', 'Los Angeles, USA', 'London, UK', 'Dubai, UAE', 'Doha, Qatar', 'Singapore', 'Tokyo, Japan', 'Paris, France', 'Toronto, Canada', 'Sydney, Australia', 'Bangkok, Thailand', 'Frankfurt, Germany', 'Kuala Lumpur, Malasiya', 'Amsterdam, Netherlands', 'Rome, Italy', 'Hong Kong'
])
domestic_airlines = [
    'Any Airline(Lowest Price)', 'IndiGo', 'Air India', 'SpiceJet', 'Vistara', 'Akasa Air', 'Air India Express'
]
international_airlines = [
    'Any Airline(Lowest Price)', 'Air India', 'Emirates', 'Qatar Airways', 'Singapore Airlines', 'British Airways', 'Lufthansa', 'Etihad Airways', 'United Airlines', 'Cathay Pacific', 'Thai Airways', 'IndiGo'
]

# splitting inputs in two columns
column1, column2 = stre.columns(2)

with column1:
    if flight_type == "Domestic (India)":
        source_city = stre.selectbox("From", domestic_cities)
        destination_city = stre.selectbox("To", domestic_cities, index= min(1, len(domestic_cities)- 1))
        selected_airline = domestic_airlines
    else:
        source_city = stre.selectbox("From", international_cities)
        destination_city = stre.selectbox("To", international_cities)
        selected_airline = international_airlines
    compare_flights = stre.checkbox("Compare two airlines?")
    if compare_flights:
        airline1 = stre.selectbox("Airline 1", selected_airline, index=0)
        airline2 = stre.selectbox("Airline 2", selected_airline, index=1)
    else:
        airline1 = stre.selectbox("Preferred Airline", selected_airline, index=0)
        airline2 = None
    travel_class = stre.selectbox("Cabin Class", ['Economy', 'Premium Economy', 'Business', 'First Class'])
with column2:
    today = date.today()
    flight_date = stre.date_input("Flight Date", min_value=today, value=today)
    time_options = [
        "Early Morning (12AM - 6AM)",
        "Morning (6AM - 12PM)",
        "Afternoon (12PM - 5PM)",
        "Evening (5PM - 9PM)",
        "Night (9PM - 12AM)"
    ]
    flight_time = stre.selectbox("Departure Time", time_options)
    days_left = (flight_date - today).days
    if trip_type == "Round-Trip":
        return_date = stre.date_input("Return Flight Date", min_value=flight_date, value=flight_date)
        return_days = (return_date - flight_date).days
        formatted_return_date = return_date.strftime("%B %d, %Y")
    else:
        return_date = None
        formatted_return_date = "N/A"

stre.markdown("---")

if stre.button("Predict Fare"):
    stre.markdown("""
        <div class="flying-plane">✈️</div>
        <style>
        @keyframes fly {
        0% {
            left:-10vw;
            bottom:-10vh;
            opacity:1;
        }
        100% {
        left:110vw;
        bottom:110vh;
        opacity:0;
        }
    }
        .flying-plane{
        position:fixed;
        font-size:100px;
        z-index:999999;
        pointer-events: none;
        animation: fly 2.5s ease-in forwards;
        }
        </style>
    """, unsafe_allow_html=True)

    if not API_KEY or API_KEY== "YOUR_API_KEY_HERE":
        stre.error("Please insert API key")
    elif source_city == destination_city:
        stre.warning("⚠️ Source and Destination cannot be the same place.")
    else:
        formatted_date = flight_date.strftime("%B %d, %Y")
        formatted_time = flight_time

        with stre.spinner("Analyzing flight price data..."):
            try:
                gemini.configure(api_key=API_KEY)
                model = gemini.GenerativeModel('gemini-3.5-flash-lite')

                if trip_type == "Round-Trip":
                    trip_details = f"a ROUND-TRIP {travel_class} class flight from {source_city} to {destination_city} and back. The outbound flight is on {formatted_date} ({days_left} days from today) at {formatted_time}, and the return flight is on {formatted_return_date} ({return_days} days after departure)."
                else:
                    trip_details = f"a one-way {travel_class} class flight from {source_city} to {destination_city}. The flight is on {formatted_date} ({days_left} days from today) at {formatted_time}."

                if compare_flights:
                    prompt = f"""
                    You are an expert global travel agent. Estimate the current average price in INR (₹) for {trip_details}
                    Airlines to compare:
                    1. {airline1}
                    2. {airline2}
                    Consider airline tier (budget vs premium), time of departure, seasonality, and advance booking window. If the preferred airline does not directly fly this specific route, mention the most common operating carriers.
                    CRITICAL INSTRUCTION: If the selected airline does NOT offer the requested Cabin Class(e.g., Indigo or SpiceJet usually do not have business class or first class), set the Estimated Range to "N/A" and explain this limitation in the explaination.
                    Respond ONLY in this format:
                    **{airline1} Estimated Range:** ₹X,XXX - ₹Y,YYY (or N/A)
                    **{airline2} Estimated Range:** ₹X,XXX - ₹Y,YYY (or N/A)
                    
                    **Explaination:** [2-3 sentences comparing the price based on airline tier, date and route]
                    """
                else:
                    prompt = f"""
                    You are an expert global travel agent. Estimate the current average price in INR (₹) for {trip_details}
                    Flight Details:
                    - Preferred Airline: {airline1}
                    Consider airline tier (budget vs premium), time of departure, seasonality, and advance booking window. If the preferred airline does not directly fly this specific route, mention the most common operating carriers.
                    CRITICAL INSTRUCTION: If the selected airline does NOT offer the requested Cabin Class(e.g., Indigo or SpiceJet usually do not have business class or first class), set the Estimated Range to "N/A" and explain this limitation in the explaination.
                    Respond ONLY in this format:
                    **Estimated Range:** ₹X,XXX - ₹Y,YYY

                    **Explaination:** [1-2 sentences explaining the price based on airline choice, date and route]
                    """
                response = model.generate_content(prompt)
                stre.success(response.text)
            except Exception as e:
                stre.error(f"An error occured: {e}")
