from rest_framework import serializers

from apps.journal.models import TimeLog


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('id',)
        extra_kwargs = {
            'started_at': {'write_only': True},
            'duration': {'read_only': True}
        }


class TimeJournalSerializer(serializers.ModelSerializer):
    minutes = serializers.DurationField(source='duration')

    class Meta:
        model = TimeLog
        fields = ('id', 'started_at', 'minutes', 'user')


class TimeLogListSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField()

    class Meta:
        model = TimeLog
        fields = ('id', 'task', 'total_duration', 'user', 'started_at')
