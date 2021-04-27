from django.shortcuts import render
from django.contrib.sessions.models import Session
from django.http import *
from tempfile import NamedTemporaryFile
from integrations.models import *
import errno
import os
#extracts the code from a url
def obtain_url_code(url):
    print(f"code request {url}")
    try:
        index = url.index("code=") #throws ValueError if index not found
        amp_separator = url.find("&", index) #sometimes codes re delimited by '&'
        code = ""
        if (amp_separator != -1):
            code = url[index+5:amp_separator]
        else:
            code = url[index+5:len(url)-3]
        return code
    except Exception as e:
        print(f"could not find code in string {str(url)}")
        return -1

def send_request(request):
    discord = DiscordApi(request.user.id)
    request.session['api'] = 'discord'
    discord.init_contact()
    return "<h1>poop</h1>"

def redirect(request):
    try: 
        url = str(request.build_absolute_uri)
        code = obtain_url_code(url)
        if(code is -1):
            msg = "Code not set as it was not found in redirect. Url probably malformed..."
            print(msg)
            return(msg)
        if os.path.exists("code.txt"):
            os.remove("code.txt")
        if request.session['api'] == 'discord':
            print("CODE IS: "+code)
        f = open("code.txt","w")
        f.write(code)
        f.close()
    except Exception as e:
        print(e)
    finally:
        return render(request, 'users/redirect.html')

def index(request):
    userinfo = {'current_user': 'bingo',
                'top_tracks': 'Some Music',
                'top_artists': 'Celine Dion'}
    return render(request, 'integrations/index.html', {'userinfo':userinfo})
