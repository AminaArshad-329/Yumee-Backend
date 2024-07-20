# import library
import math, random


# function to generate OTP
import os

from .core_functions import twilio_otp, otp_verification_check

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toietmoiapp_backend.settings")
import django
django.setup()

from .models import User_Profile


def generateOTP():
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789FRAZMIRA"
    OTP = ""

    # length of password can be chaged
    # by changing value in range
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP


# Driver codeorigin/Twilio_Signup
if __name__ == "__main__":
    print("OTP oSDASDSAits:", generateOTP())

    twilio_otp('03130802699')
    # print(otp_verification_check('03130802699','1616'))







