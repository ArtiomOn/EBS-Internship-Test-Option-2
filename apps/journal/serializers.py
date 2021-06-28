from rest_framework import serializers

from apps.journal.models import TimeLog
from apps.tasks.models import Task


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
            'duration': {'read_only': True}
        }


class TimeJournalSerializer(serializers.ModelSerializer):
    minutes = serializers.DurationField(source='duration')

    class Meta:
        model = TimeLog
        fields = ('id', 'minutes')


class TimeJournalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'


class TimeProfileListSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField()

    class Meta:
        model = TimeLog
        fields = ('id', 'total_duration',)
