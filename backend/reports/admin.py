from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import IncomeReport

@admin.register(IncomeReport)
class IncomeReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'status', 'signature_verification_status', 
        'total_income', 'created_at', 'signature_actions'
    ]
    list_filter = [
        'status', 'signature_verification_status', 'is_signature_submitted',
        'purpose', 'report_type', 'created_at'
    ]
    search_fields = ['title', 'user__email', 'verification_code', 'purpose_description']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'completed_at', 'document_hash',
        'verification_code', 'access_token', 'file_size', 'download_count',
        'signature_submitted_at', 'qr_code_url', 'verification_link'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'status', 'created_at', 'updated_at')
        }),
        ('Report Configuration', {
            'fields': ('report_type', 'date_from', 'date_to', 'purpose', 'purpose_description')
        }),
        ('Financial Data', {
            'fields': ('total_income', 'total_expenses', 'net_income', 'average_monthly_income', 'transaction_count')
        }),
        ('File Information', {
            'fields': ('pdf_file', 'file_size', 'document_hash', 'download_count')
        }),
        ('Verification & QR Code', {
            'fields': (
                'verification_code', 'qr_code_url', 'verification_link',
                'is_signature_submitted', 'signature_verification_status',
                'signature_submitted_at', 'signature_approved_at', 'signature_approved_by',
                'admin_notes'
            )
        }),
        ('Access Control', {
            'fields': ('is_public', 'access_token', 'expires_at')
        }),
    )
    
    def signature_actions(self, obj):
        """Display action buttons for signature verification"""
        if not obj.is_signature_submitted:
            return format_html('<span style="color: gray;">Not submitted</span>')
        
        if obj.signature_verification_status == 'pending':
            approve_url = f"/admin/approve-signature/{obj.id}/"
            reject_url = f"/admin/reject-signature/{obj.id}/"
            return format_html(
                '<a href="{}" class="button" style="background: green; color: white; padding: 5px 10px; margin-right: 5px;">Approve</a>'
                '<a href="{}" class="button" style="background: red; color: white; padding: 5px 10px;">Reject</a>',
                approve_url, reject_url
            )
        elif obj.signature_verification_status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">✓ Approved</span>')
        elif obj.signature_verification_status == 'rejected':
            return format_html('<span style="color: red; font-weight: bold;">✗ Rejected</span>')
        
        return '-'
    
    def verification_link(self, obj):
        """Display clickable verification link"""
        if obj.qr_code_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: blue;">{}</a>',
                obj.qr_code_url, obj.qr_code_url
            )
        return '-'
    
    signature_actions.short_description = 'Signature Actions'
    verification_link.short_description = 'Public Verification Link'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('approve-signature/<uuid:report_id>/', 
                 self.admin_site.admin_view(self.approve_signature_view),
                 name='approve_signature'),
            path('reject-signature/<uuid:report_id>/',
                 self.admin_site.admin_view(self.reject_signature_view), 
                 name='reject_signature'),
        ]
        return custom_urls + urls
    
    def approve_signature_view(self, request, report_id):
        """Admin view to approve signature"""
        try:
            report = IncomeReport.objects.get(id=report_id)
            
            if request.method == 'POST':
                notes = request.POST.get('notes', '')
                report.approve_signature(request.user, notes)
                messages.success(request, f'Document "{report.title}" signature approved successfully!')
                return redirect('admin:reports_incomereport_changelist')
            
            # Show confirmation form
            context = {
                'title': f'Approve Signature for "{report.title}"',
                'report': report,
                'action': 'approve'
            }
            return render(request, 'admin/signature_action_confirm.html', context)
            
        except IncomeReport.DoesNotExist:
            messages.error(request, 'Report not found.')
            return redirect('admin:reports_incomereport_changelist')
    
    def reject_signature_view(self, request, report_id):
        """Admin view to reject signature"""
        try:
            report = IncomeReport.objects.get(id=report_id)
            
            if request.method == 'POST':
                notes = request.POST.get('notes', '')
                report.reject_signature(request.user, notes)
                messages.success(request, f'Document "{report.title}" signature rejected.')
                return redirect('admin:reports_incomereport_changelist')
            
            # Show confirmation form
            context = {
                'title': f'Reject Signature for "{report.title}"',
                'report': report,
                'action': 'reject'
            }
            return render(request, 'admin/signature_action_confirm.html', context)
            
        except IncomeReport.DoesNotExist:
            messages.error(request, 'Report not found.')
            return redirect('admin:reports_incomereport_changelist')
