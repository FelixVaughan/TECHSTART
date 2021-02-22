from django.shortcuts import render

# Create your views here.
def index(request):
    """Renders the homepage"""
    return render(request, "index.html")
