from django.contrib import admin

from .models import Listing, Bid, Comment

# username: admin: Admin@2020

# Register your models here.
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    pass
    #     list_display = ()


admin.site.register(Bid)
admin.site.register(Comment)


