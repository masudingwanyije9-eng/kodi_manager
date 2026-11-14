from django.contrib import admin
from .models import Jengo, Chumba, Mpangaji, Malipo

admin.site.register(Jengo)
admin.site.register(Chumba)
admin.site.register(Mpangaji)
admin.site.register(Malipo)

from .models import Usajili, Maoni
@admin.register(Usajili)
class UsajiliAdmin(admin.ModelAdmin):
 list_display=('mtumiaji','amelipia','tarehe_kuanza','siku_za_majaribio','tarehe_ya_mwisho_malipo')
 list_editable=('amelipia','siku_za_majaribio','tarehe_ya_mwisho_malipo')
 search_fields=('mtumiaji__username','mtumiaji__email')
@admin.register(Maoni)
class MaoniAdmin(admin.ModelAdmin):
 list_display=('mtumiaji','aina_ya_maoni','ujumbe','tarehe','imesomwa')
 list_filter=('aina_ya_maoni','imesomwa')
 list_editable=('imesomwa',)
