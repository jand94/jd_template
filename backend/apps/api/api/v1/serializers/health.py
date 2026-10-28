from rest_framework import serializers


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


class ReadyCheckSerializer(serializers.Serializer):
    database = serializers.CharField()
    cache = serializers.CharField()


class ReadySerializer(serializers.Serializer):
    status = serializers.CharField()
    checks = ReadyCheckSerializer()
