from django.shortcuts import get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Jengo,Chumba,Mpangaji,Malipo
@login_required(login_url='login')
def hariri_jengo(r,jengo_id):
 j=get_object_or_404(Jengo,id=jengo_id,mmiliki=r.user)
 if r.method=='POST':
  setattr(j,'jina',r.POST.get('jina',getattr(j,'jina')).strip())
  if hasattr(j,'eneo'):setattr(j,'eneo',r.POST.get('eneo','').strip())
  j.save();messages.success(r,'Jengo limehaririwa.')
 return redirect('dashboard')
@login_required(login_url='login')
def hariri_chumba(r,chumba_id):
 c=get_object_or_404(Chumba,id=chumba_id,jengo__mmiliki=r.user)
 if r.method=='POST':
  setattr(c,'namba',r.POST.get('namba',getattr(c,'namba')).strip());k=r.POST.get('kodi_kwa_mwezi','').strip()
  if k:setattr(c,'kodi_kwa_mwezi',k)
  c.save();messages.success(r,'Chumba kimehaririwa.')
 return redirect('dashboard')
@login_required(login_url='login')
def hariri_mpangaji(r,mpangaji_id):
 m=get_object_or_404(Mpangaji,id=mpangaji_id,chumba__jengo__mmiliki=r.user)
 if r.method=='POST':
  setattr(m,'jina_kamili',r.POST.get('jina_kamili',getattr(m,'jina_kamili')).strip());setattr(m,'namba_ya_simu',r.POST.get('namba_ya_simu',getattr(m,'namba_ya_simu')).strip());t=r.POST.get('tarehe_kodi_kuisha','').strip()
  if t:setattr(m,'tarehe_kodi_kuisha',t)
  m.save()
  if m.chumba:
   nc=r.POST.get('namba_chumba','').strip();k=r.POST.get('kodi_kwa_mwezi','').strip()
   if nc:setattr(m.chumba,'namba',nc)
   if k:setattr(m.chumba,'kodi_kwa_mwezi',k)
   m.chumba.save()
  messages.success(r,'Mpangaji amehaririwa.')
 return redirect('dashboard')
@login_required(login_url='login')
def hariri_malipo(r,malipo_id):
 p=get_object_or_404(Malipo,id=malipo_id,mpangaji__chumba__jengo__mmiliki=r.user)
 if r.method=='POST':
  for f in('kiasi','miezi_aliyolipia','njia_ya_malipo','tarehe_ya_malipo'):
   v=r.POST.get(f,'').strip()
   if v:setattr(p,f,v)
  p.save();messages.success(r,'Malipo yamehaririwa.')
 return redirect('dashboard')
