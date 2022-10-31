'''
Application to scrape flights from kayak.cl (CLP is currency)
As input, a destination or list of destinations are options
As input, dates to look for flights are specified through 1st flight, staying days, and tolerance of staying days
Working with Mozilla Firefox 106.0.1 and geckodriver.exe for that Firefox version
Depending on internet speed, sleep values, must be changed for each case
Code not free of bugs

santiagovalenciam@outlook.com  01/09/2022
'''

# Librerías
# from lib2to3.pgen2 import driver
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from random import randint
from datetime import date, timedelta
import pandas as pd

def abrir_navegador():
    # Options
    options =  webdriver.FirefoxOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    #Driver
    driver = webdriver.Firefox(options=options) # When geckodriver.exe is in the path.
    return driver


def iniciar_pagina(driver,origen,destino,fecha_ida,fecha_vuelta,n):
    #url
    composed_url='https://www.kayak.cl/flights/'+origen+'-'+destino+'/'+fecha_ida+'/'+fecha_vuelta+'?sort=bestflight_a'
    # Open website
    driver.get(composed_url)
    print('Scraping mejor vuelo ',origen,destino,fecha_ida,fecha_vuelta)
    sleep(randint(24,30))
    #Closing pop up if required
    try:
        xp_popup_close = '//button[contains(@id,"dialog-close") and contains(@class,"Button-No-Standard-Style close ")]'
        driver.find_elements_by_xpath(xp_popup_close)[5].click()
    except Exception as e:
        pass
    
    #Saving scraped info in s1
    s1=scrape(driver,origen,destino,fecha_ida,fecha_vuelta,'mejor',n)

    #Same but cheapest flights
    composed_url='https://www.kayak.cl/flights/'+origen+'-'+destino+'/'+fecha_ida+'/'+fecha_vuelta+'?sort=price_a'
    driver.get(composed_url)
    print('Scraping vuelo más barato ',origen,destino,fecha_ida,fecha_vuelta)
    sleep(randint(20,24))
    #Closing pop up if required
    try:
        xp_popup_close = '//button[contains(@id,"dialog-close") and contains(@class,"Button-No-Standard-Style close ")]'
        driver.find_elements_by_xpath(xp_popup_close)[5].click()
    except Exception as e:
        pass

    s2=scrape(driver,origen,destino,fecha_ida,fecha_vuelta,'mas_barato',n)

    #Merging s1 and s2 as one for each fight
    df_parcial= s1.append(s2,ignore_index=True)

    return df_parcial

    
