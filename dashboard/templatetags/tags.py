from django import template
import time

register = template.Library()

@register.filter(name='event_month')
def event_month(value):
	return time.strftime('%b', time.localtime(float(value)))
	
@register.filter(name='event_date')
def event_date(value):
	return time.strftime('%d', time.localtime(float(value)))
