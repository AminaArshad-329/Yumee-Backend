from django_filters.rest_framework import FilterSet
from core.models import User_Profile


class UserFilter(FilterSet):
    class Meta:
        model = User_Profile
        fields = ['gender', 'interested_in', 'religion', 'education', 'package', 'package_duration']
