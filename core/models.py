from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from io import BytesIO
from PIL import Image
from django.core.files import File


# import reverse


# Create your models here.
class User_Profile(models.Model):
    KIDS_CHOICES = (
        ('partener_kids_yes', 'Yes'),
        ('partener_kids_no', 'No')
    )
    drinkandsmoke = (
        ('partener_drink_frequently', 'Frequently'),
        ('partener_drink_socially', 'Socially'),
        ('partener_drink_never', 'Never')
    )
    exercise = (
        ('partener_exercise_active', 'Active'),
        ('partener_exercise_sometime', 'Sometimes'),
        ('partener_exercise_almostNever', 'Almost Never')
    )
    religion = (
        ('Christian', 'Christian'),
        ('Buddhist', 'Buddhist'),
        ('Catholic', 'Catholic'),
        ('Islam', 'Islam'),
        ('Atheist', 'Atheist'),
        ('hindui', 'Spirituality'),
    )
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Super', 'Super'),
        ('User', 'User'),
        ('Vendor', 'Vendor'),
    )
    GENDER_CHOICES = (
        ('editprofile_gender_checkboxman', 'Male'),
        ('editprofile_gender_checkboxwoman', 'Female')
    )
    GENDER_INTERESTED = (
        ('editprofile_gender_checkboxman', 'Male'),
        ('editprofile_gender_checkboxwoman', 'Female'),
        ('editprofile_gender_checkboxboth', 'Both'),
    )
    Education = (
        (
            ('update_education_college_checkbox', 'College'),
            ('update_education_highschool_checkbox', 'High School'),
            ('update_education_BAC_checkbox', 'BAC Level'),
            ('update_university_checkbox', 'University Diploma'),
        )
    )
    PACKAGE = (
        (
            ('Classic', 'Classic'),
            ('VIP', 'VIP'),
            ('Classic Plus', 'Classic Plus'),
            ('VIP Plus', 'VIP Plus')
        )
    )
    PACKAGE_TIME = (
        (
            ('1 Month', '1 Month'),
            ('3 Month', '3 Month'),
            ('6 Month', '6 Month'),
            ('15 Days Trial', '15 Days Trial')
        )
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, default='0')
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True)
    email = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True)
    interested_in = models.CharField(max_length=100, choices=GENDER_INTERESTED, blank=True)
    your_name = models.CharField(max_length=255, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, default=0)
    interested_age = models.IntegerField(blank=True, null=True)
    max_interested_age = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    distance = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    education = models.CharField(max_length=200, choices=Education, blank=True)
    about = models.CharField(max_length=1000, blank=True)
    passion = ArrayField(models.CharField(max_length=200, blank=True, null=True), default=list)
    job_title = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    university = models.CharField(max_length=255, blank=True)
    school = models.CharField(max_length=255, blank=True)
    living = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    verfication_status = models.BooleanField(default=False)
    registration_status = models.BooleanField(default=False, blank=True)
    otp = models.CharField(max_length=255, blank=True, default='')
    otp_time = models.DateTimeField(auto_now=True)
    user_deactive_status = models.CharField(max_length=255, blank=True, default='')
    user_deactive_reason = models.CharField(max_length=255, blank=True, default='')
    forget_password_key = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    kids = models.CharField(max_length=100, blank=True, choices=KIDS_CHOICES)
    drink = models.CharField(max_length=100, blank=True, choices=drinkandsmoke)
    smoke = models.CharField(max_length=100, blank=True, choices=drinkandsmoke)
    religion = models.CharField(max_length=20, blank=True, choices=religion)
    exercise = models.CharField(max_length=200, blank=True, choices=exercise)
    appear_to_other = models.BooleanField(default=True, blank=True)
    time_list = ArrayField(models.DateTimeField(max_length=100, blank=True, null=True), default=list, blank=True)
    cross_user_list = ArrayField(models.CharField(max_length=100, blank=True, null=True), default=list, blank=True)
    popup_seen = models.BooleanField(default=False, blank=True, null=True)
    manage_read_receipts = models.BooleanField(default=False, blank=True)
    month_later_date = models.DateTimeField(auto_now_add=True)
    power_like_count = models.IntegerField(blank=True, null=True, default=1)

    package = models.CharField(max_length=100, choices=PACKAGE, blank=True, default='VIP Plus')
    package_duration = models.CharField(max_length=100, choices=PACKAGE_TIME, blank=True, default='15 Days Trial')
    package_date_start = models.DateField(blank=True, null=True)
    package_date_end = models.DateField(blank=True, null=True)
    remaining_days_in_exp = models.PositiveSmallIntegerField(default=15, blank=True)
    manage_read_receipts_date_start = models.DateField(blank=True, null=True)
    manage_read_receipts_date_end = models.DateField(blank=True, null=True)
    manage_read_receipts_payment = models.BooleanField(default=False, blank=True)
    fcm_token = models.CharField(max_length=200, blank=True, null=True)
    package_name = models.CharField(max_length=200, blank=True, null=True)
    classic_bonus_2chance = models.BooleanField(default=False, blank=True)
    classic_bonus_power_like = models.BooleanField(default=False, blank=True)
    classic_bonus_power_like_start = models.DateField(blank=True, null=True)
    classic_bonus_power_like_end = models.DateField(blank=True, null=True)
    vip_bonus_power_like = models.BooleanField(default=False, blank=True)
    vip_bonus_power_like_start = models.DateField(blank=True, null=True)
    vip_bonus_power_like_end = models.DateField(blank=True, null=True)
    classic_bonus_guaranteed_match = models.BooleanField(default=False, blank=True)
    classic_bonus_guaranteed_match_start = models.DateField(blank=True, null=True)
    classic_bonus_guaranteed_match_end = models.DateField(blank=True, null=True)
    classic_bonus_love_coach = models.BooleanField(default=False, blank=True)
    vip_bonus_love_coach = models.BooleanField(default=False, blank=True)
    is_banned = models.BooleanField(default=False, blank=True)
    is_restored = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.user)


