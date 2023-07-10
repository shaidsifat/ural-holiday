from django.urls import path 
from . import views


urlpatterns = [
    path('list', views.flight_search_offers, name='flight_search_offers'),
    path('origin_airport_search/', views.airport_search, name='airport_search'), # Ajax request to search airport codes
    path('book-review/<str:flight>/', views.book_review, name="book_review"),
    path('book/<str:flight>/', views.book_travelers, name="book_travelers"),
    path('book/checkout/<int:flight_offer_id>/', views.book_checkout, name="book_checkout"),
    path('book/create-checkout-session/<int:flight_offer_id>/', views.create_checkout_session, name="flight_create_checkout"), # login required
    path('book/payment/success', views.payment_success, name="flight_payment_success"),
    path('order-manage-access/', views.get_access_for_order_manage, name="order_manage_access"),
    path('order-manage/', views.order_manage, name="order_manage"),
    # path('book/payment/failed', views.payment_failed, name="flight_payment_failed")
    path('airports/', views.airports, name="airports"),
    # path('flights', views.flights, name='flights'),
    path('flights', views.FlightSearchView.as_view(), name='flights'),
]
