from django.db import models
import json

class RTCData(models.Model):
    survey_number = models.CharField(max_length=100)
    surnoc = models.CharField(max_length=100)
    hissa = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    hobli = models.CharField(max_length=100)
    taluk = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    screenshot_path = models.CharField(max_length=255, blank=True, null=True)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.survey_number} - {self.village}"

    class Meta:
        verbose_name = "RTC Data"
        verbose_name_plural = "RTC Data"

class RTCDocument(models.Model):
    rtc_data = models.ForeignKey(RTCData, on_delete=models.CASCADE, related_name='documents')
    period = models.CharField(max_length=100)
    period_text = models.CharField(max_length=255)
    year = models.CharField(max_length=100)
    year_text = models.CharField(max_length=100)
    image_data = models.BinaryField(blank=True, null=True)
    screenshot_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.period_text} - {self.year_text}"

    class Meta:
        verbose_name = "RTC Document"
        verbose_name_plural = "RTC Documents"
