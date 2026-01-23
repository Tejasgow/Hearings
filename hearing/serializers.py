from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Hearing, HearingUpdate, UserRole


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
    
    def get_role(self, obj):
        try:
            return obj.role.get_role_display()
        except UserRole.DoesNotExist:
            return None


class HearingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for HearingUpdate model"""
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    updated_by_email = serializers.CharField(source='updated_by.email', read_only=True)
    
    class Meta:
        model = HearingUpdate
        fields = [
            'id',
            'hearing',
            'updated_by',
            'updated_by_username',
            'updated_by_email',
            'update_type',
            'title',
            'description',
            'is_important',
            'visible_to_advocate',
            'visible_to_client',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HearingSerializer(serializers.ModelSerializer):
    """Serializer for Hearing model"""
    advocate_name = serializers.CharField(source='advocate.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    advocate_email = serializers.CharField(source='advocate.email', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    updates = HearingUpdateSerializer(many=True, read_only=True)
    
    class Meta:
        model = Hearing
        fields = [
            'id',
            'title',
            'description',
            'hearing_date',
            'location',
            'case_number',
            'advocate',
            'advocate_name',
            'advocate_email',
            'client',
            'client_name',
            'client_email',
            'status',
            'updates',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HearingDetailSerializer(HearingSerializer):
    """Extended serializer for detailed hearing information"""
    updates_count = serializers.SerializerMethodField()
    recent_updates = serializers.SerializerMethodField()
    
    class Meta(HearingSerializer.Meta):
        fields = HearingSerializer.Meta.fields + ['updates_count', 'recent_updates']
    
    def get_updates_count(self, obj):
        return obj.updates.count()
    
    def get_recent_updates(self, obj):
        recent = obj.updates.all()[:5]
        return HearingUpdateSerializer(recent, many=True).data


class CreateHearingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating hearing updates"""
    
    class Meta:
        model = HearingUpdate
        fields = [
            'hearing',
            'update_type',
            'title',
            'description',
            'is_important',
            'visible_to_advocate',
            'visible_to_client',
        ]
    
    def create(self, validated_data):
        # Set the updated_by field to the current user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)
