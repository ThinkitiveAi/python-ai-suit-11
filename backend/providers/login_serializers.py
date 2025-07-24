from rest_framework import serializers

class ProviderLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField()
    remember_me = serializers.BooleanField(required=False, default=False)

class PatientLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField()
    remember_me = serializers.BooleanField(required=False, default=False)
    device_info = serializers.DictField(required=False, allow_null=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')
        if not identifier or not password:
            raise serializers.ValidationError('Identifier and password are required.')
        return data
