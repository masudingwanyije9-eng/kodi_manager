from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Jengo(models.Model):
    jina = models.CharField(max_length=100)
    eneo = models.CharField(max_length=100)
    mmiliki = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.jina


class Chumba(models.Model):
    jengo = models.ForeignKey(Jengo, on_delete=models.CASCADE)
    namba = models.CharField(max_length=20)
    kodi_kwa_mwezi = models.PositiveIntegerField()
    kimejaa = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.jengo.jina} - {self.namba}"


class Mpangaji(models.Model):
    chumba = models.ForeignKey(Chumba, on_delete=models.SET_NULL, null=True, blank=True)
    jina_kamili = models.CharField(max_length=100)
    namba_ya_simu = models.CharField(max_length=15)
    tarehe_kuingia = models.DateField(default=timezone.now)
    tarehe_kodi_kuisha = models.DateField(null=True, blank=True)
    yupopo = models.BooleanField(default=True)
    tarehe_kuondoka = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.jina_kamili


class Malipo(models.Model):
    NJIA_CHOICES = [
        ('M-Pesa', 'M-Pesa'),
        ('Tigo Pesa', 'Mixx by Yas (Tigo Pesa)'),
        ('Airtel Money', 'Airtel Money'),
        ('Halopesa', 'Halopesa'),
        ('T-Pesa', 'T-Pesa'),
        ('Selcom Pay', 'Selcom Pay'),
        ('AzamPesa', 'AzamPesa'),
        ('Benki', 'Benki'),
        ('Taslimu', 'Taslimu'),
        ('Nyingine', 'Njia Nyingine'),
    ]
    mpangaji = models.ForeignKey(Mpangaji, on_delete=models.CASCADE)
    kiasi = models.PositiveIntegerField()
    miezi_aliyolipia = models.PositiveIntegerField(default=1)
    njia_ya_malipo = models.CharField(max_length=30, choices=NJIA_CHOICES, default='Taslimu')
    tarehe_ya_malipo = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.mpangaji.jina_kamili} - {self.kiasi}"


from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Usajili(models.Model):
    mtumiaji = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usajili')
    tarehe_kuanza = models.DateTimeField(default=timezone.now)
    siku_za_majaribio = models.IntegerField(default=15)
    amelipia = models.BooleanField(default=False)
    tarehe_ya_mwisho_malipo = models.DateField(null=True, blank=True)

    def siku_zilizobaki(self):
        if self.amelipia:
            if self.tarehe_ya_mwisho_malipo:
                baki = (self.tarehe_ya_mwisho_malipo - timezone.now().date()).days
                return max(0, baki)
            return 999
        mwisho = self.tarehe_kuanza + timedelta(days=self.siku_za_majaribio)
        baki = (mwisho - timezone.now()).days
        return max(0, baki)

    def ni_hai(self):
        if self.mtumiaji.is_superuser:
            return True
        if self.amelipia:
            if self.tarehe_ya_mwisho_malipo:
                return self.tarehe_ya_mwisho_malipo >= timezone.now().date()
            return True
        return timezone.now() <= (self.tarehe_kuanza + timedelta(days=self.siku_za_majaribio))

    def __str__(self):
        hali = "Amelipia" if self.amelipia else f"Trial ({self.siku_zilizobaki()} siku)"
        return f"{self.mtumiaji.username} - {hali}"

class Maoni(models.Model):
    AINA_CHOICES = [
        ('Maboresho', 'Pendekezo la Maboresho'),
        ('Hitilafu', 'Tatizo / Hitilafu'),
        ('Pongezi', 'Sifa / Pongezi'),
        ('Swali', 'Swali / Msaada'),
    ]
    mtumiaji = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aina_ya_maoni = models.CharField(max_length=30, choices=AINA_CHOICES, default='Maboresho')
    ujumbe = models.TextField()
    tarehe = models.DateTimeField(auto_now_add=True)
    imesomwa = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mtumiaji.username} ({self.aina_ya_maoni}) - {self.tarehe:%Y-%m-%d}"
