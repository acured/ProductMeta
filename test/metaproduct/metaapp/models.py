from django.db import models

# Create your models here.
class Source(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    details = models.TextField()
    #photo_url = models.URLField()
    source_type = models.CharField(max_length=255)

class Attribute(models.Model):
    #source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="attributes")
    content = models.TextField()
    attribute_type = models.CharField(max_length=255)
    is_target = models.BooleanField()  # True 表示是 target 的属性，False 表示是 source 的属性

class MainMapping(models.Model):
    target_attribute = models.TextField()
    source_attribute = models.TextField()
    description = models.TextField()  # 简短的映射描述
    image_url = models.URLField()

    def __str__(self):
        return f"Mapping: {self.target_attribute} <-> {self.source_attribute}"
