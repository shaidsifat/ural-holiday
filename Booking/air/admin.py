from django.contrib import admin
from .models import FlightOffer, OrderDetail, Traveler, User
# Register your models here.


class FlightOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'price', 'currency', 'created_on')
    search_fields = ('id', 'user__username')

    @admin.display(ordering='user__username', description='Username')
    def get_user(self, obj):
        return obj.user.username

class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'get_flight_offer', 'amount', 'stripe_payment_intent', 'has_paid', 'created_on', 'updated_on')
    search_fields = ('id', 'user__username')

    @admin.display(ordering='flight_offer__user__username', description='Username')
    def get_user(self, obj):
        return obj.flight_offer.user.username if obj.flight_offer.user else 'Guest'

    @admin.display(ordering="flight_offer__created_on", description="Flight Offer")
    def get_flight_offer(self, obj):
        return obj.flight_offer.name

class TravelerAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'flight_offer', 'date_of_birth', 'first_name', 'last_name', 'middle_name', 'gender', 'email_address', 'phone', 'created_on', 'updated_on')
    search_fields = ('id', 'type', 'flight_offer__id', 'date_of_birth', 'first_name', 'last_name', 'middle_name', 'email_address', 'phone', 'created_on', 'updated_on')

admin.site.register(FlightOffer, FlightOfferAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(Traveler, TravelerAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('id', 'email')

admin.site.register(User, UserAdmin)