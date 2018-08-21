from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import translation

from product.tasks import scrap_copart_lots, scrap_copart_lots_all, scrap_iaai_lots, scrap_live_auctions, say_hello
from product.models import Vehicle


def switch_language(request, language):
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect('/')


def scrap_copart(request):
    vtype = request.GET.get('type')
    description = request.GET.get('description')
    code = request.GET.get('code')

    scrap_copart_lots.delay(vtype, description, code)

    return redirect('/product/vehiclemakes/')


def scrap_copart_all(request):
    scrap_copart_lots_all.delay(0, 360)
    scrap_copart_lots_all.delay(360, 720)
    scrap_copart_lots_all.delay(720, 1080)
    scrap_copart_lots_all.delay(1080, 1441)

    return redirect('/')


def scrap_iaai(request):
    scrap_iaai_lots.delay()

    return redirect('/')


def scrap_auction(request):
    scrap_live_auctions.delay()

    return redirect('/')


def task_test(request):
    say_hello.delay()

    return redirect('/')


def ajax_getimages(request):
    lot_id = request.POST.get('lot', '')

    if not lot_id:
        return JsonResponse({'result': False})

    lot = Vehicle.objects.get(lot=int(lot_id))
    if lot.source:
        images = ['https://cs.copart.com/v1/AUTH_svc.pdoc00001/' + a for a in lot.images.split('|')]
        thumb_images = ['https://cs.copart.com/v1/AUTH_svc.pdoc00001/' + a for a in lot.thumb_images.split('|')]
    else:
        images = ['https://vis.iaai.com:443/resizer?imageKeys=%s&width=640&height=480' % a for a in lot.images.split('|')]
        thumb_images = ['https://vis.iaai.com:443/resizer?imageKeys=%s&width=128&height=96' % a for a in lot.images.split('|')]

    return JsonResponse({
        'result': True,
        'lot_name': lot.name,
        'lot': lot.lot,
        'images': images,
        'thumb_images': thumb_images,
    })
