from .saas_views import pata_usajili
import calendar
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Sum
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Jengo, Chumba, Mpangaji, Malipo

JengoForm = modelform_factory(Jengo, exclude=['mmiliki'])
MpangajiForm = modelform_factory(Mpangaji, exclude=['yupopo', 'tarehe_kuondoka'])
MalipoForm = modelform_factory(Malipo, exclude=['tarehe_ya_malipo'])
ChumbaForm = modelform_factory(Chumba, exclude=['kimejaa'])


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Karibu {user.username}! Akaunti yako imetengenezwa kikamilifu.")
            return redirect('dashboard')
    return render(request, 'usimamizi/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    return render(request, 'usimamizi/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def ongeza_miezi(tarehe_awali, miezi):
    mwezi_mpya = tarehe_awali.month - 1 + miezi
    mwaka_mpya = tarehe_awali.year + mwezi_mpya // 12
    mwezi_mwisho = mwezi_mpya % 12 + 1
    siku_mwisho = min(tarehe_awali.day, calendar.monthrange(mwaka_mpya, mwezi_mwisho)[1])
    return tarehe_awali.replace(year=mwaka_mpya, month=mwezi_mwisho, day=siku_mwisho)


@login_required(login_url='login')
def dashboard(request):
    _usajili = pata_usajili(request.user)
    if not _usajili.ni_hai():
        return redirect('muda_umeisha')
    leo = timezone.now().date()
    tahadhari_tarehe = leo + timedelta(days=7)

    if request.user.is_superuser:
        Jengo.objects.filter(mmiliki__isnull=True).update(mmiliki=request.user)

    majengo_user = Jengo.objects.filter(mmiliki=request.user)

    jengo_form = JengoForm()
    chumba_form = ChumbaForm()
    chumba_form.fields['jengo'].queryset = majengo_user

    mpangaji_form = MpangajiForm()
    mpangaji_form.fields['chumba'].queryset = Chumba.objects.filter(jengo__mmiliki=request.user, kimejaa=False)

    malipo_form = MalipoForm()
    malipo_form.fields['mpangaji'].queryset = Mpangaji.objects.filter(chumba__jengo__mmiliki=request.user, yupopo=True)

    fungua_modal = None

    if request.method == 'POST':
        aina = request.POST.get('aina_ya_fomu')
        if aina == 'jengo':
            jengo_form = JengoForm(request.POST)
            if jengo_form.is_valid():
                jengo_mpya = jengo_form.save(commit=False)
                jengo_mpya.mmiliki = request.user
                jengo_mpya.save()
                messages.success(request, f"Jengo '{jengo_mpya}' limeongezwa kikamilifu!")
                return redirect('dashboard')
            fungua_modal = 'modalJengo'

        elif aina == 'badili_idadi_vyumba':
            jengo_obj = get_object_or_404(Jengo, id=request.POST.get('jengo_id'), mmiliki=request.user)
            try:
                jumla_mpya = max(0, int(request.POST.get('jumla_vyumba', 0)))
                vilivyojaa_vipya = max(0, int(request.POST.get('vilivyochukuliwa', 0)))
            except ValueError:
                jumla_mpya = 0
                vilivyojaa_vipya = 0

            vyumba_qs = Chumba.objects.filter(jengo=jengo_obj)
            sasa = vyumba_qs.count()

            if jumla_mpya > sasa:
                existing_names = set(vyumba_qs.values_list('namba', flat=True))
                chumba_mfano = vyumba_qs.first()
                bei_msingi = chumba_mfano.kodi_kwa_mwezi if chumba_mfano else 0

                namba_index = sasa + 1
                for _ in range(jumla_mpya - sasa):
                    jina_chumba = f"Chumba {namba_index}"
                    while jina_chumba in existing_names:
                        namba_index += 1
                        jina_chumba = f"Chumba {namba_index}"
                    existing_names.add(jina_chumba)
                    Chumba.objects.create(
                        jengo=jengo_obj,
                        namba=jina_chumba,
                        kodi_kwa_mwezi=bei_msingi,
                        kimejaa=False,
                    )
                    namba_index += 1

            elif jumla_mpya < sasa:
                za_kufuta = sasa - jumla_mpya
                ids_za_kufuta = list(vyumba_qs.filter(kimejaa=False).order_by('-id').values_list('id', flat=True)[:za_kufuta])
                Chumba.objects.filter(id__in=ids_za_kufuta).delete()

            vyumba_qs = Chumba.objects.filter(jengo=jengo_obj)
            vilivyojaa_vipya = min(vilivyojaa_vipya, vyumba_qs.count())
            vilivyojaa_sasa = vyumba_qs.filter(kimejaa=True).count()

            if vilivyojaa_vipya > vilivyojaa_sasa:
                ongeza = vilivyojaa_vipya - vilivyojaa_sasa
                ids = list(vyumba_qs.filter(kimejaa=False).order_by('id').values_list('id', flat=True)[:ongeza])
                Chumba.objects.filter(id__in=ids).update(kimejaa=True)
            elif vilivyojaa_vipya < vilivyojaa_sasa:
                punguza = vilivyojaa_sasa - vilivyojaa_vipya
                vyenye_wapangaji_ids = Mpangaji.objects.filter(yupopo=True, chumba__jengo=jengo_obj).values_list('chumba_id', flat=True)
                wazi_ids = list(
                    vyumba_qs.filter(kimejaa=True).exclude(id__in=vyenye_wapangaji_ids).order_by('-id').values_list('id', flat=True)[:punguza]
                )
                if len(wazi_ids) < punguza:
                    baki = punguza - len(wazi_ids)
                    extra = list(
                        vyumba_qs.filter(kimejaa=True).exclude(id__in=wazi_ids).order_by('-id').values_list('id', flat=True)[:baki]
                    )
                    wazi_ids.extend(extra)
                Chumba.objects.filter(id__in=wazi_ids).update(kimejaa=False)

            messages.success(request, f"Idadi ya vyumba vya '{jengo_obj}' imesasishwa!")
            return redirect('dashboard')

        elif aina == 'malipo':
            malipo_form = MalipoForm(request.POST)
            malipo_form.fields['mpangaji'].queryset = Mpangaji.objects.filter(chumba__jengo__mmiliki=request.user, yupopo=True)
            if malipo_form.is_valid():
                malipo_mpya = malipo_form.save()
                mpangaji = malipo_mpya.mpangaji
                tarehe_msingi = mpangaji.tarehe_kodi_kuisha or leo
                mpangaji.tarehe_kodi_kuisha = ongeza_miezi(tarehe_msingi, malipo_mpya.miezi_aliyolipia)
                mpangaji.save()
                messages.success(
                    request,
                    f"Malipo yamerekodiwa! Kodi ya {mpangaji.jina_kamili} sasa itaisha tarehe {mpangaji.tarehe_kodi_kuisha}."
                )
                return redirect('dashboard')
            fungua_modal = 'modalMalipo'

        elif aina == 'mpangaji':
            mpangaji_form = MpangajiForm(request.POST)
            mpangaji_form.fields['chumba'].queryset = Chumba.objects.filter(jengo__mmiliki=request.user, kimejaa=False)
            if mpangaji_form.is_valid():
                jina_mpangaji = ' '.join(mpangaji_form.cleaned_data['jina_kamili'].split())
                if Mpangaji.objects.filter(chumba__jengo__mmiliki=request.user, yupopo=True, jina_kamili__iexact=jina_mpangaji).exists():
                    messages.warning(request, f"Mpangaji '{jina_mpangaji}' tayari amesajiliwa na yupo!")
                    return redirect('dashboard')
                mpangaji_mpya = mpangaji_form.save(commit=False)
                mpangaji_mpya.jina_kamili = jina_mpangaji
                mpangaji_mpya.yupopo = True
                mpangaji_mpya.save()
                if mpangaji_mpya.chumba:
                    mpangaji_mpya.chumba.kimejaa = True
                    mpangaji_mpya.chumba.save()
                messages.success(request, f"Mpangaji {mpangaji_mpya.jina_kamili} amesajiliwa kikamilifu!")
                return redirect('dashboard')
            fungua_modal = 'modalMpangaji'

        elif aina == 'chumba':
            chumba_form = ChumbaForm(request.POST)
            chumba_form.fields['jengo'].queryset = majengo_user
            if chumba_form.is_valid():
                chumba_form.save()
                messages.success(request, "Chumba kipya kimeongezwa kikamilifu!")
                return redirect('dashboard')
            fungua_modal = 'modalChumba'

    jengo_lililochaguliwa = request.GET.get('jengo', '')
    vyumba_qs = Chumba.objects.filter(jengo__mmiliki=request.user)
    wapangaji_qs = Mpangaji.objects.filter(chumba__jengo__mmiliki=request.user, yupopo=True).order_by('tarehe_kodi_kuisha')
    malipo_qs = Malipo.objects.filter(mpangaji__chumba__jengo__mmiliki=request.user).order_by('-tarehe_ya_malipo', '-id')

    if jengo_lililochaguliwa:
        vyumba_qs = vyumba_qs.filter(jengo_id=jengo_lililochaguliwa)
        wapangaji_qs = wapangaji_qs.filter(chumba__jengo_id=jengo_lililochaguliwa)
        malipo_qs = malipo_qs.filter(mpangaji__chumba__jengo_id=jengo_lililochaguliwa)

    jumla_vyumba = vyumba_qs.count()
    vyumba_vilivyojaa = vyumba_qs.filter(kimejaa=True).count()
    vyumba_wazi_list = vyumba_qs.filter(kimejaa=False)
    vyumba_wazi = vyumba_wazi_list.count()

    takwimu_majengo = []
    for j in majengo_user:
        vyumba_jengo = Chumba.objects.filter(jengo=j)
        takwimu_majengo.append({
            'jengo': j,
            'jumla': vyumba_jengo.count(),
            'vilivyojaa': vyumba_jengo.filter(kimejaa=True).count(),
            'wazi': vyumba_jengo.filter(kimejaa=False).count(),
        })

    mapato_mwezi_huu = (
        malipo_qs.filter(tarehe_ya_malipo__year=leo.year, tarehe_ya_malipo__month=leo.month)
        .aggregate(jumla=Sum('kiasi'))['jumla'] or 0
    )
    jumla_mapato = malipo_qs.aggregate(jumla=Sum('kiasi'))['jumla'] or 0

    context = {
        'majengo': majengo_user,
        'takwimu_majengo': takwimu_majengo,
        'jengo_lililochaguliwa': jengo_lililochaguliwa,
        'jumla_vyumba': jumla_vyumba,
        'vyumba_vilivyojaa': vyumba_vilivyojaa,
        'vyumba_wazi': vyumba_wazi,
        'vyumba_wazi_list': vyumba_wazi_list,
        'mapato_mwezi_huu': mapato_mwezi_huu,
        'jumla_mapato': jumla_mapato,
        'wapangaji': wapangaji_qs,
        'malipo': malipo_qs[:20],
        'leo': leo,
        'tahadhari_tarehe': tahadhari_tarehe,
        'vyumba':Chumba.objects.filter(jengo__mmiliki=request.user).select_related('jengo'),'usajili': _usajili,'jengo_form': jengo_form,
        'mpangaji_form': mpangaji_form,
        'malipo_form': malipo_form,
        'chumba_form': chumba_form,
        'fungua_modal': fungua_modal,
    }
    return render(request, 'usimamizi/dashboard.html', context)


@login_required(login_url='login')
def mpangaji_hama(request, mpangaji_id):
    if request.method == 'POST':
        mpangaji = get_object_or_404(Mpangaji, id=mpangaji_id, chumba__jengo__mmiliki=request.user)
        mpangaji.yupopo = False
        mpangaji.tarehe_kuondoka = timezone.now().date()
        mpangaji.save()
        if mpangaji.chumba:
            chumba = mpangaji.chumba
            chumba.kimejaa = False
            chumba.save()
        messages.success(request, f"{mpangaji.jina_kamili} ameondolewa na chumba sasa kipo wazi.")
    return redirect('dashboard')


@login_required(login_url='login')
def risiti_malipo(request, malipo_id):
    malipo = get_object_or_404(Malipo, id=malipo_id, mpangaji__chumba__jengo__mmiliki=request.user)
    return render(request, 'usimamizi/risiti.html', {'malipo': malipo})