def scrape(driver,origen,destino,fecha_ida,fecha_vuelta,seleccion,n):

    # getting the Prices
    xp_prices = '//div[@class="booking"]//span[@class="price option-text"]'
    prices = driver.find_elements_by_xpath(xp_prices)
    prices_list = [0]*n
    try:
        prices_list = [price.text.replace('$','') for price in prices if price.text != '']
        prices_list = [price.replace('.','') for price in prices_list if price != '']
        prices_list = list(map(int, prices_list))
        prices_list = prices_list[:n]
    except:
        pass

    #Flight times (2 for each option)
    tiempos_vuelo = '//div[@class="section duration allow-multi-modal-icons"]/div[@class="top"]'
    times_list = driver.find_elements_by_xpath(tiempos_vuelo)
    times_list = [time_.text for time_ in times_list]
    times_list = times_list[:2*n]
    tiempo_ida=[]
    tiempo_vuelta=[]
    for i in range(len(times_list)):
        if i%2==0:
            tiempo_ida.append(times_list[i])
        else:
            tiempo_vuelta.append(times_list[i])

    #Stops (escalas)
    escalas = '//div[@class="top"]/span[@class="stops-text"]'
    escalas_list = driver.find_elements_by_xpath(escalas)
    escalas_list = [esca.text for esca in escalas_list]
    escalas_list = escalas_list[:2*n]
    escalas_ida=[]
    escalas_vuelta=[]
    for i in range(len(escalas_list)):
        if i%2==0:
            escalas_ida.append(escalas_list[i])
        else:
            escalas_vuelta.append(escalas_list[i])

    #Departure time
    salidas = '//span[@class="time-pair"]/span[@class="depart-time base-time"]'
    salidas_list = driver.find_elements_by_xpath(salidas)
    salidas_list = [sali.text for sali in salidas_list]
    salidas_list = salidas_list[:2*n]
    salidas_ida=[]
    salidas_vuelta=[]
    for i in range(len(salidas_list)):
        if i%2==0:
            salidas_ida.append(salidas_list[i])
        else:
            salidas_vuelta.append(salidas_list[i])


    #Arrival time
    llegadas = '//span[@class="time-pair"]/span[@class="arrival-time base-time"]'
    llegadas_list = driver.find_elements_by_xpath(llegadas)
    llegadas_list = [llega.text for llega in llegadas_list]
    llegadas_list = llegadas_list[:2*n]
    llegadas_ida=[]
    llegadas_vuelta=[]
    for i in range(len(llegadas_list)):
        if i%2==0:
            llegadas_ida.append(llegadas_list[i])
        else:
            llegadas_vuelta.append(llegadas_list[i])


    #Aerolines
    aerolinea = '//div[@class="section codeshares allow-airlines"]/span[@class="codeshares-airline-names"]'
    aerolinea_list = driver.find_elements_by_xpath(aerolinea)
    aerolinea_list = [aerol.text for aerol in aerolinea_list]
    aerolinea_list = aerolinea_list[:n]

    #Dataframe to save
    df_info=pd.DataFrame(columns=['fecha_ida','fecha_vuelta','origen','destino','precio','tiempo_ida','tiempo_vuelta','escalas_ida','escalas_vuelta','aerolinea','tipo_busqueda'])
    if len(prices_list)>0:
        df_info['fecha_ida']=[fecha_ida]*n
        df_info['fecha_vuelta']=[fecha_vuelta]*n
        df_info['origen']=[origen]*n
        df_info['destino']=[destino]*n
        df_info['precio']=prices_list
        df_info['tiempo_ida']=tiempo_ida
        df_info['tiempo_vuelta']=tiempo_vuelta
        df_info['escalas_ida']=escalas_ida
        df_info['escalas_vuelta']=escalas_vuelta
        df_info['salida_ida']=salidas_ida
        df_info['llegada_ida']=llegadas_ida
        df_info['salida_vuelta']=salidas_vuelta
        df_info['llegada_vuelta']=llegadas_vuelta
        df_info['aerolinea']=aerolinea_list
        df_info['tipo_busqueda']=seleccion

    return df_info


#Creating the list of dates to scrape
def lista_fechas(fecha_inicio,fecha_fin,salto,dias_estadia,dias_tolerancia):
    fecha_inicio=date(int(fecha_inicio.split('-')[2]),int(fecha_inicio.split('-')[1]),int(fecha_inicio.split('-')[0]))
    fecha_fin=date(int(fecha_fin.split('-')[2]),int(fecha_fin.split('-')[1]),int(fecha_fin.split('-')[0]))
    dates=pd.date_range(fecha_inicio,fecha_fin,freq=str(salto)+'d')
    df_busqueda=pd.DataFrame(columns=['ida','vuelta'])
    for i in dates:
        for j in range(dias_estadia-dias_tolerancia,dias_estadia+dias_tolerancia+1):
            ff=i+timedelta(days=j)
            df_busqueda=df_busqueda.append({'ida':i.strftime('%Y-%m-%d'),'vuelta':ff.strftime('%Y-%m-%d')},ignore_index=True)
    
    return df_busqueda

def main():
    #Inputs
    origen='SCL' #From
    destino=['UIO'] #To
    fecha_inicio='01-02-2023' #Inital date to search the first flight
    fecha_fin='02-02-2023'  #Final date to search the first flight
    salto=1 #Look for trips every x days
    dias_estadia=14 #How many days between flights to complete round-trip
    dias_tolerancia=0 #Days before and after return to search (if 1, 3 days of returning flights are searched, the day, 1 before and 1 after)
    cantidad_vuelos_por_pagina=5 #How many flights are scraped for each 'best' and 'cheapest' selection

    #Getting a dates matrix to look.
    fechas=lista_fechas(fecha_inicio,fecha_fin,salto,dias_estadia,dias_tolerancia)
    driver=abrir_navegador()

    df_resultado=pd.DataFrame()

    for i in destino:
        for j in fechas.index:
            add=iniciar_pagina(driver,origen,i,fechas.loc[j,'ida'],fechas.loc[j,'vuelta'],cantidad_vuelos_por_pagina)
            df_resultado = df_resultado.append(add ,ignore_index=True)
    
    #At the end...
    print('Finalizado, guardando resultados')
    #Saving results in the same folder
    df_resultado.to_excel('resultados_scrape.xlsx',index=False)
    #Showing results
    print(df_resultado)


if __name__=='__main__':
    main()