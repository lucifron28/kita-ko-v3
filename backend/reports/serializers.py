from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from .models import IncomeReport


class IncomeReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating income reports
    """
    class Meta:
        model = IncomeReport
        fields = [
            'report_type', 'date_from', 'date_to', 'purpose', 
            'purpose_description', 'title'
        ]
    
    def validate(self, attrs):
        """Validate report creation data"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to:
            if date_from >= date_to:
                raise serializers.ValidationError("date_from must be before date_to")
            
            # Check if date range is not too far in the future
            if date_to > timezone.now().date():
                raise serializers.ValidationError("date_to cannot be in the future")
            
            # Check if date range is reasonable (not more than 5 years)
            if (date_to - date_from).days > 1825:  # 5 years
                raise serializers.ValidationError("Date range cannot exceed 5 years")
        
        return attrs
    
    def create(self, validated_data):
        """Create income report with user from context"""
        validated_data['user'] = self.context['request'].user
        
        # Generate title if not provided
        if not validated_data.get('title'):
            date_from = validated_data['date_from']
            date_to = validated_data['date_to']
            purpose = validated_data.get('purpose', 'general')
            validated_data['title'] = f"Preliminary Income Report ({date_from} to {date_to}) - {purpose.replace('_', ' ').title()}"
        
        return super().create(validated_data)


class IncomeReportSerializer(serializers.ModelSerializer):
    """
    Serializer for income report data
    """
    user_name = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    formatted_total_income = serializers.SerializerMethodField()
    formatted_net_income = serializers.SerializerMethodField()
    
    class Meta:
        model = IncomeReport
        fields = [
            'id', 'user_name', 'title', 'report_type', 'date_from', 'date_to',
            'purpose', 'purpose_description', 'summary', 'total_income',
            'total_expenses', 'net_income', 'average_monthly_income',
            'formatted_total_income', 'formatted_net_income',
            'income_breakdown', 'expense_breakdown', 'monthly_trends',
            'data_sources', 'transaction_count', 'ai_insights',
            'anomalies_detected', 'confidence_score', 'pdf_url',
            'file_size', 'verification_code', 'status', 'generation_error',
            'is_public', 'is_expired', 'download_count', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'summary', 'total_income', 'total_expenses', 'net_income',
            'average_monthly_income', 'income_breakdown', 'expense_breakdown',
            'monthly_trends', 'data_sources', 'transaction_count',
            'ai_insights', 'anomalies_detected', 'confidence_score',
            'file_size', 'verification_code', 'status', 'generation_error',
            'download_count', 'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's full name"""
        return obj.user.full_name
    
    def get_pdf_url(self, obj):
        """Get PDF file URL if available"""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None
    
    def get_formatted_total_income(self, obj):
        """Get formatted total income"""
        return f"₱{obj.total_income:,.2f}"
    
    def get_formatted_net_income(self, obj):
        """Get formatted net income"""
        return f"₱{obj.net_income:,.2f}"


class IncomeReportListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing income reports
    """
    formatted_total_income = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = IncomeReport
        fields = [
            'id', 'title', 'report_type', 'date_from', 'date_to',
            'purpose', 'total_income', 'formatted_total_income',
            'net_income', 'status', 'is_expired', 'verification_code',
            'created_at', 'completed_at'
        ]
    
    def get_formatted_total_income(self, obj):
        """Get formatted total income"""
        return f"₱{obj.total_income:,.2f}"


class ReportGenerationRequestSerializer(serializers.Serializer):
    """
    Serializer for report generation requests
    """
    report_id = serializers.UUIDField()
    include_ai_analysis = serializers.BooleanField(default=True)
    include_charts = serializers.BooleanField(default=False)  # For future enhancement
    
    def validate_report_id(self, value):
        """Validate that the report exists and belongs to the user"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        try:
            report = IncomeReport.objects.get(id=value, user=request.user)
            return value
        except IncomeReport.DoesNotExist:
            raise serializers.ValidationError("Report not found or access denied")


class ReportVerificationSerializer(serializers.Serializer):
    """
    Serializer for report verification
    """
    verification_code = serializers.CharField(max_length=20)
    
    def validate_verification_code(self, value):
        """Validate verification code format"""
        if not value.isalnum():
            raise serializers.ValidationError("Invalid verification code format")
        return value.upper()


class ReportSharingSerializer(serializers.ModelSerializer):
    """
    Serializer for report sharing settings
    """
    class Meta:
        model = IncomeReport
        fields = ['is_public', 'expires_at']
    
    def validate_expires_at(self, value):
        """Validate expiration date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value
