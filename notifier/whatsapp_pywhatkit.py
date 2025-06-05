import pywhatkit as kit

# Parameters:
# phone_number: str - The phone number in the format "country_code+number"
# message: str - The message to send
#kit.sendwhatmsg_instantly("false_120363402705898527@g.us_3E4387A15AA377E8AD316E4F76444989_201140487737@c.us", "Instant message!", wait_time=10, tab_close=True)
def send_whatsapp_message(text):
    try:
        kit.sendwhatmsg_instantly("+4917657989352", text, wait_time=10, tab_close=False)
        print(f"[+] Sent WhatsApp message: {text}")
    except Exception as e:
        print(f"[!] Error sending WhatsApp message: {e}")

if __name__ == "__main__":
    try:
        send_whatsapp_message("Test message from WhatsApp notifier!")
    except Exception as e:
        print(f"[!] Error sending WhatsApp message: {e}")