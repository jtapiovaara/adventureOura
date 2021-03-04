from django.db import models


class Sportdays(models.Model):
    DAYS_CHOICES = [
        ('0', 'Ma'),
        ('1', 'Ti'),
        ('2', 'Ke'),
        ('3', 'To'),
        ('4', 'Pe'),
        ('5', 'La'),
        ('6', 'Su'),
    ]
    days = models.CharField(max_length=1, blank=True, choices=DAYS_CHOICES)

    def __str__(self):
        return self.days


class Ourauser(models.Model):
    firstname = models.CharField(max_length=32, blank=True)
    lastname = models.CharField(max_length=32, blank=True)
    username = models.CharField(max_length=24, blank=True)
    ourakey = models.CharField(max_length=64, blank=True)
    sportdays = models.ManyToManyField('Sportdays', blank=True)
    tintensity = models.IntegerField(blank=True, null=True, default=2)

    def __str__(self):
        return self.firstname


class Hqmessages(models.Model):
    shortdesc = models.CharField(max_length=8, blank=True)
    meaning = models.CharField(max_length=32, blank=True)
    longdesc = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.shortdesc

