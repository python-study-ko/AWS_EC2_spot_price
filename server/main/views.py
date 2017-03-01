from django.views.generic import View,TemplateView
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse

# Create your views here.
class Index(TemplateView):
    template_name = 'index.html'
    def get(self,request):
        data = rander_to_string("index.html",request=request)
        return HttpRespones(data)
