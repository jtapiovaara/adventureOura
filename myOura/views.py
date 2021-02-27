import os
import requests
import datetime

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.admin import User
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Ourauser, Sportdays


def logout(request):
    logout(request)


@login_required
def ouraapi(request):
    """
    2021-01-09 Päätös hakea aina kaikista rajapinnoista 'kaikki' data. Vaihtoehtona olisi hakea vain eilisestä eteenpäin.
    Oli käytössä Sleep- ja Readiness- rajapinnoissa.  Voi muuttaa takaisin jos tarvis, toiminnot #-merkitty
    """
    global sleepstory
    # omaouraapi = OURA_API
    kayttaja = request.user.username
    assert isinstance(Ourauser.objects.get(username=kayttaja).ourakey, object)
    omaouraapi = Ourauser.objects.get(username=kayttaja).ourakey
    you = Ourauser.objects.get(username=kayttaja).firstname

    today = datetime.date.today()
    # eilinen = str(today - datetime.timedelta(days=1))

    # url_sleep = 'https://api.ouraring.com/v1/sleep?start=' + eilinen + '&access_token=' + omaouraapi
    # url_ready = 'https://api.ouraring.com/v1/readiness?start=' + eilinen + '&access_token=' + omaouraapi
    url_user = 'https://api.ouraring.com/v1/userinfo?access_token=' + omaouraapi
    url_sleep = 'https://api.ouraring.com/v1/sleep?&access_token=' + omaouraapi
    url_active = 'https://api.ouraring.com/v1/activity?access_token=' + omaouraapi
    url_ready = 'https://api.ouraring.com/v1/readiness?&access_token=' + omaouraapi
    url_bedtime = 'https://api.ouraring.com/v1/bedtime?access_token=' + omaouraapi
    u = requests.get(url_user).json()
    s = requests.get(url_sleep).json()
    a = requests.get(url_active).json()
    r = requests.get(url_ready).json()
    b = requests.get(url_bedtime).json()

# Käyttäjätietoje

    # BMI (u)
    height = float(u['height']) / 100
    weight = float(u['weight'])
    bmi = round(weight / (height * height), 2)

# Unenlaatu

    # Syvän unen määrä viime yönä (s)
    sleeptotal = s['sleep'][0]['total']/60
    deepsleepamount = s['sleep'][-1]['deep']/60
    # deepscore = s['sleep'][0]['score_deep']
    deepsleeppercentage = round(deepsleepamount/sleeptotal*100, 1)
    if deepsleeppercentage < 12:
        sleepstory = ', mikä on liian vähän'
    if 12 <= deepsleeppercentage < 17:
        sleepstory = ', mikä on melkein riittävästi'
    if deepsleeppercentage >= 17:
        sleepstory = ', hyvät syvät!'

# Aktiivisuutta

    # Aktiivisuus, viimeiset 2h (a)
    a_kappyra = a['activity'][-1]['class_5min']
    a_2h = a_kappyra[-24:]

    # Kävellyt kilometrit eilen
    activedata = a['activity'][-2]['daily_movement']

    # Kävellyt kilometrit tänään
    activedata_2 = a['activity'][-1]['daily_movement']

    # Kävellyt kilometrit tänään miinus eilen.  Onko käyrä ylös vai alas?
    plusmiinus = activedata_2 - activedata
    if plusmiinus > 0:
        okei = 'parempi'
    else:
        okei = 'huonompi'

    # Otetut askeleet, total (5 vrk)
    stepsit = a['activity'][-7:]

    # Askelet tänään
    steps = a['activity'][-1]['steps']

    # Raskas urheilu eilen
    voima = a['activity'][-1]['high']

