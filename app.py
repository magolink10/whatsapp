import os
import json
from heyoo import WhatsApp
from os import environ
from flask import Flask, request
import requests
from base64 import b64decode



#print (d[0]['estado'])
#print (d[0]['loc'])
#print (d[0]['imagen'])

messenger = WhatsApp(environ.get("TOKEN"), phone_number_id=environ.get("PHONE_NUMBER_ID"))
#WhatsApp(token = "inpust accesstoken", phone_number_id="input phone number id") #messages are not recieved without this pattern


VERIFY_TOKEN = environ.get("APP_SECRET") #application secret here

#to be tested in prod environment
# messenger = WhatsApp(os.getenv("heroku whatsapp token"),phone_number_id='105582068896304')
# VERIFY_TOKEN = "heroku whatsapp token"

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, It Works"



@app.route("/whatsapi", methods=["GET", "POST"])
def hook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"


    data = request.get_json()
    changed_field = messenger.changed_field(data)
    if changed_field == "messages":
        new_message = messenger.get_mobile(data)
        if new_message:
            mobile = messenger.get_mobile(data)
            message_type = messenger.get_message_type(data)

            if message_type == "text":
                message = messenger.get_message(data)
                name = messenger.get_name(data)
                if(message=='iniciar' or message=='Iniciar'):
                    print(f"{name} with this {mobile} number sent  {message}")
                    messenger.send_message(f"Ingrese su número de cédula:", mobile)
                else:
                    #messenger.send_message(f"Hola, {name}", mobile)
                    url="http://186.46.168.227:8082/consulta/"+message
                    
                    #print(url)
                    response = requests.post(url)
                    d=response.json()
                    #print (d)
                    #print(f"{name} with this {mobile} number sent  {message}")
                    
             
                    messenger.send_message(d[0]['estado'], mobile)
                    if(d[0]['estado']=='Encontrado'):
                        
                        try:
                            messenger.send_image(image="http://186.46.168.227:8082/imagenes/"+message+".jpg",recipient_id=mobile)
                            messenger.send_location(lat=float(d[0]['loc'].split(',')[0]),long=float(d[0]['loc'].split(',')[1]),name="",address="",recipient_id=mobile)

                        except Exception as e:
                            print (e)
                                                 
                    else:
                        messenger.send_message(d[0]['estado'], mobile)
                                               
                                       

            elif message_type == "interactive":
                message_response = messenger.get_interactive_response(data)
                print(message_response)

            else:
                pass
        else:
            delivery = messenger.get_delivery(data)
            if delivery:
                print(f"Message : {delivery}")
            else:
                print("No new message")
    return "ok"




if __name__ == '__main__': 
    app.run(debug=True)
