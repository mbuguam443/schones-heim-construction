from django.db import models
from django.conf import settings
from django.utils import timezone


class CompanyDocument(models.Model):
    class DocType(models.TextChoices):
        LETTER = 'letter', 'Letter'
        REPORT = 'report', 'Report'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        FINAL = 'final', 'Final'
        ARCHIVED = 'archived', 'Archived'

    doc_type = models.CharField(max_length=10, choices=DocType.choices, default=DocType.LETTER)
    reference_number = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, help_text='Rich-text HTML content')

    recipient_name = models.CharField(max_length=200, blank=True)
    recipient_organization = models.CharField(max_length=200, blank=True)
    recipient_address = models.TextField(blank=True)
    subject = models.CharField(max_length=300, blank=True)
    report_date = models.DateField(null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    prepared_by = models.CharField(max_length=200, blank=True)
    report_period = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    show_signature = models.BooleanField(default=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_doc_type_display()} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_ref_number()
        super().save(*args, **kwargs)

    def _generate_ref_number(self):
        year = timezone.now().year
        prefix = 'LET' if self.doc_type == self.DocType.LETTER else 'RPT'
        last = CompanyDocument.objects.filter(
            doc_type=self.doc_type,
            reference_number__startswith=f'SHB/{prefix}/{year}/'
        ).order_by('-reference_number').first()
        if last:
            try:
                last_num = int(last.reference_number.split('/')[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
        return f'SHB/{prefix}/{year}/{next_num:03d}'


class DocumentCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Document Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Document(models.Model):
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, related_name='documents')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, blank=True, default='1.0')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def cancel(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self):
        self.is_active = True
        self.save(update_fields=['is_active'])

    def filename(self):
        import os
        return os.path.basename(self.file.name)
