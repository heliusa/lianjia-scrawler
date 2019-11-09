# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import model
import misc
import time
import datetime
import urllib2
import re
from util.tracking import Tracking
import traceback
from util.logger import logging

tracking = Tracking()

channel = 'lianjia'

def GetHouseByCommunitylist(city, communitylist):
    tracking.start("Get House By Community")

    for community in communitylist:
        try:
            get_house_percommunity(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community.title + "Fail")
            pass

    tracking.end()

def GetSellByCommunitylist(city, communitylist):
    tracking.start("Get Sell Infomation")
    for community in communitylist:
        try:
            get_sell_percommunity(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community.title + "Fail")
            pass
    tracking.end()

def GetRentByCommunitylist(city, communitylist):

    tracking.start("Get Rent Infomation")

    for community in communitylist:
        try:
            get_rent_percommunity(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community.title + "Fail")
            pass
    tracking.end()


def GetCommunityByRegionlist(city, regionlist=[u'xicheng']):
    tracking.start("Get Community Infomation")
    for regionname in regionlist:
        try:
            get_community_perregion(city, regionname)
            logging.info(regionname + "Done")
        except Exception as e:
            logging.error(e)
            logging.error(regionname + "Fail")
            pass
    tracking.end()


def GetHouseByRegionlist(city, regionlist=[u'xicheng']):
    tracking.start()
    for regionname in regionlist:
        logging.info("Get Onsale House Infomation in %s" % regionname)
        try:
            get_house_perregion(city, regionname)
        except Exception as e:
            logging.error(e)
            pass
    tracking.end()


def GetRentByRegionlist(city, regionlist=[u'xicheng']):
    tracking.start()
    for regionname in regionlist:
        logging.info("Get Rent House Infomation in %s" % regionname)
        try:
            get_rent_perregion(city, regionname)
        except Exception as e:
            logging.error(e)
            pass
    tracking.end()