# Liikuntaraportti

    viikkoday = []
    weekstrength = []
    for i in range(0, 7):
        viikkovoima = a['activity'][i]['high']
        viikkovoimapvm = a['activity'][i]['day_start']
        y = int(viikkovoimapvm[0:4])
        m = int(viikkovoimapvm[6:7])
        d = int(viikkovoimapvm[8:10])
        viikkoday.append(datetime.datetime(y, m, d).weekday())
        weekstrength.append(viikkovoima)

    pvm = viikkoday
    pvmh = weekstrength
    pvm_pvmh = dict(zip(pvm, pvmh))

    # Nämä on Django Adminissa määritetyt omat harjoittelupäivät/viikko.
    # Huomaa, tässä lasketaan hikisuoritukseksi vasta kun on vähintään kolme minuuttia kovaa pulssia (pvm_pvmh[i] > 2)
    #TODO päivittäiseen hikisuotitukseen riittävä harjoittelumäärä käyttäjän omaksi valinnaksi/asetukseksi

    # Suunniteltujen urheilupäivien loogiset nimet
    urkkadaynimet = Sportdays.objects.filter(ourauser__firstname__iexact=you).order_by('days')
    sdays = urkkadaynimet.filter().values_list('days', flat=True)
    kova_tintensity = Ourauser.objects.get(username=kayttaja).tintensity
    sporttiminuutit = 0

    for i in pvm_pvmh:
        sporttiminuutit += pvm_pvmh[i]
        if pvm_pvmh[i] > kova_tintensity:
            with open('lauantairaportti.txt', 'a') as f:
                f.write('Päivä ' + str(i) + ' Urheilit kovalla pulssilla ' + str(pvm_pvmh[i]) + ' minuuttia.')
            if str(i) in sdays:
                with open('lauantairaportti.txt', 'a') as f:
                    f.write(' Bene, kuten oli suunnitelmakin.')
            else:
                with open('lauantairaportti.txt', 'a') as f:
                    f.write(' Hyvä homma, mutta muista myös levätä välillä.')
        else:
            if str(i) in sdays:
                with open('lauantairaportti.txt', 'a') as f:
                    f.write('Päivä ' + str(i) + ' Jaahas et sitten ehtinyt urheilla, vaikka olisi pitänyt.')
            else:
                with open('lauantairaportti.txt', 'a') as f:
                    f.write('Päivä ' + str(i) + ' Välipäivä. Suunnitelman mukaan mennään.')
        with open('lauantairaportti.txt', 'a') as f:
            f.write('\n')
    with open('lauantairaportti.txt', 'a') as f:
        f.write('Viikonsaldo: ' + str(sporttiminuutit) + ' minuuttia hikijumppaa.')

    fin = open("lauantairaportti.txt", "rt")
    # read file contents to string
    data = fin.read()
    # replace all occurrences of the required string
    data = data.replace('Päivä 0', 'Ma')
    data = data.replace('Päivä 1', 'Ti')
    data = data.replace('Päivä 2', 'Ke')
    data = data.replace('Päivä 3', 'To')
    data = data.replace('Päivä 4', 'Pe')
    data = data.replace('Päivä 5', 'La')
    data = data.replace('Päivä 6', 'Su')
    # close the input file
    fin.close()
    # open the input file in write mode
    fin = open("lauantairaportti.txt", "wt")
    # overrite the input file with the resulting data
    fin.write(data)
    # close the file
    fin.close()

    with open('lauantairaportti.txt', 'r') as f:
        raportti = f.readlines()

    os.remove('lauantairaportti.txt')

# Valmiustila (r)

    readydata = r['readiness'][-1]['score']
    readydatahistory = r['readiness'][-7:]

    # score_previous_day vaihdettu '-2' koska en tiedä, mitä se tekee
    # r_yesterday = r['readiness'][-1]['score_previous_day']
    r_yesterday = r['readiness'][-2]['score']
    valmiusero = readydata - r_yesterday

# Ihanteellinen nukkumaanmenoaika (b)

    nukkumaanko = b['ideal_bedtimes'][0]['status']
    unille = b['ideal_bedtimes'][0]['bedtime_window']['end']
    pillowtime = ''

    if unille is not None:
        seconds_input = unille
        conversion = datetime.timedelta(seconds=seconds_input)
        ta = str(conversion)
        pillowtime = ta[-8:-3]

    context = {
        'you': you,
        'urkkadaynimet': urkkadaynimet,
        'bmi': bmi,
        'deepsleepamount': deepsleepamount,
        'deepsleeppercentage': deepsleeppercentage,
        'sleepstory': sleepstory,
        'a_2h': a_2h,
        'readydatahistory': readydatahistory,
        'plusmiinus': plusmiinus,
        'okei': okei,
        'stepsit': stepsit,
        'steps': steps,
        'voima': voima,
        'readydata': readydata,
        'nukkumaanko': nukkumaanko,
        'unille': unille,
        'pillowtime': pillowtime,
        'valmiusero': valmiusero,
        'raportti': raportti,
    }
    return render(request, 'myOura/ouraring.html', {'context': context})
