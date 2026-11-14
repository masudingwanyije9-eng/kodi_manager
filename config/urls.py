from django.contrib import admin
from django.urls import path
from usimamizi.views import dashboard,login_view,logout_view,mpangaji_hama,risiti_malipo,signup_view
from usimamizi.edit_views import hariri_jengo,hariri_chumba,hariri_mpangaji,hariri_malipo
from usimamizi.saas_views import tuma_maoni,muda_umeisha
urlpatterns=[path('admin/',admin.site.urls),path('',dashboard,name='dashboard'),path('jisajili/',signup_view,name='signup'),path('ingia/',login_view,name='login'),path('toka/',logout_view,name='logout'),path('hama/<int:mpangaji_id>/',mpangaji_hama,name='mpangaji_hama'),path('risiti/<int:malipo_id>/',risiti_malipo,name='risiti_malipo'),path('hariri-jengo/<int:jengo_id>/',hariri_jengo,name='hariri_jengo'),path('hariri-chumba/<int:chumba_id>/',hariri_chumba,name='hariri_chumba'),path('hariri-mpangaji/<int:mpangaji_id>/',hariri_mpangaji,name='hariri_mpangaji'),path('hariri-malipo/<int:malipo_id>/',hariri_malipo,name='hariri_malipo'),path('tuma-maoni/',tuma_maoni,name='tuma_maoni'),path('muda-umeisha/',muda_umeisha,name='muda_umeisha')]
