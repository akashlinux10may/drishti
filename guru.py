import time
from supabase import create_client, Client
from twilio.rest import Client as TwilioClient

# --- DZIRE TECH CONFIGURATION ---
SUPABASE_URL = "https://wiyrwciskmononuaaeih.supabase.co"
SUPABASE_KEY = "sb_publishable_SlQxcUZEN193jYnehQvLEg_f5fUlS8_"

# Credentials from your screenshot
TWILIO_SID = "AC95f3fc37aff0efc284b77ecbf9fb441d".strip()
TWILIO_TOKEN = "e741a114e0f986dd0e790c5131603bd7".strip()

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+917017834244" 

# Initialize Clients
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    twilio_client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
    print("✅ [SYSTEM] Connected to Supabase and Twilio successfully.")
except Exception as e:
    print(f"❌ [SYSTEM] Connection Error: {e}")

def send_guru_alert(name, time_str):
    print(f"DEBUG: 🛠️ Attempting to construct WhatsApp message for {name}...")
    
    message_body = (
        f"✅ *Dzire Guru-Assistant: Student Entry*\n\n"
        f"Dear Parent, your child *{name}* has entered the campus safely at {time_str}.\n\n"
        f"🛡️ _Safety monitoring by Dzire Technologies_"
    )
    
    try:
        print(f"DEBUG: 📡 Sending request to Twilio API for {name}...")
        message = twilio_client.messages.create(
            body=message_body,
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )
        print(f"🚀 [SUCCESS] WhatsApp SID: {message.sid} - Alert sent for {name}!")
    except Exception as e:
        print(f"❌ [TWILIO ERROR] Failed to send message: {e}")

# --- MONITORING LOOP ---
# HARDCODED TO 0 to pick up all existing logs for the demo
last_id = 0 
print(f"👨‍💼 Guru-Assistant Agent is LIVE. Starting scan from ID: {last_id}")

while True:
    try:
        # Query for logs greater than our last processed ID
        response = supabase.table("attendance_logs").select("*").gt("id", last_id).execute()
        
        # DEBUG: See how many records were found in this poll
        if len(response.data) > 0:
            print(f"DEBUG: 🔎 Found {len(response.data)} new attendance records in Supabase.")
        
        for entry in response.data:
            student_name = entry['student_name']
            entry_time = entry['entry_time']
            current_id = entry['id']
            
            # Trigger the WhatsApp
            send_guru_alert(student_name, entry_time)
            
            # Update the last_id so we don't process this record again
            last_id = current_id
            
    except Exception as e:
        print(f"❌ [DB ERROR] Error fetching from Supabase: {e}")
    
    # Poll every 5 seconds
    time.sleep(5)