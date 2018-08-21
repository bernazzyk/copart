from __future__ import absolute_import

import re
import json
import random
import subprocess
from multiprocessing.pool import ThreadPool

from lxml.html import document_fromstring, fromstring
from datetime import datetime, timedelta
from django.utils import timezone

import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from copart.celery import app
from product.models import *

GLOBAL = {'live_auctions': []}


@app.task
def say_hello():
    print('say_hello() called at ' + str(datetime.now()))


@app.task
def say_ok():
    print('say_ok() called at ' + str(datetime.now()))


@app.task
def scrap_copart_lots_all(start, end):
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    while True:
        try:
            driver = webdriver.Chrome(chrome_options=options)
            break
        except:
            time.sleep(1)

    driver.get('https://www.copart.com/')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@data-uname="homePageSignIn"]'))).click()
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@data-uname="homePageMemberSignIn"]'))).click()
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@data-uname="loginUsernametextbox"]'))).send_keys('vdm.cojocaru@gmail.com')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@data-uname="loginPasswordtextbox"]'))).send_keys('c0p2rt')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//button[@data-uname="loginSigninmemberbutton"]'))).click()

    page_count = 1000
    misc = '#MakeCode:{code} OR #MakeDesc:{description}, #VehicleTypeCode:VEHTYPE_{type},#LotYear:[1920 TO 2019]'.format
    payloads = 'draw={draw}&columns[0][data]=0&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=false&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=1&columns[1][name]=&columns[1][searchable]=true&columns[1][orderable]=false&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=2&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3][data]=3&columns[3][name]=&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&columns[4][data]=4&columns[4][name]=&columns[4][searchable]=true&columns[4][orderable]=true&columns[4][search][value]=&columns[4][search][regex]=false&columns[5][data]=5&columns[5][name]=&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][value]=&columns[5][search][regex]=false&columns[6][data]=6&columns[6][name]=&columns[6][searchable]=true&columns[6][orderable]=true&columns[6][search][value]=&columns[6][search][regex]=false&columns[7][data]=7&columns[7][name]=&columns[7][searchable]=true&columns[7][orderable]=true&columns[7][search][value]=&columns[7][search][regex]=false&columns[8][data]=8&columns[8][name]=&columns[8][searchable]=true&columns[8][orderable]=true&columns[8][search][value]=&columns[8][search][regex]=false&columns[9][data]=9&columns[9][name]=&columns[9][searchable]=true&columns[9][orderable]=true&columns[9][search][value]=&columns[9][search][regex]=false&columns[10][data]=10&columns[10][name]=&columns[10][searchable]=true&columns[10][orderable]=true&columns[10][search][value]=&columns[10][search][regex]=false&columns[11][data]=11&columns[11][name]=&columns[11][searchable]=true&columns[11][orderable]=true&columns[11][search][value]=&columns[11][search][regex]=false&columns[12][data]=12&columns[12][name]=&columns[12][searchable]=true&columns[12][orderable]=true&columns[12][search][value]=&columns[12][search][regex]=false&columns[13][data]=13&columns[13][name]=&columns[13][searchable]=true&columns[13][orderable]=true&columns[13][search][value]=&columns[13][search][regex]=false&columns[14][data]=14&columns[14][name]=&columns[14][searchable]=true&columns[14][orderable]=false&columns[14][search][value]=&columns[14][search][regex]=false&columns[15][data]=15&columns[15][name]=&columns[15][searchable]=true&columns[15][orderable]=false&columns[15][search][value]=&columns[15][search][regex]=false&order[0][column]=1&order[0][dir]=asc&start={start}&length={length}&search[value]=&search[regex]=false&sort=auction_date_type desc,auction_date_utc asc&defaultSort=true&filter[MISC]={misc}&query=*&watchListOnly=false&freeFormSearch=false&page={page}&size={size}'.format

    url = "https://www.copart.com/public/vehicleFinder/search"
    detail_url = 'https://www.copart.com/public/data/lotdetails/solr/lotImages/{}'.format
    headers = {
        "Host": "www.copart.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    }

    for makes in VehicleMakes.objects.all()[start:end]:
        vtype = makes.type
        description = makes.description
        code = makes.code

        payload = payloads(draw=1, start=0, length=page_count, misc=misc(code=code, description=description, type=vtype),
                           page=0, size=page_count)
        while True:
            try:
                response = requests.request("POST", url, data=payload, headers=headers)
                break
            except:
                print(url)
                time.sleep(1)

        result = json.loads(response.text)['data']['results']
        total = result['totalElements']

        finder_item = VehicleMakes.objects.get(type=vtype, description=description, code=code)
        finder_item.count = total
        finder_item.save()

        pages_num = (total + 999) // 1000
        print(description, 'total - ' + str(total))
        print(description, 'total pages - ' + str(pages_num))

        if total == 0:
            continue

        page = 1

        driver.get(detail_url(result['content'][0]['ln']))

        while page <= pages_num:
            for _lot in result['content']:
                if Vehicle.objects.filter(lot=_lot['ln']).exists():
                    print('exists - ' + str(_lot['ln']))
                    continue

                driver.get(detail_url(_lot['ln']))
                lot = json.loads(document_fromstring(driver.page_source).text_content())['data']
                images = lot.get('imagesList', {'FULL_IMAGE': [], 'THUMBNAIL_IMAGE': [], 'HIGH_RESOLUTION_IMAGE': []})
                try:
                    lot = lot['lotDetails']
                except:
                    print(_lot['ln'], lot, detail_url(_lot['ln']))
                    continue
                print(description + ' - ' + str(lot['ln']))

                vin = lot.get('fv', '')
                if not vin or len(vin) > 17:
                    continue

                db_item, created = Vehicle.objects.get_or_create(lot=lot['ln'])

                db_item.make = lot['mkn']
                db_item.model = lot['lm']
                db_item.year = lot['lcy']
                db_item.vin = vin
                db_item.retail_value = lot['la']
                # rc
                # obc
                db_item.odometer_orr = lot['orr']   # 0 mi (NOT ACTUAL), 0 km (EXEMPT), 76,848 mi (ACTUAL)
                db_item.odometer_ord = lot['ord']   # NOT ACTUAL
                db_item.engine_type = lot.get('egn', '')
                db_item.cylinders = lot.get('cy', '')
                db_item.name = lot['ld']
                db_item.location = lot['yn']
                db_item.currency = lot['cuc']
                # tz
                if 'ad' in lot:
                    db_item.sale_date = timezone.make_aware(datetime.fromtimestamp(lot['ad'] / 1000), timezone.get_current_timezone()) + timedelta(hours=14)
                # at
                db_item.item = str(lot['aan'])
                # ahb
                # ss
                # bndc  BUY IT NOW
                # bnp   buyTodayBid 3000
                # sbf
                db_item.doc_type_ts = lot['ts']
                db_item.doc_type_stt = lot['stt']
                db_item.doc_type_td = lot['td']    # TN - SALVAGE CERTIFICATE, QC - GRAVEMENT ACCIDENTE
                # tgc
                db_item.lot_1st_damage = lot['dd']
                db_item.avatar = lot.get('tims', None)
                # lic[2]
                db_item.grid = lot['gr']
                # dtc
                db_item.lane = lot.get('al', '')
                # adt
                # ynumb
                # phynumb
                # bf
                # ymin
                # offFlg    condition
                # htsmn
                db_item.transmission = lot.get('tmtp', '')
                # myb
                # lmc - same with makecode
                # lcc
                db_item.lot_2nd_damage = lot.get('sdd', '')
                db_item.body_style = lot.get('bstl', '')
                db_item.lot_highlights = lot.get('lcd', '')
                db_item.fuel = lot.get('ft', '')
                db_item.keys = lot.get('hk', '')
                db_item.drive = lot.get('drv', '')
                # showSeller
                # sstpflg
                # syn same with yn
                # ifs
                # pbf
                # crg
                # brand
                db_item.notes = lot.get('ltnte', '').strip()
                db_item.color = lot.get('clr')
                db_item.lot_seller = lot.get('scn', '')

                db_item.current_bid = lot['dynamicLotDetails']['currentBid']
                db_item.bid_status = lot['dynamicLotDetails']['bidStatus']
                db_item.sale_status = lot['dynamicLotDetails']['saleStatus']

                db_item.images = '|'.join([a['url'][44:] for a in images.get('FULL_IMAGE', [])])
                db_item.thumb_images = '|'.join([a['url'][44:] for a in images.get('THUMBNAIL_IMAGE', [])])
                # db_item.high_images = '|'.join([a['url'][44:] for a in images.get('HIGH_RESOLUTION_IMAGE', [])])

                db_item.save()

            if page == pages_num:
                break

            page += 1
            payload = payloads(draw=page, start=page_count * (page - 1), length=page_count,
                               misc=misc(code=code, description=description, type=vtype), page=page - 1, size=page_count)
            while True:
                try:
                    response = requests.request("POST", url, data=payload, headers=headers)
                    break
                except:
                    print(url)
                    time.sleep(1)
            print('page - ' + str(page))

            result = json.loads(response.text)['data']['results']
            total = result['totalElements']
            pages_num = (total + 999) // 1000

        finder_item = VehicleMakes.objects.get(type=vtype, description=description, code=code)
        finder_item.count = total
        finder_item.save()

        print('total - ' + str(total))
        print('total pages - ' + str(pages_num))

    current_vin = ''
    lots = Vehicle.objects.filter(source=True).order_by('vin', 'lot')
    for lot_id, lot in enumerate(lots):
        if lot.vin == current_vin:
            lots[lot_id - 1].show = False
            lots[lot_id - 1].save()
            lot.foregoing = lots[lot_id - 1]
            lot.save()
            print(', '.join([current_vin, str(lots[lot_id - 1].lot), str(lot.lot)]))
        current_vin = lot.vin

    driver.close()
    driver.quit()


@app.task
def scrap_copart_lots(vtype, description, code):
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    while True:
        try:
            driver = webdriver.Chrome(chrome_options=options)
            break
        except:
            time.sleep(1)

    driver.get('https://www.copart.com/')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@data-uname="homePageSignIn"]'))).click()
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@data-uname="homePageMemberSignIn"]'))).click()
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@data-uname="loginUsernametextbox"]'))).send_keys('vdm.cojocaru@gmail.com')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@data-uname="loginPasswordtextbox"]'))).send_keys('c0p2rt')
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//button[@data-uname="loginSigninmemberbutton"]'))).click()

    page_count = 1000
    misc = '#MakeCode:{code} OR #MakeDesc:{description}, #VehicleTypeCode:VEHTYPE_{type},#LotYear:[1920 TO 2019]'.format
    payloads = 'draw={draw}&columns[0][data]=0&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=false&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=1&columns[1][name]=&columns[1][searchable]=true&columns[1][orderable]=false&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=2&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3][data]=3&columns[3][name]=&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&columns[4][data]=4&columns[4][name]=&columns[4][searchable]=true&columns[4][orderable]=true&columns[4][search][value]=&columns[4][search][regex]=false&columns[5][data]=5&columns[5][name]=&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][value]=&columns[5][search][regex]=false&columns[6][data]=6&columns[6][name]=&columns[6][searchable]=true&columns[6][orderable]=true&columns[6][search][value]=&columns[6][search][regex]=false&columns[7][data]=7&columns[7][name]=&columns[7][searchable]=true&columns[7][orderable]=true&columns[7][search][value]=&columns[7][search][regex]=false&columns[8][data]=8&columns[8][name]=&columns[8][searchable]=true&columns[8][orderable]=true&columns[8][search][value]=&columns[8][search][regex]=false&columns[9][data]=9&columns[9][name]=&columns[9][searchable]=true&columns[9][orderable]=true&columns[9][search][value]=&columns[9][search][regex]=false&columns[10][data]=10&columns[10][name]=&columns[10][searchable]=true&columns[10][orderable]=true&columns[10][search][value]=&columns[10][search][regex]=false&columns[11][data]=11&columns[11][name]=&columns[11][searchable]=true&columns[11][orderable]=true&columns[11][search][value]=&columns[11][search][regex]=false&columns[12][data]=12&columns[12][name]=&columns[12][searchable]=true&columns[12][orderable]=true&columns[12][search][value]=&columns[12][search][regex]=false&columns[13][data]=13&columns[13][name]=&columns[13][searchable]=true&columns[13][orderable]=true&columns[13][search][value]=&columns[13][search][regex]=false&columns[14][data]=14&columns[14][name]=&columns[14][searchable]=true&columns[14][orderable]=false&columns[14][search][value]=&columns[14][search][regex]=false&columns[15][data]=15&columns[15][name]=&columns[15][searchable]=true&columns[15][orderable]=false&columns[15][search][value]=&columns[15][search][regex]=false&order[0][column]=1&order[0][dir]=asc&start={start}&length={length}&search[value]=&search[regex]=false&sort=auction_date_type desc,auction_date_utc asc&defaultSort=true&filter[MISC]={misc}&query=*&watchListOnly=false&freeFormSearch=false&page={page}&size={size}'.format

    url = "https://www.copart.com/public/vehicleFinder/search"
    detail_url = 'https://www.copart.com/public/data/lotdetails/solr/lotImages/{}'.format
    headers = {
        "Host": "www.copart.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    }

    # response = requests.request("POST", url, headers=headers)
    # cookies = response.cookies.get_dict()
    # cookie_str = '{incap_key}={incap_value}'.format
    # incap_key = ''
    # incap_value = ''
    # for key, value in cookies.items():
    #     if str(key).startswith('incap'):
    #         incap_key = key
    #         incap_value = value
    #         break
    # headers['cookie'] = cookie_str(incap_key=incap_key, incap_value=incap_value)

    payload = payloads(draw=1, start=0, length=page_count, misc=misc(code=code, description=description, type=vtype),
                       page=0, size=page_count)
    while True:
        try:
            response = requests.request("POST", url, data=payload, headers=headers)
            break
        except:
            print(url)
            time.sleep(1)

    result = json.loads(response.text)['data']['results']
    total = result['totalElements']

    finder_item = VehicleMakes.objects.get(type=vtype, description=description, code=code)
    finder_item.count = total
    finder_item.save()

    pages_num = (total + 999) // 1000
    print('total - ' + str(total))
    print('total pages - ' + str(pages_num))

    if total == 0:
        return

    page = 1

    driver.get(detail_url(result['content'][0]['ln']))

    while page <= pages_num:
        for _lot in result['content']:
            if Vehicle.objects.filter(lot=_lot['ln']).exists():
                print('exists - ' + str(_lot['ln']))
                continue

            driver.get(detail_url(_lot['ln']))
            lot = json.loads(document_fromstring(driver.page_source).text_content())['data']
            images = lot.get('imagesList', {'FULL_IMAGE': [], 'THUMBNAIL_IMAGE': [], 'HIGH_RESOLUTION_IMAGE': []})
            try:
                lot = lot['lotDetails']
            except:
                print(_lot['ln'], lot, detail_url(_lot['ln']))
                continue
            print(description + ' - ' + str(lot['ln']))

            vin = lot.get('fv', '')
            if not vin or len(vin) > 17:
                continue

            db_item, created = Vehicle.objects.get_or_create(lot=lot['ln'])

            db_item.make = lot['mkn']
            db_item.model = lot['lm']
            db_item.year = lot['lcy']
            db_item.vin = vin
            db_item.retail_value = lot['la']
            # rc
            # obc
            db_item.odometer_orr = lot['orr']   # 0 mi (NOT ACTUAL), 0 km (EXEMPT), 76,848 mi (ACTUAL)
            db_item.odometer_ord = lot['ord']   # NOT ACTUAL
            db_item.engine_type = lot.get('egn', '')
            db_item.cylinders = lot.get('cy', '')
            db_item.name = lot['ld']
            db_item.location = lot['yn']
            db_item.currency = lot['cuc']
            # tz
            if 'ad' in lot:
                db_item.sale_date = timezone.make_aware(datetime.fromtimestamp(lot['ad'] / 1000), timezone.get_current_timezone()) + timedelta(hours=14)
            # at
            db_item.item = str(lot['aan'])
            # ahb
            # ss
            # bndc  BUY IT NOW
            # bnp   buyTodayBid 3000
            # sbf
            db_item.doc_type_ts = lot['ts']
            db_item.doc_type_stt = lot['stt']
            db_item.doc_type_td = lot['td']    # TN - SALVAGE CERTIFICATE, QC - GRAVEMENT ACCIDENTE
            # tgc
            db_item.lot_1st_damage = lot['dd']
            db_item.avatar = lot.get('tims', None)
            # lic[2]
            db_item.grid = lot['gr']
            # dtc
            db_item.lane = lot.get('al', '')
            # adt
            # ynumb
            # phynumb
            # bf
            # ymin
            # offFlg    condition
            # htsmn
            db_item.transmission = lot.get('tmtp', '')
            # myb
            # lmc - same with makecode
            # lcc
            db_item.lot_2nd_damage = lot.get('sdd', '')
            db_item.body_style = lot.get('bstl', '')
            db_item.lot_highlights = lot.get('lcd', '')
            db_item.fuel = lot.get('ft', '')
            db_item.keys = lot.get('hk', '')
            db_item.drive = lot.get('drv', '')
            # showSeller
            # sstpflg
            # syn same with yn
            # ifs
            # pbf
            # crg
            # brand
            db_item.notes = lot.get('ltnte', '').strip()
            db_item.color = lot.get('clr')
            db_item.lot_seller = lot.get('scn', '')

            db_item.current_bid = lot['dynamicLotDetails']['currentBid']
            db_item.bid_status = lot['dynamicLotDetails']['bidStatus']
            db_item.sale_status = lot['dynamicLotDetails']['saleStatus']

            db_item.images = '|'.join([a['url'][44:] for a in images.get('FULL_IMAGE', [])])
            db_item.thumb_images = '|'.join([a['url'][44:] for a in images.get('THUMBNAIL_IMAGE', [])])
            # db_item.high_images = '|'.join([a['url'][44:] for a in images.get('HIGH_RESOLUTION_IMAGE', [])])

            db_item.save()

        if page == pages_num:
            break

        page += 1
        payload = payloads(draw=page, start=page_count * (page - 1), length=page_count,
                           misc=misc(code=code, description=description, type=vtype), page=page - 1, size=page_count)
        while True:
            try:
                response = requests.request("POST", url, data=payload, headers=headers)
                break
            except:
                print(url)
                time.sleep(1)
        print('page - ' + str(page))

        result = json.loads(response.text)['data']['results']
        total = result['totalElements']
        pages_num = (total + 999) // 1000

    finder_item = VehicleMakes.objects.get(type=vtype, description=description, code=code)
    finder_item.count = total
    finder_item.save()

    print('total - ' + str(total))
    print('total pages - ' + str(pages_num))

    current_vin = ''
    lots = Vehicle.objects.filter(source=True).order_by('vin', 'lot')
    for lot_id, lot in enumerate(lots):
        if lot.vin == current_vin:
            lots[lot_id - 1].show = False
            lots[lot_id - 1].save()
            lot.foregoing = lots[lot_id - 1]
            lot.save()
            print(', '.join([current_vin, str(lots[lot_id - 1].lot), str(lot.lot)]))
        current_vin = lot.vin

    driver.close()
    driver.quit()


@app.task
def scrap_iaai_lots():
    first_url = 'Search?url=pd6JWbJ9kRzcBdFK3vKeyjpx+85A4wDWncLLWXG+ICNJ+99sqMaoisYKWs6Cr9ehv9+/+aONWE6H6WT3ZwrT5WJbMzhonrNwbBqJ1gz8MLhEGYLSkxHCvDCjFfWbo0PvmwHJtE0eSnJvuIuIOW9/5g==&crefiners=&keyword='
    item_url = 'https://www.iaai.com/Vehicle?itemID={item_id}'.format

    def get_detail(item_and_stock_number):
        item_id = item_and_stock_number[0]
        stock_id = item_and_stock_number[1]
        try:
            if Vehicle.objects.filter(lot=int(stock_id)).exists():
                print('exists - ' + item_id + ', ' + stock_id)
                return

            while True:
                try:
                    response = requests.get(item_url(item_id=item_id))
                    break
                except:
                    print('reconnect to ' + item_url(item_id=item_id))
                    time.sleep(1)
            if response.text.__contains__('<h1>Vehicle details are not found for this stock.</h1>'):
                print(item_url(item_id=item_id) + ' - Vehicle details are not found for this stock.')
                return
            t = fromstring(response.text)
            data = t.xpath('//script[@id="layoutVM"]/text()')[0].strip()
            lot = json.loads(data)['VehicleDetailsViewModel']

            print(', '.join(['ItemID: ' + lot['ItemID'], 'StockNo: ' + lot['StockNo']]))

            try:
                vin = bytearray.fromhex(lot['VIN']).decode()
                if not vin or len(vin) != 17:
                    raise Exception
            except:     # Unknown, BILL OF SALE, N/A, NONE
                print(item_url(item_id=item_id) + ' - vin not correct ' + lot['VIN'])
                return

            # db_item, created = Vehicle.objects.get_or_create(lot=item_id)
            db_item = Vehicle(lot=int(stock_id))
            db_item.vin = vin

            # General Information
            db_item.name = t.xpath('//h1[@class="pd-title-ymm"]/text()')[0]
            db_item.make = lot['Make']
            db_item.model = lot['Model']
            db_item.year = int(lot['Year'])
            db_item.currency = 'USD'

            def get_item(items, key, index=0):
                value = [a for a in items if a['Name'].strip() == key]
                if value and len(value[0]['DisplayValues']) > index:
                    return value[0]['DisplayValues'][index]['Text']
                return ''

            # Lot Information
            db_item.doc_type_td = lot['SaleDoc']
            odometer_orr = get_item(lot['ConditionInfo'], 'Odometer')
            odometer_orr = re.sub('[^0-9]', '', odometer_orr)
            db_item.odometer_orr = int(odometer_orr) if odometer_orr else 0
            db_item.odometer_ord = get_item(lot['ConditionInfo'], 'Odometer', 1)
            db_item.lot_highlights = get_item(lot['ConditionInfo'], 'runAndDrive')
            db_item.lot_seller = lot['SaleInfo']['Seller']
            db_item.lot_1st_damage = get_item(lot['ConditionInfo'], 'PrimaryDamage')
            db_item.lot_2nd_damage = get_item(lot['ConditionInfo'], 'SecondaryDamage')
            db_item.retail_value = int(re.sub('[^0-9]', '', lot['SaleInfo']['ACV'])) if lot['SaleInfo']['ACV'] else 0

            # Features
            db_item.body_style = get_item(lot['VINInfo'], 'BodyStyle')
            db_item.color = get_item(lot['VINInfo'], 'Color')
            db_item.engine_type = get_item(lot['VINInfo'], 'Engine')
            db_item.cylinders = get_item(lot['VINInfo'], 'Cylinders')
            db_item.transmission = get_item(lot['VINInfo'], 'Transmission')
            db_item.drive = get_item(lot['VINInfo'], 'DriveLineType')
            db_item.fuel = get_item(lot['VINInfo'], 'FuelType')
            db_item.keys = get_item(lot['ConditionInfo'], 'Keys')
            db_item.notes = get_item(lot['ConditionInfo'], 'MissingComponents')

            # Bid Information
            # db_item.bid_status = models.CharField(_('Bid Status'), max_length=30, default='')
            # db_item.sale_status = lot['AuctionStatusDescription']
            db_item.current_bid = int(re.sub('[^0-9]', '', lot['HighBidAmount'])) if lot['HighBidAmount'] else 0
            # db_item.buy_today_bid = models.IntegerField(_('Buy Today Bid'), default=0)
            # db_item.sold_price = models.IntegerField(_('Sold Price'), default=0)

            # Sale Information
            db_item.location = lot['SaleInfo']['TitleState'] if lot['SaleInfo']['TitleState'] else ''
            db_item.lane = lot['AuctionLane'] if lot['AuctionLane'] else '-'
            db_item.item = lot['Slot']
            # db_item.grid = models.CharField(_('Grid/Row'), max_length=5, default='')
            db_item.sale_date = timezone.make_aware(datetime.strptime(lot['LiveDate'], '%m/%d/%Y %I:%M:%S %p'), timezone.get_current_timezone())
            db_item.last_updated = timezone.make_aware(datetime.strptime(str(datetime.now().year) + '-' + lot['SaleInfo']['ModifiedDate'], '%Y-%b-%d %I:%M%p (CDT)'), timezone.get_current_timezone())

            db_item.source = False

            image_url = 'https://www.iaai.com/Images/GetJsonImageDimensions?json={"stockNumber":"%s","branchCode":"%s","salvageId":"%s"}' % (
                lot['SaleInfo']['StockNumber'], lot['BranchCode'], lot['SalvageID']
            )
            while True:
                try:
                    response = requests.get(image_url)
                    break
                except:
                    print('reconnect to ' + image_url)
                    time.sleep(1)
            if response.text != '':
                images = json.loads(response.text)
                db_item.images = '|'.join([a['K'] for a in images['keys']])
                db_item.avatar = 'https://vis.iaai.com:443/resizer?imageKeys=%s&width=128&height=96' % images['keys'][0]['K']

            db_item.save()
        except Exception as e:
            error_file = open('error.txt', 'a')
            error_file.write(item_url(item_id=item_id) + ' ' + str(e))
            error_file.close()
            print(item_url(item_id=item_id), e)

    def get_lot_urls(pg):
        payload = {
            'URL': first_url,
            'Key': 'pg',
            'Value': pg
        }
        while True:
            try:
                response = requests.post('https://www.iaai.com/Search/ChangeKey', data=payload)
                print('search key - ' + str(pg))
                break
            except:
                print('search key again - ' + str(pg))
                time.sleep(1)

        while True:
            try:
                response = requests.get('https://www.iaai.com/' + response.text)
                t = fromstring(response.text)
                print('page - ' + str(pg))
                break
            except:
                print('page again - ' + str(pg))
                time.sleep(1)

        urls = t.xpath('//div[@id="dvSearchList"]/div/div/table/tbody/tr/td[3]/a/@href')
        stock_nums = t.xpath('//div[@id="dvSearchList"]/div/div/table/tbody/tr/td[3]/p/text/text()')
        return [url.split('?')[1].split('&')[0].split('=')[1] for url in urls], stock_nums

    start = datetime.now()

    print('page - 1')
    response = requests.get('https://www.iaai.com/' + first_url)
    t = fromstring(response.text)
    results = t.xpath('//div[@id="dvSearchList"]/div/div/table/tbody/tr/td[3]/a/@href')
    stock_numbers = t.xpath('//div[@id="dvSearchList"]/div/div/table/tbody/tr/td[3]/p/text/text()')
    lots = [url.split('?')[1].split('&')[0].split('=')[1] for url in results]

    total = int(t.xpath('//span[@id="dvTotalText"]/text()')[0].strip().replace(',', ''))
    pages = (total + 99) // 100

    pool = ThreadPool(32)
    for chunk in pool.imap_unordered(get_lot_urls, range(2, pages + 1)):
        a, b = chunk
        lots += a
        stock_numbers += b

    end = datetime.now()
    print(len(lots), len(stock_numbers), (end - start).total_seconds())

    lots = [[item, stock_numbers[item_id]] for item_id, item in enumerate(lots)]

    pool = ThreadPool(32)
    for _ in pool.imap_unordered(get_detail, lots):
        pass

    current_vin = ''
    lots = Vehicle.objects.filter(source=False).order_by('vin', 'lot')
    for lot_id, lot in enumerate(lots):
        if lot.vin == current_vin:
            lots[lot_id - 1].show = False
            lots[lot_id - 1].save()
            lot.foregoing = lots[lot_id - 1]
            lot.save()
            print(', '.join([current_vin, str(lots[lot_id - 1].lot), str(lot.lot)]))
        current_vin = lot.vin


@app.task
def scrap_live_auctions():
    try:
        options = webdriver.ChromeOptions()

        options.add_argument('--disable-extensions')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        while True:
            try:
                driver = webdriver.Chrome(chrome_options=options)
                break
            except:
                time.sleep(1)
        driver.implicitly_wait(300)
        driver.set_page_load_timeout(300)

        driver.get('https://www.copart.com/todaysAuction/')

        auction_live_now = driver.find_element_by_xpath('//table[@id="auctionLiveNow-datatable"]')
        auction_later_today = driver.find_element_by_xpath('//table[@id="auctionLaterToday-datatable"]')
        no_auction = 'There are no auctions available at this time.'
        if auction_live_now.text.__contains__(no_auction) and auction_later_today.text.__contains__(no_auction):
            print(no_auction)
            return

        auction_urls = auction_live_now.find_elements_by_xpath('./tbody/tr/td/ul/li[1]/a')
        auction_urls = [a.get_attribute('href') for a in auction_urls]

        driver.close()
        driver.quit()

        params = []
        for url in auction_urls:
            param = url.split('=')[-1]
            num = '%03d' % int(param.split('-')[0])
            params.append(num + param.split('-')[1])

        for param in params:
            if param in GLOBAL['live_auctions']:
                continue
            command = "python auction.py " + param + '-' + str(random.randint(204, 206)) + " &"
            subprocess.call(command, shell=True)
            print('new auction -', param)
        GLOBAL['live_auctions'] = params
        print(len(params))
    except Exception as e:
        print(e)
