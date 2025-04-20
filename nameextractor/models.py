from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    title = models.CharField(max_length=255, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,blank=True, null=True)

    def __str__(self):
        return self.title


from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploaded_files/")  # Save files in 'uploaded_files/' directory
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Automatically track upload time
    original_name = models.CharField(max_length=255, null=True, blank=True)  # Save the original file name
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,  blank=True, null=True,
                             related_name="uploaded_files")  # Reference to uploading user


    def __str__(self):
        return self.original_name


class PersonDetails(models.Model):
    name = models.CharField(max_length=255)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    source_file = models.ForeignKey(UploadedFile, null=True, blank=True, on_delete=models.CASCADE, related_name='person_details')
    page_numbers = models.CharField(max_length=255)  # e.g., "31,32"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
