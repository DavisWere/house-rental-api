from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import NotificationCreateView

from core.views import CustomObtainTokenPairView, CompanyViewSet, TenantViewSet, PropertyViewSet, \
    UnitTypeViewSet, UtilitiesViewSet, PropertyUnitViewSet, FixedUnitChargeViewSet, TenantPropertyUnitViewSet, \
    TenantPropertyUnitsUtilitiesViewSet, InvoiceViewSet, InvoiceItemsViewSet, InvoicePaymentViewSet, \
    InvoiceTransactionViewSet, PaymentCallBackHandler, TransactionViewSet 

core_router = DefaultRouter()
core_router.register(r"company", CompanyViewSet)
core_router.register(r"tenants", TenantViewSet)
core_router.register(r"property", PropertyViewSet)
core_router.register(r"unit-type", UnitTypeViewSet)
core_router.register(r"utilities", UtilitiesViewSet)
core_router.register(r"property-unit", PropertyUnitViewSet)
core_router.register(r"fixed-unit-charge", FixedUnitChargeViewSet)
core_router.register(r"tenant-property-unit", TenantPropertyUnitViewSet)
core_router.register(r"tenant-property-unit-utilities", TenantPropertyUnitsUtilitiesViewSet)
core_router.register(r"invoice", InvoiceViewSet)
core_router.register(r"invoice-items", InvoiceItemsViewSet)
core_router.register(r"invoice-payment", InvoicePaymentViewSet)
core_router.register(r"transaction", TransactionViewSet)
#core_router.register(r"notification", NotificationViewSet)


#core_router.register(r"invoice-transaction", InvoiceTransactionViewSet)

url_patterns = core_router.urls
url_patterns += [
    path("token/request/", CustomObtainTokenPairView.as_view(), name="token_request"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('create-notification/', NotificationCreateView.as_view(), name='create-notification'),
    path("payment-callback-handler/", PaymentCallBackHandler.as_view(), name='payment-callback-handler')

]
