from django.contrib import admin

# Register your models here.
from .models import FilterHistory, User_Profile, User_Picture, like_and_dislike, user_block, Countries, City


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'your_name', 'email', 'gender', 'interested_in', 'age', 'date_of_birth', 'kids',
                    'package', 'package_date_start',
                    'package_date_end', 'remaining_days_in_exp', 'city', 'is_banned', 'is_restored', 'appear_to_other']

    class Meta:
        model = User_Profile
        fields = '__all__'


class LikeProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user_profile_liked_or_dislike', 'counter', 'profile_status', 'is_active',
                    'cross_check_user', 'match_seen']

    class Meta:
        model = like_and_dislike
        fields = '__all__'


admin.site.register(User_Profile, UserProfileAdmin)
admin.site.register(User_Picture)
admin.site.register(like_and_dislike, LikeProfileAdmin)
admin.site.register(user_block)
admin.site.register(Countries)
admin.site.register(City)
admin.site.register(FilterHistory)