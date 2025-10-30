import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from helpers import load_properties, get_property_by_id, get_property_by_name, polish_with_llm

# --- Configuration & Data Loading ---
st.set_page_config(page_title="Real Estate Chatbot")
st.title("Real Estate Chatbot")

# Use st.cache_data for efficient data loading
@st.cache_data
def load_data():
    return load_properties()

properties_df = load_data()
#  Create a list of options for the dropdown
property_options = properties_df.apply(
    lambda row: f"{row['property_name']} - {row['listing_id']}", axis=1
).tolist()

# add an initial blank option
property_options.insert(0, "Select a property (optional)")

# Create a dictionary to easily get the listing_id from the selected string
property_map = {
    f"{row['property_name']} - {row['listing_id']}": row['listing_id']
    for index, row in properties_df.iterrows()
}
if properties_df is None:
    st.error("Error: properties.csv not found. Please check the 'data' directory.")
    st.stop()

# Define hard-coded FAQs
faq_data = {
    "office location": "Our main office is located in Dubai, UAE.",
    "working hours": "We are open from 9 AM to 6 PM, Monday to Friday.",
    "contact": "You can reach us at info@zorever.com or call us at +91-9876543210."
}

# Initialize session state for the chat history and booking form visibility
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with your real estate needs today?"}]
    st.markdown("""
    Ask FAQs: Office location, working hours, and contact of the Zorever Real State.
    """)
if "show_booking_form" not in st.session_state:
    st.session_state.show_booking_form = False

# --- Booking Automation Logic ---
def save_booking(name, phone, property_query, user_message):
    visits_file_path = 'data/visits.csv'
    
    listing_id = ""
    property_name = ""

    if property_query:
        prop_id_match = re.search(r'P\d{3}', property_query, re.IGNORECASE)
        if prop_id_match:
            found_prop = get_property_by_id(properties_df, prop_id_match.group(0).upper())
            if found_prop:
                listing_id = found_prop[0]['listing_id']
                property_name = found_prop[0]['property_name']
        if not listing_id:
            found_props = get_property_by_name(properties_df, property_query)
            if found_props:
                listing_id = found_props[0]['listing_id']
                property_name = found_props[0]['property_name']

    booking_data = {
        'timestamp': datetime.now().isoformat(),
        'listing_id': listing_id,
        'property_name': property_name,
        'name': name,
        'phone': phone,
        'user_message': user_message
    }
    
    file_exists = os.path.isfile(visits_file_path)
    with open(visits_file_path, 'a') as f:
        if not file_exists:
            f.write("timestamp,listing_id,property_name,name,phone,user_message\n")
        f.write(f"{booking_data['timestamp']},{booking_data['listing_id']},{booking_data['property_name']},{booking_data['name']},{booking_data['phone']},{booking_data['user_message']}\n")
    
    return f"Thanks, {name}! Your visit has been booked. We will contact you shortly."

# --- Chatbot Core Logic ---
def format_property_details(prop):
    details = (
        f"{prop['property_name']} — {prop['bedrooms']} BHK ({prop['area_sqft']} sqft) in {prop['city']}. "
        f"Price: {prop['price']} {prop['price_currency']}. Status: {prop['availability']}. "
        f"Short: {prop['short_description']} Contact: {prop['agent_email']}"
    )
    return details

def get_chatbot_response(prompt):
    user_input_lower = prompt.lower()

     # Add conversational intent 
    if any(word in user_input_lower for word in ["hello", "hi", "hey"]):
        return "Hello there! How can I help you today?", None
    
    if any(word in user_input_lower for word in ["thank", "thanks", "thankyou"]):
        return "You're welcome! ThankYou for visiting", None

     # Check if the user is asking to see properties for sale
    if any(keyword in user_input_lower for keyword in ["buy", "purchase", "looking for a flat", "want to buy a flat", "show me flats", "want to visit flat"]):
        
        # Filter properties based on "Available" status, as per the CSV data
        flats_for_sale = properties_df[properties_df['availability'].str.contains("Available", case=False, na=False)]
        
        # Add a conditional filter for location if a city is mentioned
        city_match = re.search(r'in ([\w\s]+)', user_input_lower)
        if city_match:
            city_query = city_match.group(1).strip()
            flats_for_sale = flats_for_sale[flats_for_sale['city'].str.contains(city_query, case=False, na=False)]
        
        if not flats_for_sale.empty:
            response_list = ["Here is a list of properties available for you:", ""]
            for index, row in flats_for_sale.iterrows():
                response_list.append(
                    f"**{row['property_name']}**\n"
                    f"**Location:** {row['city']}\n"
                    f"**BHK:** {row['bedrooms']}\n"
                    f"**Price:** {row['price']} {row['price_currency']}\n"
                    f"**Listing ID:** {row['listing_id']}\n"
                )
            response_list.append("\nFor more details on a specific property, please ask me by its name or Listing ID!")
            return "\n".join(response_list), None
        else:
            return "I'm sorry, there are no properties available for sale. Please check back later!", None
    
    if any(keyword in user_input_lower for keyword in ["book a visit", "schedule a visit", "visit booking"]):
        st.session_state.show_booking_form = True
        st.markdown("Please fill out the form below to book your visit.")
        st.rerun()

    for keyword, answer in faq_data.items():
        if keyword in user_input_lower:
            return polish_with_llm(answer), None

    prop_id_match = re.search(r'P\d{3}', user_input_lower, re.IGNORECASE)
    if prop_id_match:
        prop_id = prop_id_match.group(0).upper()
        found_prop = get_property_by_id(properties_df, prop_id)
        if found_prop:
            formatted_details = format_property_details(found_prop[0])
            return polish_with_llm(formatted_details), found_prop[0]['listing_id']

    found_props = get_property_by_name(properties_df, user_input_lower)
    if found_props:
        formatted_details = format_property_details(found_props[0])
        return polish_with_llm(formatted_details), found_props[0]['listing_id']
        
    return "I'm sorry, I couldn't find information on that. Please try asking about a specific property by its name or listing ID.", None

# --- Streamlit UI Loop ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about a property or book a visit..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response_text, property_id = get_chatbot_response(prompt)

    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text, "property_id": property_id})
        with st.chat_message("assistant"):
            st.markdown(response_text)
            if property_id:
                if st.button(f"Book a visit for {property_id}"):
                    st.session_state.show_booking_form = True
                    st.session_state.prefill_property_id = property_id
                    st.rerun()


# booking form to use the pre-filled value ---
if st.session_state.show_booking_form:
    st.subheader("Book a Visit")
    prefilled_prop_id = st.session_state.get('prefill_property_id', '')
    with st.form("booking_form"):
        name = st.text_input("Full Name", key="booking_name")
        phone = st.text_input("Phone Number", key="booking_phone")
        selected_property_option = st.selectbox(
            "Which property?",
            options=property_options,
            key="booking_property_select"
        )
    
        submitted = st.form_submit_button("Submit Booking")
        if submitted:
            if not name or not phone:
                st.error("Please provide your name and phone number.")
            else:

            # listing_id from the selected option
                property_query = ""
                if selected_property_option != "Select a property (optional)":
                    property_query = property_map.get(selected_property_option, "")

                user_message = f"User booked a visit using the form for: {selected_property_option}"
                save_booking(name, phone, property_query, user_message)
                st.success("Booking submitted successfully! We'll contact you shortly.")
                st.session_state.messages.append({"role": "assistant", "content": "Your booking has been confirmed! A team member will reach out to you."})
                st.session_state.show_booking_form = False
                st.rerun()

