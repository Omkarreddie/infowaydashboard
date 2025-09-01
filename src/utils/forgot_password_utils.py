import streamlit as st
import random 
import smtplib
from email.mime.text import MIMEText
def generate_otp():
        return str(random.randint(10000,100000))
def send_email_otp(to_email, otp):
        # Replace below with your real email credentials
        sender_email = "omkaradireddy143@gmail.com"
        sender_password = "mmih jxwl suoj xvti"  # Use App Password for Gmail

        msg = MIMEText(f"Your OTP for password reset is: {otp}")
        msg['Subject'] = "Password Reset OTP"
        msg['From'] = sender_email
        msg['To'] = to_email
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                st.success("OTP sent to Successfully ")
        except Exception as e:
            st.error(f"Failed to send email: {e}")