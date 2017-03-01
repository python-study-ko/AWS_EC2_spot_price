from django.views.generic import View,TemplateView
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse

# Create your views here.
class Index(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self,**kwargs):
        context = kwargs
        return context

