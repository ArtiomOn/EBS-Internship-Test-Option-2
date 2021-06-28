from rest_framework import serializers

from apps.journal.models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('id',)
        extra_kwargs = {
            'started_at': {'write_only': True}
        }


class TimeLogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('id',)
        extra_kwargs = {
            'duration': {'write_only': True}
        }
