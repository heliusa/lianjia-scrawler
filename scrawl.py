from channel import lianjia,fang
import model
import settings
import sys
from util.log import Log

logging = Log()

def get_communitylist(channel, city):
    res = []
    for community in model.Community.select().where(model.Community.city == city , model.Community.channel == channel):
        res.append(community)
    return res

if __name__ == "__main__":
    args  = sys.argv
    ch = lianjia
    chstr = 'lianjia'
    if len(args) > 1:
        chstr = args[1]
        if chstr == 'fang':
            ch = fang
        elif chstr == 'lianjia':
            ch = lianjia    
        else:
            raise LookupError('Channel parameter is wrong!')
        
        logging.info("Channel is %s", chstr)
    else:
        logging.info("Channel is lianjia")    


    logging.info(settings.CHANNEL_PARAM[chstr]);
    regionlist = settings.CHANNEL_PARAM[chstr]['REGIONLIST']  # only pinyin support
    city = settings.CHANNEL_PARAM[chstr]['CITY']
    #model.database_init()
    ch.GetHouseByRegionlist(city, regionlist)
    #ch.GetRentByRegionlist(city, regionlist)
    # Init,scrapy celllist and insert database; could run only 1st time
    ch.GetCommunityByRegionlist(city, regionlist)
    communitylist = get_communitylist(chstr, city)  # Read celllist from database
    ch.GetSellByCommunitylist(city, communitylist)


