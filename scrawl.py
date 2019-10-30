from channel import lianjia,fang
import model
import settings
import sys
from util.log import Log
import getopt

logging = Log()

def get_communitylist(channel, city):
    res = []
    for community in model.Community.select().where(model.Community.city == city , model.Community.channel == channel):
        res.append(community)
    return res

if __name__ == "__main__":
    args  = sys.argv
    ch = lianjia
    module = 'full'
    chstr = 'lianjia'
    
    moduleList = []

    options, args = getopt.getopt(sys.argv[1:], 'c:m')
    logging.info(options)

    for opt, value in options:
        if opt in ("-c"):  
            chstr = value
        if opt in ("-m"):  
            moduleList.append(value)

    if len(moduleList) == 0:
        moduleList = ['house', 'rent', 'community', 'sell']

    logging.info("Channel is %s", chstr)

    if chstr == 'fang':
        ch = fang
    elif chstr == 'lianjia':
        ch = lianjia
    else:
        raise LookupError('Channel parameter is wrong!')

    logging.info(settings.CHANNEL_PARAM[chstr]);
    
    regionlist = settings.CHANNEL_PARAM[chstr]['REGIONLIST']  # only pinyin support
    city = settings.CHANNEL_PARAM[chstr]['CITY']

    if 'init' in moduleList:
        model.database_init()
    if 'house' in moduleList:
        ch.GetHouseByRegionlist(city, regionlist)
    if 'rent' in moduleList:
        ch.GetRentByRegionlist(city, regionlist)
    # Init,scrapy celllist and insert database; could run only 1st time
    if 'community' in moduleList:
        ch.GetCommunityByRegionlist(city, regionlist)
    communitylist = get_communitylist(chstr, city)  # Read celllist from database
    if 'sell' in moduleList:
        ch.GetSellByCommunitylist(city, communitylist)