def get_house_percommunity(city, community):
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"ershoufang/rs" + \
        urllib2.quote(community.title.encode('utf8')) + "/"
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
                                           urllib2.quote(community.title.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class": "clear"})
        i = 0
        tracking.log_progress("GetHouseByCommunitylist",
                     community.title, page + 1, total_pages)
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
                info_dict.update({u'community': community.title})
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
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"chengjiao/rs" + \
        urllib2.quote(community.title.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Sellinfo.select().where(model.Sellinfo.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + \
                u"chengjiao/pg%drs%s/" % (page,
                                          urllib2.quote(community.title.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        tracking.log_progress("GetSellByCommunitylist",
                     community.title, page + 1, total_pages)
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
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"xiaoqu/" + regionname + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Community.select().where(model.Community.channel == channel).count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"xiaoqu/" + regionname + "/pg%d/" % page
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class": "clear"})
        i = 0
        tracking.log_progress("GetCommunityByRegionlist",
                     regionname, page + 1, total_pages)
        data_source = []
        for name in nameList:  # Per house loop
            i = i + 1
            info_dict = {}
            try:
                communitytitle = name.find("div", {"class": "title"})
                title = communitytitle.get_text().strip('\n')
                link = communitytitle.a.get('href')
                info_dict.update({u'title': title})
                info_dict.update({u'link': link})

                district = name.find("a", {"class": "district"})
                info_dict.update({u'district': district.get_text()})

                bizcircle = name.find("a", {"class": "bizcircle"})
                info_dict.update({u'bizcircle': bizcircle.get_text()})

                tagList = name.find("div", {"class": "tagList"})
                info_dict.update({u'tagList': tagList.get_text().strip('\n')})

                onsale = name.find("a", {"class": "totalSellCount"})
                info_dict.update(
                    {u'onsale': onsale.span.get_text().strip('\n')})

                onrent = name.find("a", {"title": title + u"租房"})
                info_dict.update(
                    {u'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

                info_dict.update({u'id': name.get('data-housecode')})

                price = name.find("div", {"class": "totalPrice"})
                info_dict.update({u'price': price.span.get_text().strip('\n')})

                image = name.find("img", {"class": "lj-lazy"})
                info_dict.update({u'image': image.get('data-original')})
                
                info_dict.update({u'channel': channel})

                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.iteritems():
                    info_dict.update({key: value})

                info_dict.update({u'city': city})

                model.Community.insert(**info_dict).upsert().execute()

            except:
                logging.error('Get Community error: ' + title)
                logging.error(info_dict)
                continue
            # communityinfo insert into mysql
          
            
        # 如果批量插入SQL会超长报错，故改成单条插入    
        # with model.database.atomic():
        #     if data_source:
        #         model.Community.insert_many(data_source).upsert().execute()
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
        tracking.log_progress("GetRentByCommunitylist",
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
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"ershoufang/%s/" % district
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
            url_page = baseUrl + u"ershoufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        tracking.log_progress("GetHouseByRegionlist", district, page + 1, total_pages)
        data_source = []
        hisprice_data_source = []
        for ultag in soup.findAll("ul", {"class": "sellListContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "title"})
                    info_dict.update(
                        {u'title': housetitle.a.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get('href')})
                    houseID = housetitle.a.get('data-housecode')
                    info_dict.update({u'houseID': houseID})

                    houseinfo = name.find("div", {"class": "houseInfo"})
                    info = houseinfo.get_text().split('|')

                    info_dict.update({u'housetype': info[0]})
                    info_dict.update({u'square': info[1]})
                    info_dict.update({u'direction': info[2]})
                    info_dict.update({u'decoration': info[3]})
                    info_dict.update({u'floor': info[4]})
                    info_dict.update({u'years': info[5]})

                    image = name.find("img", {"class": "lj-lazy"})
                    info_dict.update({u'image': image.get('data-original')})

                    positionInfo = name.find("div", {"class": "positionInfo"})
                    info_dict.update({u'community': positionInfo.get_text().strip()})
                    regionInfo = positionInfo.find("a", {"data-el": "region"})
                    if regionInfo != None:
                        regionHref = regionInfo.get('href');
                        communityIdRe = re.findall('\d+', str(regionHref))
                        if len(communityIdRe) > 0:
                            info_dict.update({u'communityId': communityIdRe[0]})

                    followInfo = name.find("div", {"class": "followInfo"})
                    info_dict.update(
                        {u'followInfo': followInfo.get_text().strip()})

                    taxfree = name.find("span", {"class": "taxfree"})
                    if taxfree == None:
                        info_dict.update({u"taxtype": ""})
                    else:
                        info_dict.update(
                            {u"taxtype": taxfree.get_text().strip()})

                    totalPrice = name.find("div", {"class": "totalPrice"})
                    info_dict.update(
                        {u'totalPrice': totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class": "unitPrice"})
                    info_dict.update(
                        {u'unitPrice': unitPrice.get("data-price")})

                    info_dict.update({u'channel': channel})

                    model.Houseinfo.insert(**info_dict).upsert().execute()

                except:
                    logging.error('Get House error: ' + housetitle)
                    logging.error(info_dict)
                    continue

                # Houseinfo insert into mysql
                #data_source.append(info_dict)
                hisprice_data_source.append(
                    {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"],  "channel": channel})
                # model.Houseinfo.insert(**info_dict).upsert().execute()
                #model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

        with model.database.atomic():
            # if data_source:
            #     model.Houseinfo.insert_many(data_source).upsert().execute()
            if hisprice_data_source:
                model.Hisprice.insert_many(
                    hisprice_data_source).upsert().execute()
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
        tracking.log_progress("GetRentByRegionlist", district, page + 1, total_pages)
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
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    communityinfos = soup.findAll("div", {"class": "xiaoquInfoItem"})
    res = {}
    for info in communityinfos:
        key_type = {
            u"建筑年代": u'year',
            u"建筑类型": u'housetype',
            u"物业费用": u'cost',
            u"物业公司": u'service',
            u"开发商": u'company',
            u"楼栋总数": u'building_num',
            u"房屋总数": u'house_num',
        }
        try:
            key = info.find("span", {"xiaoquInfoLabel"})
            value = info.find("span", {"xiaoquInfoContent"})
            key_info = key_type[key.get_text().strip()]
            value_info = value.get_text().strip()
            res.update({key_info: value_info})

        except:
            continue

    thumbnail = soup.find("ol", {"id": "overviewThumbnail"})
    images = []
    if thumbnail != None:
        for li in thumbnail.find_all('li'):
            try:
                image = li.get("data-src")
                images.append(image)
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
