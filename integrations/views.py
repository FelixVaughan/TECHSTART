from django.shortcuts import render
from django.http import *
from integrations.models import user_code_queue


#extracts the code from a url
def obtain_url_code(url):
    index = url.index("code=") #throws ValueError if index not found
    code = url[index+5:len(url)-3]
    print(code)
    return code
    
def redirect(request):
    url = str(request.build_absolute_uri)
    code = obtain_url_code(url)
    print("\n"*4) 
    # write_code_to_file = open("transfer.txt","w")
    # write_code_to_file.write(code)
    # write_code_to_file.close()

    return HttpResponse("<h1>Code obtained! This is the redirect page<h1>")