from django.utils.dateparse import parse_date, parse_datetime
from django.conf import settings
from django.utils.timezone import make_aware

from .forms import *


def filter(com_id, prio_deg, date_d, date_f):

    date_d = parse_date(date_d)
    date_f +="T23:59:59"
    date_f = parse_datetime(date_f)

    if com_id == 0:
        posts = Post.objects.all().filter(evenementiel=True, priorite__degre__gte=prio_deg,
                                          date_evenement__gte=date_d, date_evenement__lte=date_f)
    else:
        posts = Post.objects.all().filter(evenementiel=True, communaute=com_id, priorite__degre__gte=prio_deg,
                                          date_evenement__gte=date_d, date_evenement__lte=date_f)

    return posts


def conv_date(j_d, m_d, y_d):
    date = str(y_d) + "-"

    if m_d < 10:
        date += "0" + str(m_d)
    else:
        date += str(m_d)

    date += "-"

    if j_d < 10:
        date += "0" + str(j_d)
    else:
        date += str(j_d)

    return date
