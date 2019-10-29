from peewee import *
import datetime
import settings

if settings.DBENGINE.lower() == 'mysql':
    database = MySQLDatabase(
        settings.DBNAME,
        host=settings.DBHOST,
        port=settings.DBPORT,
        user=settings.DBUSER,
        passwd=settings.DBPASSWORD,
        charset='utf8',
        use_unicode=True,
    )

elif settings.DBENGINE.lower() == 'sqlite3':
    database = SqliteDatabase(settings.DBNAME)

elif settings.DBENGINE.lower() == 'postgresql':
    database = PostgresqlDatabase(
        settings.DBNAME,
        user=settings.DBUSER,
        password=settings.DBPASSWORD,
        host=settings.DBHOST,
        charset='utf8',
        use_unicode=True,
    )

else:
    raise AttributeError("Please setup datatbase at settings.py")


class BaseModel(Model):

    class Meta:
        database = database


class Community(BaseModel):
    id = CharField(max_length=128)
    title = CharField()
    link = CharField()
    district = CharField(null=True)
    bizcircle = CharField(null=True)
    tagList = CharField(null=True, max_length=1000)
    onsale = CharField(null=True)
    onrent = CharField(null=True)
    year = CharField(null=True)
    housetype = CharField(null=True)
    cost = CharField(null=True)
    service = CharField(null=True)
    company = CharField(null=True)
    building_num = CharField(null=True)
    house_num = CharField(null=True)
    price = CharField(null=True)
    city = CharField(null=True)
    image = TextField(null=True)
    imagelist = TextField(null=True)
    channel = CharField()
    metadata = TextField(null=True)
    validdate = DateTimeField(default=datetime.datetime.now)
    class Meta:
        primary_key = CompositeKey('id', 'channel')


class Houseinfo(BaseModel):
    houseID = CharField()
    title = CharField()
    link = CharField()
    community = CharField()
    communityId = CharField(null=True, max_length=128)
    years = CharField()
    housetype = CharField()
    square = CharField()
    direction = CharField()
    floor = CharField()
    taxtype = CharField()
    totalPrice = CharField()
    unitPrice = CharField()
    followInfo = CharField()
    decoration = CharField()
    image = TextField(null=True)
    imagelist = TextField(null=True)
    channel = CharField()
    metadata = TextField(null = True)
    validdate = DateTimeField(default=datetime.datetime.now)
    class Meta:
        primary_key = CompositeKey('houseID', 'channel')


class Hisprice(BaseModel):
    houseID = CharField()
    totalPrice = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    channel = CharField()
    metadata = TextField(null = True)

    class Meta:
        primary_key = CompositeKey('houseID', 'totalPrice', 'channel')


class Sellinfo(BaseModel):
    houseID = CharField(primary_key=True)
    title = CharField()
    link = CharField()
    community = CharField()
    communityId = CharField(null=True, max_length=128)
    years = CharField()
    housetype = CharField()
    square = CharField()
    direction = CharField()
    floor = CharField()
    status = CharField()
    source = CharField()
    totalPrice = CharField()
    unitPrice = CharField()
    dealdate = CharField(null=True)
    image = TextField(null=True)
    imagelist = TextField(null=True)
    channel = CharField()
    metadata = TextField(null=True)
    updatedate = DateTimeField(default=datetime.datetime.now)


class Rentinfo(BaseModel):
    houseID = CharField(primary_key=True)
    title = CharField()
    link = CharField()
    region = CharField()
    zone = CharField()
    meters = CharField()
    other = CharField()
    subway = CharField()
    decoration = CharField()
    heating = CharField()
    price = CharField()
    pricepre = CharField()
    channel = CharField()
    metadata = TextField(null=True)
    updatedate = DateTimeField(default=datetime.datetime.now)


def database_init():
    database.connect()
    database.create_tables(
        [Community, Houseinfo, Hisprice, Sellinfo, Rentinfo], safe=True)
    database.close()
