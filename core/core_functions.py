import math, random
import random

from core import models
from twilio.rest import Client

import core
from core.models import like_and_dislike


def generateOTP():
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""

    # length of password can be chaged
    # by changing value in range
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP


def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60


def twilio_otp(number):
    # (843)256 - 4013
    # +18432564013
    # +12674165593

    client = Client(account_sid, auth_token)
    verification = client.verify \
        .services('VA9946331ecea474d825f252e4ce910b3b') \
        .verifications \
        .create(to='+92'+str(number), channel='sms',)

def otp_verification_check(number,otp_code):


    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure

    client = Client(account_sid, auth_token)

    try:
        verification_check = client.verify.services('')\
            .verification_checks.create(to='+92'+str(number), code=otp_code)
        if(verification_check.status=="approved"):
            return True
    except:
        return False
    # if verification_check.valid=="True":
    #     return True
    # else:
    #     return False



class Pagination:
    def __init__(self,request, num_of_records):
        self.request = request
        self.num_of_records = num_of_records


    # instance method
    def custom_pagination(self, objects, model_name):
        try:
            page = int(self.request.GET.get('page'))
            if page < 1:
                page = 1
        except:
            page = 1
        items = page * self.num_of_records
        offset = (page - 1) * self.num_of_records
        all_seller_lead = model_name.objects.filter(user=self.request.user).order_by("id")[offset:items]
        totalitems = int(model_name.objects.count())
        totalpages = int(totalitems / self.num_of_records)
        per = totalitems % self.num_of_records
        if per != 0:
            totalpages += 1
        return all_seller_lead

    # def advance_filter_pagination(self,model_name,list):
    #     try:
    #         page = int(self.request.GET.get('page'))
    #         if page < 1:
    #             page = 1
    #     except:
    #         page = 1
    #     items = page * self.num_of_records
    #     offset = (page - 1) * self.num_of_records
    #     model = getattr(core.models, model_name)
    #     print(list)
    #     all_object = model.objects.filter(**list)
    #     # print(all_object,"++++++++++++++++++++++++++")
    #
    #     profile = like_and_dislike.objects.all().values('user_profile_liked_or_dislike')
    #     print(profile, "*************")
    #     all = all_object.exclude(user=self.request.user.id) and all_object.exclude(id__in=profile)
    #
    #
    #     # all_profile = all_object.exclude(user=self.request.user).order_by("id")[offset:items] # and all_object.exclude(id__in = profile)
    #     # print(self.request.user,"UUUUUUUUUUUUUUSER")
    #     all_profile = all.exclude(appear_to_other=False)
    #     lenght = len(all_profile)
    #     # print(lenght,"=========================")
    #     # totalitems = int(model.objects.count())
    #     totalpages = int(lenght / self.num_of_records)
    #     per = lenght % self.num_of_records
    #     if per != 0:
    #         totalpages += 1
    #     return all_profile

    def advance_filter_pagination(self, model_name, list ,user_obj):
        try:
            page = int(self.request.GET.get('page'))
            if page < 1:
                page = 1
        except:
            page = 1
        items = page * self.num_of_records
        offset = (page - 1) * self.num_of_records
        model = getattr(core.models, model_name)
        all_object = model.objects.filter(**list)
        profile = like_and_dislike.objects.filter(user=user_obj).values_list('user_profile_liked_or_dislike', flat=True)
        all_profile = all_object.exclude(id__in=profile)# and all_object.exclude(user=self.request.user).order_by("id")[offset:items]
        all_profile = all_profile.exclude(appear_to_other=False)
        all_profile = all_profile.exclude(user=self.request.user)
        if user_obj.interested_in == 'editprofile_gender_checkboxboth':
            pass
        else:
            all_profile = all_profile.exclude(gender=user_obj.gender).order_by("id")[offset:items]
        lenght = len(all_profile)
        totalpages = int(lenght / self.num_of_records)
        per = lenght % self.num_of_records
        if per != 0:
            totalpages += 1
        return all_profile

        # serializer = serializer_name(all_seller_lead, many=True)
        # return Response(serializer.data)



def qdict_to_dict(qdict):
    """Convert a Django QueryDict to a Python dict.

    Single-value fields are put in directly, and for multi-value fields, a list
    of all values is stored at the field's key.

    """
    return {k: v[0].capitalize() if len(v) == 1 else v for k, v in qdict.lists()}