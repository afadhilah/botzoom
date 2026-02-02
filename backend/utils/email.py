"""
Email utility for sending OTP and notifications.
Uses FastAPI-Mail for async email sending.
"""

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from core.config import settings
from typing import List


# Configure email connection
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)


def send_otp_email(email: str, full_name: str, otp_code: str):
    """
    Send OTP verification email to user.
    
    Args:
        email: Recipient email address
        full_name: User's full name
        otp_code: The OTP code to send
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_SERVER:
        raise Exception("Email configuration is not set. Please configure SMTP settings in .env file")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4F46E5;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .otp-box {{
                background-color: white;
                border: 2px dashed #4F46E5;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                color: #4F46E5;
                letter-spacing: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Verification</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{full_name}</strong>,</p>
                
                <p>Thank you for registering with Meeting Transcript System. To complete your registration, please use the following OTP code:</p>
                
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                
                <p>This code will expire in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
                
                <p>If you didn't request this code, please ignore this email.</p>
                
                <p>Best regards,<br>
                Meeting Transcript Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Your OTP Verification Code",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    
    # Send email synchronously
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(fm.send_message(message))


async def send_otp_email_async(email: str, full_name: str, otp_code: str):
    """
    Async version of send_otp_email for use in async contexts.
    
    Args:
        email: Recipient email address
        full_name: User's full name
        otp_code: The OTP code to send
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_SERVER:
        raise Exception("Email configuration is not set. Please configure SMTP settings in .env file")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4F46E5;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .otp-box {{
                background-color: white;
                border: 2px dashed #4F46E5;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                color: #4F46E5;
                letter-spacing: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Verification</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{full_name}</strong>,</p>
                
                <p>Thank you for registering with Meeting Transcript System. To complete your registration, please use the following OTP code:</p>
                
                <div class="otp-box">
                    <div class="otp-code">{otp_code}</div>
                </div>
                
                <p>This code will expire in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
                
                <p>If you didn't request this code, please ignore this email.</p>
                
                <p>Best regards,<br>
                Meeting Transcript Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Your OTP Verification Code",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)


def send_password_reset_email(email: str, full_name: str, reset_token: str):
    """
    Send password reset email to user.
    
    Args:
        email: Recipient email address
        full_name: User's full name
        reset_token: Password reset token
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_SERVER:
        raise Exception("Email configuration is not set. Please configure SMTP settings in .env file")
    
    # Construct reset link (adjust URL as needed)
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4F46E5;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #4F46E5;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{full_name}</strong>,</p>
                
                <p>We received a request to reset your password. Click the button below to reset it:</p>
                
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </p>
                
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #4F46E5;">{reset_link}</p>
                
                <p>This link will expire in 1 hour.</p>
                
                <p>If you didn't request a password reset, please ignore this email.</p>
                
                <p>Best regards,<br>
                Meeting Transcript Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    
    # Send email synchronously
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(fm.send_message(message))