def compress(image):
    im = Image.open(image)
    im_io = BytesIO()
    im.save(im_io, 'JPEG', quality=60)
    new_image = File(im_io, name=image.name)
    return new_image


class User_Picture(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name="user_profile_pic")
    picture = models.ImageField(upload_to='user_profile_pic/')
    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.picture:
            new_image = compress(self.picture)
            self.picture = new_image
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user_profile)

    def get_absolute_url(self):
        return reverse('server_edit', kwargs={
            'pk': self.pk
        })


class like_and_dislike(models.Model):
    like_dislike = (
        ('Neutral', 'Neutral'),
        ('Like', 'Like'),
        ('Super_like', 'Super_like'),
        ('Dislike', 'Dislike')
    )
    status = (
        ('True', 'True'),
        ('False', 'False')
    )

    user = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name="like_dislike_profile_going_to_like")
    user_profile_liked_or_dislike = models.ForeignKey(User_Profile, on_delete=models.CASCADE,
                                                      related_name="like_dislike_profile", blank=True, null=True)
    profile_status = models.CharField(max_length=10, blank=True, choices=like_dislike, default='Neutral')
    is_active = models.BooleanField(default=True)
    cross_check_user = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    counter = models.IntegerField(default=0, null=True, blank=True)
    match_seen = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return str(self.user)


class user_block(models.Model):
    reasionchoices = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    )
    block_status = (
        ('True', 'True'),
        ('False', 'False')
    )
    user = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name="user_profile_going_to_block")
    user_profile_block = models.ForeignKey(User_Profile, on_delete=models.CASCADE, related_name="user_profile_block",
                                           blank=True, null=True)
    profile_status = models.CharField(max_length=10, blank=True, choices=block_status, default='False')
    reason = models.CharField(max_length=100, blank=True, choices=reasionchoices)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Countries(models.Model):
    country_name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.country_name


class City(models.Model):
    city_name = models.CharField(max_length=255)
    all_country_name = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.city_name




class FilterHistory(models.Model):

    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE, default= True)
    education = models.CharField(max_length=200, blank=True, null=True)
    kids = models.CharField(max_length=100, blank=True, null=True)
    drink = models.CharField(max_length=100,blank=True, null=True)
    smoke = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=20, blank=True, null=True)
    exercise = models.CharField(max_length=200, blank=True, null=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    interested_age = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    max_height = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)