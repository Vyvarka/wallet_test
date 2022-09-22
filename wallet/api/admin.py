from django.contrib import admin

from .models import *


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'type', 'currency', 'user', 'created_on')
    list_display_links = ('pk','name')
    search_fields = ('pk', 'name', 'type', 'currency', 'user')
    list_editable = ('type', 'currency')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'sender', 'receiver', 'status', 'timestamp')
    list_display_links = ('pk', 'sender', 'receiver')
    search_fields = ('pk', 'sender', 'receiver', 'status')
