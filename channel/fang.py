# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import model
import misc
import time
import datetime
import urllib2
import re
import json
from util.log import Log
import base64
from util import urlUtil
import traceback

logging = Log()

channel = u'fang'

def GetHouseByCommunitylist(city, communitylist):

    logging.info("Get House Infomation").start()

    for community in communitylist:
        try:
            get_house_percommunity(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community + "Fail")
            pass

    logging.end()

def GetSellByCommunitylist(city, communitylist):
    logging.info("Get Sell Infomation").start()
    for community in communitylist:
        try:
            get_sell_percommunity(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community + "Fail")
            pass
    logging.end()

def GetRentByCommunitylist(city, communitylist):

    logging.info("Get Rent Infomation").start()

    for community in communitylist:
        try:
            get_rent_percommunity(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community + " Fail")
            pass
        
    logging.end()


def GetCommunityByRegionlist(city, regionlist=[u'xicheng']):
    logging.info("Get Community Infomation").start()
    for regionname in regionlist:
        try:
            get_community_perregion(city, regionname)
            logging.info(regionname + " Done")
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            logging.error(regionname + " Fail")
            pass
    logging.end()


def GetHouseByRegionlist(city, regionlist=[u'xicheng']):
    logging.start()
    for regionname in regionlist:
        logging.info("Get Onsale House Infomation in %s" % regionname)
        try:
            get_house_perregion(city, regionname)
        except Exception as e:
            logging.error(e)
            pass
    logging.end()


def GetRentByRegionlist(city, regionlist=[u'xicheng']):
    logging.start()
    for regionname in regionlist:
        logging.info("Get Rent House Infomation in %s" % regionname)
        try:
            get_rent_perregion(city, regionname)
        except Exception as e:
            logging.error(e)
            pass
    logging.end()


