from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import (
    User,
    Company,  Tenant, Property,
    UnitType, Utilities, PropertyUnit, FixedUnitCharge,
    TenantPropertyUnit, TenantPropertyUnitsUtilities,
    Invoice, InvoiceItems, InvoicePayment, Transaction,
    Notification)


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Other Fields",
            {
                "fields": (
                    "phone_number",
                    "company"
                   
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Other Fields",
            {
                "fields": (
                    "phone_number",
                    "company"

                )
            },
        ),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(Tenant)
admin.site.register(Property)
admin.site.register(UnitType)
admin.site.register(Utilities)
admin.site.register(PropertyUnit)
admin.site.register(FixedUnitCharge)
admin.site.register(TenantPropertyUnit)
admin.site.register(TenantPropertyUnitsUtilities)
admin.site.register(Invoice)
admin.site.register(InvoiceItems)
admin.site.register(InvoicePayment)
admin.site.register(Transaction)
admin.site.register(Notification)

