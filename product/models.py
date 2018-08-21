from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


TYPES = (
    ('A', 'ATV'),
    ('V', 'Automobile'),
    ('M', 'Boat'),
    ('D', 'Dirt Bike'),
    ('U', 'Heavy Duty Trucks'),
    ('E', 'Industrial Equipment'),
    ('J', 'Jet Ski'),
    ('K', 'Medium Duty/Box Trucks'),
    ('C', 'Motorcycle'),
    ('H', 'Other Goods'),
    ('R', 'Recreational Vehicle (RV)'),
    ('S', 'Snowmobile'),
    ('L', 'Trailers'),
)


class VehicleMakes(models.Model):
    type = models.CharField(_('Type'), choices=TYPES, max_length=1, default='V')
    code = models.CharField(_('Code'), max_length=4)
    description = models.CharField(_('Description'), max_length=30)
    count = models.IntegerField(_('Count'), null=True, blank=True)

    class Meta:
        verbose_name = _('Make')
        verbose_name_plural = _('Makes')
        ordering = ['type', 'description']

    def __str__(self):
        return dict(TYPES)[self.type] + '-' + self.description + ' - ' + str(self.count)

    def scrap_link(self):
        scrap_link = '<a href="/scrap_copart/?type={type}&description={description}&code={code}">Scrap {description}</a>'.format
        return mark_safe(scrap_link(type=self.type, description=self.description, code=self.code))


class Vehicle(models.Model):
    lot = models.IntegerField(_('Lot'))
    vin = models.CharField(_('VIN'), max_length=17, default='')

    # General Information
    name = models.CharField(_('Name'), max_length=255, default='')
    make = models.CharField(_('Make'), max_length=50, default='')
    model = models.CharField(_('Model'), max_length=50, default='')
    year = models.IntegerField(_('Year'), null=True, blank=True)
    currency = models.CharField(_('Currency'), max_length=3, default='')
    avatar = models.URLField(_('Avatar'), null=True, blank=True)

    # Lot Information
    doc_type_ts = models.CharField(_('Doc Type TS'), max_length=2, default='')
    doc_type_stt = models.CharField(_('Doc Type STT'), max_length=2, default='')
    doc_type_td = models.CharField(_('Doc Type TD'), max_length=100, default='')
    odometer_orr = models.IntegerField(_('Odometer ORR'), default=0)
    odometer_ord = models.CharField(_('Odometer ORD'), max_length=50, default='')
    lot_highlights = models.CharField(_('Highlights'), max_length=50, null=True, blank=True)
    lot_seller = models.CharField(_('Seller'), max_length=100, null=True, blank=True)
    lot_1st_damage = models.CharField(_('Damage'), max_length=30, null=True, blank=True)
    lot_2nd_damage = models.CharField(_('Secondary Damage'), max_length=30, null=True, blank=True)
    retail_value = models.IntegerField(_('Est. Retail Value'), default=0)

    # Features
    body_style = models.CharField(_('Body Style'), max_length=50, null=True, blank=True)
    color = models.CharField(_('Color'), max_length=50, null=True, blank=True)
    engine_type = models.CharField(_('Engine Type'), max_length=50, null=True, blank=True)
    cylinders = models.CharField(_('Cylinders'), max_length=50, null=True, blank=True)
    transmission = models.CharField(_('Transmission'), max_length=50, null=True, blank=True)
    drive = models.CharField(_('Drive'), max_length=50, null=True, blank=True)
    fuel = models.CharField(_('Fuel'), max_length=50, null=True, blank=True)
    keys = models.CharField(_('Keys'), max_length=20, null=True, blank=True)
    notes = models.TextField(_('Notes'), null=True, blank=True)

    # Bid Information
    bid_status = models.CharField(_('Bid Status'), max_length=30, default='')
    sale_status = models.CharField(_('Sale Status'), max_length=30, default='')
    current_bid = models.IntegerField(_('Current Bid'), default=0)
    buy_today_bid = models.IntegerField(_('Buy Today Bid'), default=0)
    sold_price = models.IntegerField(_('Sold Price'), default=0)

    # Sale Information
    location = models.CharField(_('Location'), max_length=50, default='')
    lane = models.CharField(_('Lane'), max_length=1, default='-')
    item = models.CharField(_('Item'), max_length=20, default='')
    grid = models.CharField(_('Grid/Row'), max_length=5, default='')
    sale_date = models.DateTimeField(_('Sale Date'), null=True, blank=True)
    last_updated = models.DateTimeField(_('Last Updated'), null=True, blank=True)

    foregoing = models.ForeignKey('self', verbose_name=_('Foregoing'), on_delete=models.CASCADE, null=True, blank=True)
    show = models.BooleanField(_('Show'), default=True)
    source = models.BooleanField(_('Source'), default=True)

    images = models.TextField(_('Image Urls'), null=True, blank=True)
    thumb_images = models.TextField(_('Thumbnail Image Urls'), null=True, blank=True)
    # high_images = models.TextField(_('High Resolution Image Urls'), null=True, blank=True)

    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        ordering = ['pk']

    def __str__(self):
        return self.vin + ' ' + str(self.lot)

    def odometer(self):
        return str(self.odometer_orr) + ' ' + (self.odometer_ord[0] if self.odometer_ord else '')

    def lane_row(self):
        if self.source:
            return self.lane + ' / ' + self.grid
        else:
            return self.lane
    lane_row.short_description = 'Lane / Row'

    def doc_type(self):
        if self.source:
            return self.doc_type_stt + ' - ' + self.doc_type_ts
        else:
            return self.doc_type_td

    def est_retail_value(self):
        return '$' + str(self.retail_value) + ' ' + self.currency
    est_retail_value.short_description = 'Est. Retail Value'

    def current_bid_(self):
        return '$' + str(self.current_bid) + ' ' + self.currency
    current_bid_.short_description = 'Current Bid'

    def sold_price_(self):
        return '$' + str(self.sold_price) + ' ' + self.currency
    current_bid_.short_description = 'Current Bid'

    def avatar_img(self):
        return mark_safe('<a id="lot-images_{lot}"><img src="{url}" title="{title}" width="96" height="72"></a>'
                         .format(lot=self.lot, url=self.avatar, title=self.name))
    avatar_img.short_description = 'Avatar'