def get_house_percommunity(city, communityname):
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"ershoufang/rs" + \
        urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Houseinfo.select().where(model.Houseinfo.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + \
                u"ershoufang/pg%drs%s/" % (page,
                                           urllib2.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class": "clear"})
        i = 0
        logging.log_progress("GetHouseByCommunitylist",
                     communityname, page + 1, total_pages)
        data_source = []
        hisprice_data_source = []
        for name in nameList:  # per house loop
            i = i + 1
            info_dict = {}
            try:
                housetitle = name.find("div", {"class": "title"})
                info_dict.update({u'title': housetitle.a.get_text().strip()})
                info_dict.update({u'link': housetitle.a.get('href')})

                houseaddr = name.find("div", {"class": "address"})
                info = houseaddr.div.get_text().split('|')
                info_dict.update({u'community': communityname})
                info_dict.update({u'housetype': info[1].strip()})
                info_dict.update({u'square': info[2].strip()})
                info_dict.update({u'direction': info[3].strip()})
                info_dict.update({u'decoration': info[4].strip()})

                housefloor = name.find("div", {"class": "flood"})
                floor_all = housefloor.div.get_text().split(
                    '-')[0].strip().split(' ')
                info_dict.update({u'floor': floor_all[0].strip()})
                info_dict.update({u'years': floor_all[-1].strip()})

                followInfo = name.find("div", {"class": "followInfo"})
                info_dict.update({u'followInfo': followInfo.get_text()})

                tax = name.find("div", {"class": "tag"})
                info_dict.update({u'taxtype': tax.get_text().strip()})

                totalPrice = name.find("div", {"class": "totalPrice"})
                info_dict.update({u'totalPrice': totalPrice.span.get_text()})

                unitPrice = name.find("div", {"class": "unitPrice"})
                info_dict.update({u'unitPrice': unitPrice.get('data-price')})
                info_dict.update({u'houseID': unitPrice.get('data-hid')})
                
                info_dict.update({u'channel': channel})
            except:
                continue
            # houseinfo insert into mysql
            data_source.append(info_dict)
            hisprice_data_source.append(
                {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"], "channel": channel})
            # model.Houseinfo.insert(**info_dict).upsert().execute()
            #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

        with model.database.atomic():
            if data_source:
                model.Houseinfo.insert_many(data_source).upsert().execute()
            if hisprice_data_source:
                model.Hisprice.insert_many(
                    hisprice_data_source).upsert().execute()
        time.sleep(1)


def get_sell_percommunity(city, community):
    baseUrl = urlUtil.toHttpUrl(community.link)
    url = baseUrl + u"chengjiao/"
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    return # 暂时不跑出售记录

    total_pages = get_total_pages(url)

    if total_pages == None:
        row = model.Sellinfo.select().where(model.Sellinfo.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"chengjiao/-p1%d-t11/" % page
            source_code = get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')

        logging.log_progress("GetSellByCommunitylist", community.title, page + 1, total_pages)
        
        data_source = []
        for ultag in soup.findAll("ul", {"class": "listContent"}):
            for name in ultag.find_all('li'):
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "title"})
                    info_dict.update({u'title': housetitle.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get('href')})
                    houseID = housetitle.a.get(
                        'href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID': houseID.strip()})

                    house = housetitle.get_text().strip().split(' ')
                    info_dict.update({u'community': community.title})
                    info_dict.update({u'communityId': community.id})
                    info_dict.update(
                        {u'housetype': house[1].strip() if 1 < len(house) else ''})
                    info_dict.update(
                        {u'square': house[2].strip() if 2 < len(house) else ''})

                    houseinfo = name.find("div", {"class": "houseInfo"})
                    info = houseinfo.get_text().split('|')
                    info_dict.update({u'direction': info[0].strip()})
                    info_dict.update(
                        {u'status': info[1].strip() if 1 < len(info) else ''})

                    housefloor = name.find("div", {"class": "positionInfo"})
                    floor_all = housefloor.get_text().strip().split(' ')
                    info_dict.update({u'floor': floor_all[0].strip()})
                    info_dict.update({u'years': floor_all[-1].strip()})

                    followInfo = name.find("div", {"class": "source"})
                    info_dict.update(
                        {u'source': followInfo.get_text().strip()})

                    totalPrice = name.find("div", {"class": "totalPrice"})
                    if totalPrice.span is None:
                        info_dict.update(
                            {u'totalPrice': totalPrice.get_text().strip()})
                    else:
                        info_dict.update(
                            {u'totalPrice': totalPrice.span.get_text().strip()})

                    unitPrice = name.find("div", {"class": "unitPrice"})
                    if unitPrice.span is None:
                        info_dict.update(
                            {u'unitPrice': unitPrice.get_text().strip()})
                    else:
                        info_dict.update(
                            {u'unitPrice': unitPrice.span.get_text().strip()})

                    dealDate = name.find("div", {"class": "dealDate"})
                    info_dict.update(
                        {u'dealdate': dealDate.get_text().strip().replace('.', '-')})
                    
                    info_dict.update({u'channel': channel})
                except:
                    continue
                # Sellinfo insert into mysql
                data_source.append(info_dict)
                # model.Sellinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            if data_source:
                model.Sellinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_community_perregion(city, regionname=u'xicheng'):
    baseUrl = u"http://%s.esf.fang.com/housing/" % (city)
    regionname = convert_district_for_community(baseUrl, regionname)

    url = baseUrl + regionname + "/"
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')

    if check_block(soup):
        return
    total_pages = get_total_pages(url)

    if total_pages == None:
        row = model.Community.select().where(model.Community.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            params = regionname.split('_')
            if len(params) > 4:
                params[len(params)-4] = str(page + 1)
    
            url_page = baseUrl +  '_'.join(params) + '/'
            source_code = get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')

        nameList = soup.findAll("div", {"class": "list"})
        i = 0
        logging.log_progress("GetCommunityByRegionlist",
                     regionname, page + 1, total_pages)
        data_source = []
        for name in nameList:  # Per house loop
            i = i + 1
            info_dict = {}
            try:
                communitytitle = name.find("a", {"class": "plotTit"})
                title = communitytitle.get_text().strip('\n')
                link = communitytitle.get('href')
                info_dict.update({u'title': title})
                info_dict.update({u'link': link})

                districtInfo = communitytitle.find_parent().find_next_sibling('p')
                district = districtInfo.findAll("a")

                info_dict.update({u'district': district[0].get_text()})
                info_dict.update({u'bizcircle': district[1].get_text()})

                tagList = districtInfo.get_text()
                info_dict.update({u'tagList': tagList.strip('\n')})

                onsale = name.find("ul", {"class": "sellOrRenthy"})
                info_dict.update(
                    {u'onsale': onsale.find('li').find('a').get_text().strip('\n').strip()})

                onrent = onsale.find('li').find_next_sibling('li').find("a")
                info_dict.update(
                    {u'onrent': onrent.get_text().strip('\n').strip()})

                year = onsale.find('li').find_next_sibling('li').find_next_sibling('li')
                info_dict.update({u'year': year.get_text()})

                # matchResult = re.match('http:|https:|\/\/(.*)\.fang.com.*', link, re.M |re.I)
               

                price = name.find("p", {"class": "priceAverage"})
                info_dict.update({u'price': price.span.get_text().strip('\n')})

                image = name.find("dl", {"class": "plotListwrap"}).find('dt').find('img')
                info_dict.update({u'image': image.get('src')})

                info_dict.update({u'channel': channel})

                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.iteritems():
                    info_dict.update({key: value})

                info_dict.update({u'city': city})

            except:
                continue
            # communityinfo insert into mysql
            data_source.append(info_dict)
            model.Community.insert(**info_dict).upsert().execute()
        
        time.sleep(1)


def get_rent_percommunity(city, communityname):
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"zufang/rs" + \
        urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Rentinfo.select().where(model.Rentinfo.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + \
                u"rent/pg%drs%s/" % (page,
                                     urllib2.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        logging.log_progress("GetRentByCommunitylist",
                     communityname, page + 1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class": "house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "info-panel"})
                    info_dict.update({u'title': housetitle.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get('href')})
                    houseID = housetitle.a.get(
                        'href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID': houseID})

                    region = name.find("span", {"class": "region"})
                    info_dict.update({u'region': region.get_text().strip()})

                    zone = name.find("span", {"class": "zone"})
                    info_dict.update({u'zone': zone.get_text().strip()})

                    meters = name.find("span", {"class": "meters"})
                    info_dict.update({u'meters': meters.get_text().strip()})

                    other = name.find("div", {"class": "con"})
                    info_dict.update({u'other': other.get_text().strip()})

                    subway = name.find("span", {"class": "fang-subway-ex"})
                    if subway is None:
                        info_dict.update({u'subway': ""})
                    else:
                        info_dict.update(
                            {u'subway': subway.span.get_text().strip()})

                    decoration = name.find("span", {"class": "decoration-ex"})
                    if decoration is None:
                        info_dict.update({u'decoration': ""})
                    else:
                        info_dict.update(
                            {u'decoration': decoration.span.get_text().strip()})

                    heating = name.find("span", {"class": "heating-ex"})
                    info_dict.update(
                        {u'heating': heating.span.get_text().strip()})

                    price = name.find("div", {"class": "price"})
                    info_dict.update(
                        {u'price': int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class": "price-pre"})
                    info_dict.update(
                        {u'pricepre': pricepre.get_text().strip()})

                    info_dict.update({u'channel': channel})
                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                # model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            if data_source:
                model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_house_perregion(city, district):
    baseUrl = u"http://%s.esf.fang.com" % (city)

    district = convert_district_for_house(baseUrl, district)

    url = baseUrl + u"/%s/" % district
    source_code = get_source_code(url)

    soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')
    if check_block(soup):
        return

    total_pages = get_total_pages(url)
    if total_pages == None:
        row = model.Houseinfo.select.where(model.Houseinfo.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"/%s/i3%d/" % (district, page + 1)
            logging.info(url_page)
            source_code = get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml',  from_encoding='gb18030')
        i = 0

        logging.log_progress("GetHouseByRegionlist", district, page + 1, total_pages)
        data_source = []
        hisprice_data_source = []
        for ultag in soup.findAll("div", {"class": "shop_list"}):
            for name in ultag.select('dl[data-bg]'):
                i = i + 1
                info_dict = {}
                metadata = {}
                try:
                    housetitle = name.find("span", {"class": "tit_shop"}).find_parent()

                    info_dict.update(
                        {u'title': housetitle.get('title')})
                    info_dict.update({u'link': 'https://wuhan.esf.fang.com' + housetitle.get('href')})

                    houseJson = json.loads(name.get('data-bg'))

                    info_dict.update({u'houseID': houseJson['houseid']})
     
                    houseinfo = name.find("p", {"class": "tel_shop"})

                    info = houseinfo.get_text().split('|')

                    info_dict.update({u'housetype': info[0]})
                    info_dict.update({u'square': info[1]})
                    info_dict.update({u'direction': info[3]})
                    info_dict.update({u'floor': info[2]})
                    info_dict.update({u'years': info[4]})
                   
                    image = name.find("img")
                    info_dict.update({u'image': image.get('src')})

                    positionInfo = name.find("p", {"class": "add_shop"})
                    info_dict.update({u'community': positionInfo.a.get('title')})
                    communityInfo = positionInfo.a
                    if communityInfo != None:
                        communityHref = communityInfo.get('href');
                        communityId = communityHref.lstrip('/')
                        if len(communityId) > 0:
                            info_dict.update({u'communityId': communityId})

                    metadata.update(
                        {u'address': positionInfo.find('span').get_text().strip()})        

                    taxfree = name.find("span", {"class": "colorPink"})
                    if taxfree == None:
                        info_dict.update({u"taxtype": ""})
                    else:
                        info_dict.update(
                            {u"taxtype": taxfree.get_text().strip()})
                    
                    address_dt = name.find("span", {"class": "icon_dt"})
                    if address_dt != None:
                        metadata.update(
                            {u'address_dt': address_dt.get_text().strip()})                

                    totalPrice = name.find("dd", {"class": "price_right"})

                    info_dict.update(
                        {u'totalPrice': totalPrice.find('b').get_text()})

                    unitPrice = totalPrice.findAll("span")
                    if unitPrice != None and len(unitPrice) > 0:
                        unitPriceText = unitPrice[len(unitPrice) - 1].get_text()
                        unitPriceRe = re.findall('\d+', unitPriceText)
                        if len(unitPriceRe) > 0:
                            info_dict.update({u'unitPrice': str(unitPriceRe[0])})
                  
                    info_dict.update({u'channel': channel})
                    info_dict.update({u'metadata': json.dumps(metadata)})
                except:
                    continue

                # Houseinfo insert into mysql
                data_source.append(info_dict)
                hisprice_data_source.append(
                    {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})
                # model.Houseinfo.insert(**info_dict).upsert().execute()
                #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

        with model.database.atomic():
            if data_source:
                model.Houseinfo.insert_many(data_source).upsert().execute()
            if hisprice_data_source:
                model.Hisprice.insert_many(hisprice_data_source).upsert().execute()

        time.sleep(1)


def get_rent_perregion(city, district):
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"zufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    if total_pages == None:
        row = model.Rentinfo.select().where(model.Rentinfo.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"zufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        logging.log_progress("GetRentByRegionlist", district, page + 1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class": "house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "info-panel"})
                    info_dict.update(
                        {u'title': housetitle.h2.a.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get("href")})
                    houseID = name.get("data-housecode")
                    info_dict.update({u'houseID': houseID})

                    region = name.find("span", {"class": "region"})
                    info_dict.update({u'region': region.get_text().strip()})

                    zone = name.find("span", {"class": "zone"})
                    info_dict.update({u'zone': zone.get_text().strip()})

                    meters = name.find("span", {"class": "meters"})
                    info_dict.update({u'meters': meters.get_text().strip()})

                    other = name.find("div", {"class": "con"})
                    info_dict.update({u'other': other.get_text().strip()})

                    subway = name.find("span", {"class": "fang-subway-ex"})
                    if subway == None:
                        info_dict.update({u'subway': ""})
                    else:
                        info_dict.update(
                            {u'subway': subway.span.get_text().strip()})

                    decoration = name.find("span", {"class": "decoration-ex"})
                    if decoration == None:
                        info_dict.update({u'decoration': ""})
                    else:
                        info_dict.update(
                            {u'decoration': decoration.span.get_text().strip()})

                    heating = name.find("span", {"class": "heating-ex"})
                    if decoration == None:
                        info_dict.update({u'heating': ""})
                    else:
                        info_dict.update(
                            {u'heating': heating.span.get_text().strip()})

                    price = name.find("div", {"class": "price"})
                    logging.info(price)
                    info_dict.update(
                        {u'price': int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class": "price-pre"})
                    info_dict.update(
                        {u'pricepre': pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                # model.Rentinfo.insert(**info_dict).upsert().execute()

        with model.database.atomic():
            if data_source:
                model.Rentinfo.insert_many(data_source).upsert().execute()
        time.sleep(1)


def get_communityinfo_by_url(url):
    source_code = misc.get_source_code(urlUtil.toHttpUrl(url))
    soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')

    if check_block(soup):
        return

    communityinfos = soup.find("div", {"class": "Rinfolist"}).findAll('li')
    res = {}
    for info in communityinfos:
        key_type = {
            u"建筑年代": u'year',
            u"建筑类型": u'housetype',
            u"物业公司": u'service',
            u"开发商": u'company',
            u"楼栋总数": u'building_num',
            u"房屋总数": u'house_num',
        }
        try:
            key = info.find("b")
            key_info = key_type[key.get_text().strip()]
            value_info = info.get_text().strip()
            res.update({key_info: value_info})

            res.update({u'id': soup.find('input', {'id' : 'projCode'}).get('value')})

        except:
            continue

    thumbnail = soup.find("ul", {"id": "imageShowSmall"})
    images = []
    if thumbnail != None:
        for li in thumbnail.find_all('li'):
            try:
                image = li.find('img')
                images.append(image.get('src'))
            except:
                continue
            
        imagelist = ','.join(images)
        res.update({'imagelist': imagelist})

    return res


def check_block(soup):
    if soup.title.string == "414 Request-URI Too Large":
        logging.error(
            "Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False


def get_total_pages(url):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')
    total_pages = 0
    logging.info('url1:' + url)
    try:
        page_info = soup.find('div', {'class': 'page_al'})
        if page_info == None:
            if soup.find('div', {'class': 'fanye'}):
                page_info = soup.find('div', {'class': 'fanye'}).findAll('span')
        else:
            page_info = page_info.findAll('p')

        if page_info != None:
            pagetext = page_info[len(page_info)-1].get_text();
            pagere = re.findall('\d+', pagetext)
            if len(pagere) > 0:
                total_pages = int(pagere[0])
        else:
            page_info = soup.find('a', {'id' :'ctl00_hlk_last'})
            # 处理成交页面的页码
            if url.find('chengjiao'):
                if page_info != None:
                    href = page_info.get('href')
                    matchResult = re.match('http:|https:|\/\/(.*)\.fang.com(.*)\/-p1(\d+)-t11(.*)', href, re.M |re.I)
                    if matchResult:
                        total_pages = int(matchResult[2])
                else:
                    dealPageWarp = soup.find('div', {'class': 'dealPagewrap'})
                    if dealPageWarp != None and dealPageWarp.find('a', {'class': 'selected'}):
                        total_pages = 1
                    else:
                        # 即使没有记录，也设置为1页，因为下面页码为1的时候，会设置成50页
                        total_pages = 1
                
    except AttributeError as e:
        page_info = None

    logging.info(str(total_pages))

    # if it doesnot get total page, then return default value 50
    if page_info == None and total_pages == 0:
        return 50

    return total_pages

def get_source_code(url):
    source_code = misc.get_source_code(url)
    redirecturl = if_redirect_page(source_code)

    if redirecturl != False:
        source_code = misc.get_source_code(redirecturl)

    return source_code

def if_redirect_page(source_code):
    soup = BeautifulSoup(source_code, 'lxml')
    title = soup.find('head').find('title').get_text();
    logging.debug("title: " + title)

    if title.find(u'跳转') >=0:
        redirectBtn = soup.find('a', {"class": 'btn-redir'})
        if redirectBtn != None:
            return redirectBtn.get('href')
    return False

def convert_district_for_house(url, district):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')
   
    try:
        screenList = soup.find('div', {'class': 'screen_al'}).findAll('li')
        for screen in screenList:
            screenTitle = screen.find('span', {'class': 'screen_title'})
            if screenTitle != None and screenTitle.get_text() == u'区域':
                for tag in screen.findAll('li'):
                    item = tag.a
                    if item.get_text() ==  district:
                        districtId = item.get('href').lstrip('/')
                        return districtId
    
    except Exception as e:
        logging.error(e)

    raise RuntimeError("未找到指定对应区域 { %s } 的ID" % district)

def convert_district_for_community(url, district):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml', from_encoding='gb18030')
   
    try:
        screen = soup.find('div', {'class': 'quxian'})
        screenTitle = screen.find('span', {'class': 'type'})
        if screenTitle != None and screenTitle.get_text().lstrip(u'：').find(u'区域') > -1:
            for item in screen.find('div', "qxName").findAll('a'):
                if item.get_text() ==  district:
                    districtId = item.get('href').lstrip('/housing').strip('/')
                    return districtId
    
    except Exception as e:
        logging.error(e)

    raise RuntimeError("未找到指定对应区域 { %s } 的ID" % district)
