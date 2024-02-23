from django.db import models


# Create your models here.
class Users(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=20)
    birth_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email} {self.password} {self.birth_date}"
