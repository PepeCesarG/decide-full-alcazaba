import os 
import telebot  
from telebot import types 
import json 
import time 
import requests
 
from flask import Flask, request 
TOKEN = '5094239712:AAEWOtGe55YZ1GFjwNpmyrSF_kWPtO1Y2yk'
bot = telebot.TeleBot(TOKEN)  #Creamos nuestra instancia "bot" a partir de ese TOKEN 
server = Flask(__name__) 
url = 'http://localhost:8081/' 
tokenSesion = {} 
 
@bot.message_handler(commands=['start']) 
def comienzo(message): 
    bot.send_message(message.chat.id, "Bienvenido al sistema de votación Decide-Alcazaba Bot de Telegram Exclusive Edition") 
 
@bot.message_handler(commands=['help']) 
def send_welcome(message): 
    bot.send_message(message.chat.id,"Comando 1\nComando2\nComando3\nComando4\nComando5") 
 
@bot.message_handler(commands=["votaciones"]) #devuelve listado de todas las votaciones 
def resolver(message): 
    try: 
        url = 'http://localhost:8081/visualizer/all' 
        response = requests.get(url) 
        print(response.json()) 
        reply = 'Votaciones: \n' 
        for clave in response.json(): 
          reply += response.json()[clave]['name'] + ' - ' + clave 
        bot.reply_to(message, reply) 
    except Exception: 
        bot.reply_to(message, 'Error llamando a la API') 
 
@bot.message_handler(func=lambda msg: msg.text is not None and '/votacion' in msg.text) #devuelve detalle de votacion por su id 
def detalle(message): 
   try: 
      url = 'http://localhost:8081/visualizer/all' 
      response = requests.get(url) 
      texts = message.text.split(' ') 
      vid = texts[1] 
      reply = 'Nombre de la votacion: ' + response.json()[vid]['name'] + '\n' 
      if(response.json()[vid]['description'] is not None): 
        reply += 'Descripcion: ' + response.json()[vid]['description'] + '\n' 
      if(response.json()[vid]['fecha_inicio'] is not None): 
        reply += 'Fecha de inicio: ' + response.json()[vid]['fecha_inicio'] + '\n' 
      if(response.json()[vid]['fecha_fin'] is not None): 
        reply += 'Fecha de finalizacion: ' + response.json()[vid]['fecha_fin'] + '\n' 
      bot.reply_to(message, reply) 
   except Exception: 
      bot.reply_to(message, 'Error llamando a la API') 
 
@bot.message_handler(func=lambda msg: msg.text is not None and '/login' in msg.text) 
 
#/login <nombre_usuario> <contraseña> 
 
def login(message): 
   #bot.send_message(message.chat.id, "") 
   texts = message.text.split(' ') 
   if(len(texts)==3): 
      try: 
         user = texts[1].strip() #strip para quitarle los espacios iniciales y finales 
         password = texts[2].strip() 
         url = 'http://localhost:8081/authentication/login-bot/' 
         payload={"username":user,"password":password} 
         files=[] 
         headers = {} 
         respuesta = requests.request("POST", url, headers=headers, data=payload, files=files) 
         listaclaves = list(respuesta.json().keys()) 
         if 'non_field_errors' in listaclaves: 
            bot.reply_to(message, 'No puede iniciar sesión con las credenciales proporcionadas. Por favor vuelva a intentarlo.') 
         elif 'token' in listaclaves: 
            diccionario = {respuesta.json()['user_id']: True} 
            if((not respuesta.json()['user_id'] in tokenSesion.keys())or(tokenSesion[respuesta.json()['user_id']] == False)): 
               tokenSesion.update(diccionario) 
               bot.reply_to(message,'Ha iniciado sesión correctamente. Su ID para votar es:'+str(respuesta.json()['user_id'])+'. Este ID deberas de usarlo para votar !Por favor, no la comparta con nadie¡\n\nEs importante que cierre la sesion al terminar de votar') 
            else: 
               bot.reply_to(message,'Ya ha iniciado sesión anteriormente.') 
         else: 
            raise Exception() 
      except Exception: 
         bot.reply_to(message, 'Error llamando a la API') 
 
   else: 
      bot.reply_to(message, 'Por favor, use correctamente el comando /login      (ver en /help)') 
      print("Error en /login, al introducir el comando: "+str(message.text)) 
 
@bot.message_handler(func=lambda msg: msg.text is not None and '/logout' in msg.text) 
 
#/logout <id_usuario> 
 
def logout(message): 
   try: 
      texts = message.text.split(' ') 
      if(len(texts)==2): 
         id_usuario = texts[1].strip() 
         id_usuario = int(id_usuario) 
         if(id_usuario in tokenSesion.keys()): 
            if(tokenSesion[id_usuario] == False): 
               bot.send_message(message.chat.id, "No ha iniciado sesion, introduzca el comando: \"/login <usuario> <contraseña>\" para iniciar sesion") 
            else: 
               tokenSesion[id_usuario] = False 
               if(tokenSesion[id_usuario]==False): 
                  bot.send_message(message.chat.id, "Sesión cerrada!!") 
               else: 
                  raise Exception() 
         else: 
            bot.send_message(message.chat.id, "No ha iniciado sesion, introduzca el comando: \"/login <usuario> <contraseña>\" para iniciar sesion")    
      else: 
         bot.reply_to(message, 'Por favor, use correctamente el comando /logout      (ver /help)') 
         print("Error en /logout, al introducir el comando: "+str(message.text)) 
   except Exception: 
      bot.reply_to(message, 'Error llamando a la API') 
 
