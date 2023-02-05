from django.shortcuts import render
from django.views import View
from linkedin_api import Linkedin
from reportlab.pdfgen import canvas  
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from bs4 import BeautifulSoup
from ektaapp.models import *
# Create your views here.
# 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
context = {}
class DownloadPDF(APIView):
    def get(self, request):
        response = HttpResponse(content_type='application/pdf')  
        response['Content-Disposition'] = f"""attachment; filename="EKTA.pdf"""  
        p = canvas.Canvas(response)  
        p.setFont("Times-Roman", 16)  
        p.drawString(10,800, "Ekta Solve more crimes.")
        if 'firstName' in context["profile"]:
            p.drawString(10,750, f"Full Name: {context['profile']['firstName']} {context['profile']['lastName']}")
            p.drawString(10,700, f"Industry Name: {context['profile']['industryName']}")
            if 'email_address' in context['contact_info']:
                p.drawString(10,650, f"Email: {context['contact_info']['email_address']}")
            else:
                p.drawString(10,650, f"Email: NOT Found")
                
            if len(context['contact_info']['phone_numbers']) != 0:
                p.drawString(10,600, f"Phone Number: {context['contact_info']['phone_numbers'][0]['number']}")
            else:
                p.drawString(10,600, f"Phone Number: NOT Found")
                
            if 'birthDate' in context['profile']:
                p.drawString(10,550, f"Birthday: {context['profile']['birthDate']['month']} month, {context['profile']['birthDate']['day']} day.")
            if len(context['profile']['experience']) != 0:
                p.drawString(10,500, f"Experience: {context['profile']['experience'][0]['companyName']}, {context['profile']['experience'][0]['locationName']}")
            if len(context['profile']['education']) != 0:
                p.drawString(10,450, f"Education: {context['profile']['education'][0]['school']['schoolName']}")
            p.drawString(10,400, f"LinkedIN URL: https://www.linkedin.com/in/{context['username']}/")
        else:
            p.drawString(10,750, f"Full Name: Not Found")
            p.drawString(10,700, f"Industry Name: Not Found")
            p.drawString(10,650, f"Email: Not Found")
            p.drawString(10,600, f"Phone Number: Not Found")
            p.drawString(10,550, f"Birthday: Not Found")
            p.drawString(10,500, f"Experience: Not Found")
            p.drawString(10,450, f"Education: Not Found")
            p.drawString(10,400, f"LinkedIN URL: Not Found")
        if "instalink" in context:
            p.drawString(10,350, f"Instagram URL: {context['instalink']}")
            p.drawString(10,300, f"Instagram Details: {context['insta_details']}")
        p.save()
        return response
    
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    def post(self, request):
        return HttpResponseRedirect("/home/")

class ImageSearchView(View):
    def get(self, request):
        return render(request, "image_search.html")
    

class HomeView(View):
    def get(self, request):
        recent_searchdata = RecentSearch.objects.all()[0:3].values_list('user_id', flat=True)
        result = []
        for i in range(len(recent_searchdata)):
            result.append({"id": i+1, "user_id": recent_searchdata[i]})
        context = {
            "userdata": result
        }
        return render(request, "index.html", context)
    
    # def post(self, request):
    #     global username
    #     if "linkedin" in request.POST:
    #         username = request.POST["linkedin"]
    #     return render(request, "index.html", context)

def instaGramData(username):
    BASE_URL = f"https://www.instagram.com/{username}/"
    x = requests.get(BASE_URL)
    if x.status_code == 200:
        soup = BeautifulSoup(x.text, 'html.parser')
        profile = [i.get("content") for i in soup.find_all("meta") if i.get("content") and "http" in i.get("content")]
        insta_profile = profile[0]
        insta_id = profile[1]
        insta_details = [i.get("content") for i in soup.find_all("meta")][-3].replace("See Instagram photos and videos from", "")
        return insta_profile, insta_id, insta_details
    return "", "", ""
    
    
class LinkedInDATAAPI(APIView):
    def post(self, request):
        global context
        image, link, profile, contact_info, insta_details = "", "", {}, {}, ""
        api = Linkedin('yashgarg11131@gmail.com', 'Opentheaccount@123')
        data = request.data
        try:
            RecentSearch(user_id=data["linkedin"]).save()
            image, link, insta_details = instaGramData(data["linkedin"])
        except:
            pass
        try:
            profile = api.get_profile(data["linkedin"])
            contact_info = api.get_profile_contact_info(data["linkedin"])
        except:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Result not found."}, status=status.HTTP_404_NOT_FOUND)
        context = {"image": image, "insta_details": insta_details, "instalink": link, "username": data["linkedin"], "status": status.HTTP_200_OK, "message": "Data found successfully.", "profile": profile, "contact_info": contact_info}
        return Response({"status": status.HTTP_200_OK, "insta_details": insta_details, "image": image, "instalink": link, "username": data["linkedin"], "message": "Data found successfully.", "profile": profile, "contact_info": contact_info, "dbData": RecentSearch.objects.all()[0:3].values()}, status=status.HTTP_200_OK)