from rest_framework import serializers

from apps.journal.models import Timer


class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        exclude = ('task', 'real_time')


class TimerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = ('execution_end',)