def getVotacion(id_votacion): 
   url = 'http://localhost:8081/voting/?id=' 
   url+=str(id_votacion) 
   payload={} 
   files={} 
   headers = {} 
   response = requests.request("GET", url, headers=headers, data=payload, files=files) 
   return response.json() 
 
@bot.message_handler(func=lambda msg: msg.text is not None and '/options' in msg.text) 
#/options <id_votacion> 
def opciones(message): 
   try: 
      texts = message.text.split(' ') 
      if(len(texts)==2): 
 
         texto = 'Las opciones a votar en está votacion son:\n' 
          
         id_voting = texts[1].strip() 
         diccionario = getVotacion(id_votacion=id_voting) 
          
         cont = 1 
         for elemento in diccionario[0]['question']['options']: 
            texto += '  Opción '+str(cont)+' : '+str(elemento['option']+'\n') 
            cont += 1 
          
         texto += 'Para votar introduzca /vote <su_id_de_usuario> '+str(id_voting)+' <numero de la opcion a elegir>' 
         bot.send_message(message.chat.id, texto) 
      else: 
         bot.reply_to(message, 'Por favor, use correctamente el comando /options     (ver /help)') 
 
   except: 
      bot.reply_to(message, 'Error llamando a la API') 
 
@bot.message_handler(func=lambda msg: msg.text is not None and '/vote' in msg.text) 
#/vote <id_usuario> <id_votacion> <id_opcion> 
def votacion(message): 
   try: 
      texts = message.text.split(' ') 
      if(len(texts) == 4): 
         id_usuario = int(texts[1].strip()) 
         if(id_usuario in tokenSesion.keys()): 
            if(tokenSesion[id_usuario] == True): 
               id_votacion = int(texts[2].strip()) 
               id_opcion = int(texts[3].strip()) 
 
               diccionarioVotacion = getVotacion(id_votacion) 
               diccionario_asignacion = {} 
               cont = 1 
                
               for elemento in diccionarioVotacion[0]['question']['options']: 
                  diccionario_asignacion.setdefault(cont, elemento) 
                  cont += 1 
               #{1 : 2, 2 : 3} 
                
               if(not id_opcion in diccionario_asignacion.keys()): 
                  bot.send_message(message.chat.id, 'La opción que ha elegido no existe') 
                  print('La opción que ha elegido no existe') 
               else: 
                  for opcion in diccionario_asignacion: 
                     
                     if(opcion == id_opcion): 
 
                        question_opt = diccionario_asignacion[opcion] 
                        question_opt_body = str(question_opt).replace('\'', '\"') 
                         
                        url = "http://localhost:8081/voting/encrypt/" 
                        payload={"question_opt": str(question_opt),"id_v": str(id_votacion)} 
                        files=[] 
                        headers = {} 
                        respuesta = requests.request("POST", url, headers=headers, data=payload, files=files) 
                        listaclaves = list(respuesta.json().values()) 

                        url2 = 'http://localhost:8081/store/store-bot/' 
                        payload2={"voting_id":id_votacion,"voter_id":id_usuario, "a":str(listaclaves[0]), "b":str(listaclaves[1])} 
                        files2=[] 
                        headers2 = {} 
                        respuesta2 = requests.request("POST", url2, headers=headers2, data=payload2, files=files2) 
                        
                        if(respuesta2.status_code == 201): 
                           bot.send_message(message.chat.id, 'Has votado correctamente. Por favor, cierre sesión al salir de la aplicación') 
                        elif(respuesta2.status_code == 401): 
                           bot.send_message(message.chat.id, 'No está autorizado para votar en esta votación') 
                        elif(respuesta2.status_code == 200):
                           bot.send_message(message.chat.id, 'Has votado correctamente. Por favor, cierre sesión al salir de la aplicación')
                        else: 
                           bot.send_message(message.chat.id, 'Algo ha salido mal') 

            else: 
               bot.send_message(message.chat.id, "No ha iniciado sesion, introduzca el comando: \"/login <usuario> <contraseña>\" para iniciar sesion") 
         else: 
            bot.send_message(message.chat.id, "No ha iniciado sesion, introduzca el comando: \"/login <usuario> <contraseña>\" para iniciar sesion") 
      else: 
         bot.reply_to(message, 'Por favor, use correctamente el comando /vote      (ver /help)') 
         print("Error en /vote, al introducir el comando: "+str(message.text)) 
   except Exception: 
      bot.reply_to(message, 'Error llamando a la API') 
 
 
@bot.message_handler(func=lambda msg: msg.text is not None and not '/' in msg.text) 
def no_command_message(message): 
   bot.send_message(message.chat.id, 'Por favor introduzca algun comando del listado siguiente:') 
   send_welcome(message) 
 
''' 
# SERVER SIDE  
@server.route('/' + TOKEN, methods=['POST']) 
def getMessage(): 
   bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]) 
   return "!", 200 
@server.route("/") 
def webhook(): 
   bot.remove_webhook() 
   bot.set_webhook(url='https://telebot-decide-alcazaba.herokuapp.com/' + TOKEN) 
   return "!", 200 
if __name__ == "__main__": 
   server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000))) 
'''
'''
#https://api.telegram.org/bot5094239712:AAEWOtGe55YZ1GFjwNpmyrSF_kWPtO1Y2yk/setWebhook?url= 
'''

bot.polling()