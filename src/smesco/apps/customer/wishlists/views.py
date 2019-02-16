from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar.apps.customer.wishlists.views import WishListListView as OriginalWishListListView
from oscar.core.loading import (get_class, get_model)

LineFormset = get_class('wishlists.formsets', 'LineFormset')
WishList = get_model('wishlists', 'WishList')


class WishListListView(OriginalWishListListView):
    context_object_name = active_tab = "wishlists"
    template_name = 'customer/wishlists/wishlists_list.html'
    paginate_by = settings.OSCAR_ADDRESSES_PER_PAGE
    page_title = _('Wish Lists')

    def get_queryset(self):
        user = self.request.user
        wishlist = WishList.objects.filter(owner=user).last()
        if wishlist and wishlist.is_allowed_to_see(user):
            return wishlist.lines.all()
        else:
            return WishList.objects.none()


