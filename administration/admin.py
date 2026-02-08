from django.contrib import admin
from .models import Room, RoomBooking

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'room_type', 'capacity', 'has_projector', 'has_smartboard')
    list_filter = ('room_type', 'has_projector', 'has_smartboard')
    search_fields = ('number', 'description')

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'teacher', 'date', 'start_time', 'end_time', 'purpose')
    list_filter = ('date', 'room')
    search_fields = ('teacher__username', 'purpose', 'room__number')
    date_hierarchy = 'date'
