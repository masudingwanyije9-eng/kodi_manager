from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usajili, Maoni

def pata_usajili(user):
    obj, _ = Usajili.objects.get_or_create(mtumiaji=user)
    return obj

@login_required(login_url='login')
def tuma_maoni(request):
    if request.method == 'POST':
        aina = request.POST.get('aina_ya_maoni', 'Maboresho').strip()
        ujumbe = request.POST.get('ujumbe', '').strip()
        if ujumbe:
            Maoni.objects.create(mtumiaji=request.user, aina_ya_maoni=aina, ujumbe=ujumbe)
            messages.success(request, 'Asante! Maoni yako yamepokelewa kwa ajili ya maboresho.')
    nxt = request.POST.get('next') or 'dashboard'
    return redirect(nxt)

@login_required(login_url='login')
def muda_umeisha(request):
    u = pata_usajili(request.user)
    if u.ni_hai():
        return redirect('dashboard')
    return render(request, 'usimamizi/muda_umeisha.html', {'usajili': u})
