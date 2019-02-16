from django.contrib import admin
from .models import Banner, BannerMini, Endorsement


class BannerAdmin(admin.ModelAdmin):
    pass


class BannerMiniAdmin(admin.ModelAdmin):
    pass


class EndorsementAdmin(admin.ModelAdmin):
    pass


admin.site.register(Banner, BannerAdmin)
admin.site.register(BannerMini, BannerMiniAdmin)
admin.site.register(Endorsement, EndorsementAdmin)
