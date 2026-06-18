from django.db import models
from django.conf import settings


class DailySiteReport(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='site_reports')
    date = models.DateField()
    weather = models.CharField(max_length=100, blank=True)
    workers_present = models.PositiveIntegerField(default=0)
    tasks_completed = models.TextField(blank=True)
    materials_used = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Daily Site Report'
        verbose_name_plural = 'Daily Site Reports'

    def __str__(self):
        return f'{self.project} - {self.date}'


class SiteReportPhoto(models.Model):
    report = models.ForeignKey(DailySiteReport, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='site_reports/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.caption or f'Photo {self.id}'