# class Location(models.Model):
#     phone = models.CharField(_('Phone'), max_length=255, null=True, blank=True)
#     fax = models.CharField(_('Fax'), max_length=255, null=True, blank=True)
#     hours = models.CharField(_('Hours'), max_length=255, null=True, blank=True)
#     free_wifi = models.CharField(_('Free WiFi'), max_length=255, null=True, blank=True)
#     address = models.CharField(_('Address'), max_length=255, null=True, blank=True)
#     mailing_address = models.CharField(_('Mailing Address'), max_length=255, null=True, blank=True)
#     location = models.CharField(_('Location'), max_length=255, null=True, blank=True)
#     general_manager = models.CharField(_('General Manager'), max_length=255, null=True, blank=True)
#     regional_manager = models.CharField(_('Regional Manager'), max_length=255, null=True, blank=True)
#
#     class Meta:
#         verbose_name = _('Location')
#         verbose_name_plural = _('Locations')
#
#     def __str__(self):
#         return self.address
#
#
# class CronJob(models.Model):
#     name = models.CharField(_('JobName'), max_length=255, null=True, blank=True)
#
#     class Meta:
#         verbose_name = _('CronJob')
#         verbose_name_plural = _('CronJobs')
#         ordering = ['pk']
#
#     def __str__(self):
#         return self.name
#
#
# class CronFinder(models.Model):
#     finder = models.ForeignKey(VehicleMakes, verbose_name=_('VehicleMakes'), on_delete=models.CASCADE)
#     job = models.ForeignKey(CronJob, verbose_name=_('CronJob'), on_delete=models.CASCADE)
#
#     def __str__(self):
#         return dict(TYPES)[self.finder.type] + '-' + self.finder.description + ' - ' + str(self.finder.count)
