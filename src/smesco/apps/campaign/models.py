import random

from django.db import models
from django.urls import reverse
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from .utils import file_cleanup


class TimesStampedModel(models.Model):
    """
    Class for adding created date and updated date
    """
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class BannerEntryQuery(models.QuerySet):
    def published(self):
        return self.filter(published=True)

    def random_banner(self):
        return self.published().order_by('?')

    def get_featured_banner(self):
        return random.choice(self.published())


class Banner(TimesStampedModel):
    image_desktop = models.ImageField(_('Image Desktop'), upload_to='campaign/banner/')
    image_mobile = models.ImageField(_('Image Mobile'), upload_to='campaign/banner/')
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), max_length=255)
    url = models.URLField(_('Url'), default='')
    number = models.IntegerField(_('Number'), default=1)
    valid_from = models.DateTimeField(_('Valid From'), default='')
    valid_until = models.DateTimeField(_('Valid Until'), default='')
    published = models.BooleanField(_('Published'), default=True)
    objects = BannerEntryQuery.as_manager()

    _metadata = {
        'title': 'title',
        'description': 'description',
        'url': 'get_absolute_url',
        'image': 'get_meta_image',
        'og_type': 'article',
        'og_description': 'description',
        'gplus_type': 'article',
        'gplus_description': 'description',
        'twitter_type': 'article',
        'twitter_description': 'description',
        'twitter_creator': '@smesco',
        'twitter_site': '@smesco',
        'site_name': 'Jims Honey',
        'number': 'number',
        'valid_from': 'valid_from',
        'valid_until': 'valid_until',
        'published_time': 'date_created',
        'modified_time': 'get_date',
        'locale': 'id',
    }

    def get_meta_image(self):
        return self.image_desktop.url

    def get_date(self, param):
        if param in ['published_time', 'modified_time']:
            return self.date_created.strftime('%Y-%m-%dT%H:%M:%S:%z')
        return self.date_created

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('banner:banner-detail', kwargs={'slug': self.slug})

    def remove_on_image_update(self):
        try:
            obj = Banner.objects.get(id=self.id)
        except Banner.DoesNotExist:
            return

        if obj.image_desktop and self.image_desktop and obj.image_desktop != self.image_desktop:
            obj.image_desktop.delete()

        if obj.image_mobile and self.image_mobile and obj.image_mobile != self.image_mobile:
            obj.image_mobile.delete()

    def save(self, *args, **kwargs):
        self.remove_on_image_update()
        return super(Banner, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['-date_created', ]


post_delete.connect(file_cleanup, sender=Banner, dispatch_uid='Banner.file_cleanup')


class BannerMiniEntryQuery(models.QuerySet):
    def published(self):
        return self.all()

    def random_banner_mini(self):
        return self.published().order_by('')[:4]

    def get_featured_banner_mini(self):
        return random.choice(self.published())


class BannerMini(TimesStampedModel):
    image = models.ImageField(_('Image'), upload_to='campaign/banner_mini/')
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    caption = models.TextField(_('Caption'))
    url = models.CharField(_('Click URL'), max_length=255)
    description = models.TextField(_('Description'), max_length=255)
    sort_priority = models.IntegerField(_('Sort Priority'), default=0)
    published = models.BooleanField(_('Published'), default=True)
    objects = BannerMiniEntryQuery.as_manager()

    _metadata = {
        'title': 'title',
        'description': 'description',
        'url': 'get_absolute_url',
        'image': 'get_meta_image',
        'og_type': 'article',
        'og_description': 'description',
        'gplus_type': 'article',
        'gplus_description': 'description',
        'twitter_type': 'article',
        'twitter_description': 'description',
        'twitter_creator': '@smesco',
        'twitter_site': '@smesco',
        'site_name': 'Jims Honey',
        'published_time': 'date_created',
        'modified_time': 'get_date',
        'locale': 'id',
    }

    def get_meta_image(self):
        return self.image.url

    def get_date(self, param):
        if param in ['published_time', 'modified_time']:
            return self.date_created.strftime('%Y-%m-%dT%H:%M:%S:%z')
        return self.date_created

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('bannermini:bannermini-detail', kwargs={'slug': self.slug})

    def remove_on_image_update(self):
        try:
            obj = BannerMini.objects.get(id=self.id)
        except BannerMini.DoesNotExist:
            return

        if obj.image and self.image and obj.image != self.image:
            obj.image.delete()

    def _get_unique_slug(self, slug):
        unique_slug = slug
        num = 1
        while BannerMini.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        self.remove_on_image_update()

        slug = slugify(self.title)
        if not self.slug or self.slug != slug:
            self.slug = self._get_unique_slug(slug)

        return super(BannerMini, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('BannerMini')
        verbose_name_plural = _('BannerMinis')
        ordering = ['-date_created', ]


post_delete.connect(file_cleanup, sender=BannerMini, dispatch_uid='BannerMini.file_cleanup')


class EndorsementQueryManager(models.QuerySet):
    def published(self):
        return self.all()

    def random_endorsement(self):
        return self.published().order_by('')[:4]

    def get_featured_endorsement(self):
        return random.choice(self.published())


class Endorsement(TimesStampedModel):
    image = models.ImageField(_('Image'), upload_to='campaign/endorsement/')
    name = models.CharField(_('Endorsement Name'), max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    caption = models.TextField(_('Caption'))
    url = models.CharField(_('Click URL'), max_length=255)
    description = models.TextField(_('Description'), max_length=255)
    sort_priority = models.IntegerField(_('Sort Priority'))
    valid_from = models.DateTimeField(_('Valid From'), default='')
    valid_until = models.DateTimeField(_('Valid Until'), default='')
    published = models.BooleanField(_('Published'), default=True)
    objects = EndorsementQueryManager.as_manager()

    _metadata = {
        'title': 'title',
        'description': 'description',
        'url': 'get_absolute_url',
        'image': 'get_meta_image',
        'og_type': 'article',
        'og_description': 'description',
        'gplus_type': 'article',
        'gplus_description': 'description',
        'twitter_type': 'article',
        'twitter_description': 'description',
        'twitter_creator': '@smesco',
        'twitter_site': '@smesco',
        'site_name': 'Jims Honey',
        'published_time': 'date_created',
        'modified_time': 'get_date',
        'locale': 'id',
    }

    def get_meta_image(self):
        return self.image.url

    def get_date(self, param):
        if param in ['published_time', 'modified_time']:
            return self.date_created.strftime('%Y-%m-%dT%H:%M:%S:%z')
        return self.date_created

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('endorsement:endorsement-detail', kwargs={'slug': self.slug})

    def remove_on_image_update(self):
        try:
            obj = Endorsement.objects.get(id=self.id)
        except Endorsement.DoesNotExist:
            return

        if obj.image and self.image and obj.image != self.image:
            obj.image.delete()

    def _get_unique_slug(self, slug):
        unique_slug = slug
        num = 1
        while Endorsement.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        self.remove_on_image_update()

        slug = slugify(self.name)
        if not self.slug or self.slug != slug:
            self.slug = self._get_unique_slug(slug)

        return super(Endorsement, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Endorsement')
        verbose_name_plural = _('Endorsements')
        ordering = ['-date_created', ]


post_delete.connect(file_cleanup, sender=Endorsement, dispatch_uid='Endorsement.file_cleanup')
