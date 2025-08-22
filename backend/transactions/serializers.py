from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import magic
import os
from .models import FileUpload, Transaction


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for file uploads with validation
    """
    file = serializers.FileField(write_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'file', 'file_url', 'original_filename', 'file_size',
            'file_type', 'source', 'processing_status', 'processing_error',
            'date_range_start', 'date_range_end', 'description',
            'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_size', 'processing_status',
            'processing_error', 'created_at', 'updated_at', 'processed_at'
        ]
    
    def get_file_url(self, obj):
        """Get the file URL if it exists"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def validate_file(self, file):
        """Validate uploaded file"""
        # Check file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
            )
        
        # Check file type using python-magic
        file_content = file.read(1024)  # Read first 1KB for type detection
        file.seek(0)  # Reset file pointer
        
        mime_type = magic.from_buffer(file_content, mime=True)
        
        if mime_type not in settings.ALLOWED_FILE_TYPES:
            raise serializers.ValidationError(
                f"File type '{mime_type}' not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        return file
    
    def create(self, validated_data):
        """Create file upload instance"""
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        
        # Extract file info
        file = validated_data['file']
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for transaction data
    """
    file_upload_info = serializers.SerializerMethodField(read_only=True)
    formatted_amount = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'date', 'amount', 'formatted_amount', 'currency', 'description',
            'reference_number', 'transaction_type', 'category', 'subcategory',
            'ai_categorized', 'ai_confidence', 'ai_reasoning',
            'manually_verified', 'manual_notes', 'source_platform',
            'counterparty', 'is_anomaly', 'anomaly_reason', 'is_recurring',
            'file_upload_info', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'ai_categorized', 'ai_confidence', 'ai_reasoning',
            'is_anomaly', 'anomaly_reason', 'is_recurring',
            'created_at', 'updated_at'
        ]
    
    def get_file_upload_info(self, obj):
        """Get basic info about the source file upload"""
        if obj.file_upload:
            return {
                'id': obj.file_upload.id,
                'filename': obj.file_upload.original_filename,
                'source': obj.file_upload.source,
                'file_type': obj.file_upload.file_type
            }
        return None
    
    def get_formatted_amount(self, obj):
        """Get formatted amount with currency symbol"""
        if obj.currency == 'PHP':
            return f"₱{obj.amount:,.2f}"
        return f"{obj.currency} {obj.amount:,.2f}"


class TransactionBulkUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk updating transactions
    """
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    updates = serializers.DictField(
        child=serializers.CharField(),
        required=True
    )
    
    def validate_updates(self, value):
        """Validate that only allowed fields are being updated"""
        allowed_fields = [
            'category', 'subcategory', 'transaction_type',
            'manually_verified', 'manual_notes'
        ]
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    f"Field '{field}' cannot be bulk updated. Allowed fields: {allowed_fields}"
                )
        
        return value


class FileUploadStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for checking file upload processing status
    """
    transaction_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'processing_status', 'processing_error',
            'transaction_count', 'processed_at'
        ]
    
    def get_transaction_count(self, obj):
        """Get count of transactions extracted from this file"""
        return obj.transactions.count()
