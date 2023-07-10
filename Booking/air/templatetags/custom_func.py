from django import template
import base64

register = template.Library()

from django import template

register = template.Library()

@register.filter()
def range_filter(min, max):
    return range(min, max)

@register.filter()
def base64_encode(data):
    encodedBytes = base64.urlsafe_b64encode(str(data).encode("utf-8"))
    return str(encodedBytes, "utf-8")

@register.filter()
def base64_decode(data):
    decodedBytes = base64.urlsafe_b64decode(data)
    return str(decodedBytes, "utf-8")