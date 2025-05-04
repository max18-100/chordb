import os
from dotenv import load_dotenv
import time
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from PIL import Image
load_dotenv()
# Konfiguration für MariaDB
db_config = {
    'user': 're_chor',
    #'password': 'Basilika13!',
    'password': os.getenv("dbpw"),
    'host': '192.168.178.43',
    'port': 3307,
    'database': 're_chor',
}

# PDF und Layout-Konfiguration
output_pdf = "personen.pdf"
seitenbreite, seitenhoehe = A4
bilder_pro_zeile = 8
bild_breite = 2 * cm
bild_hoehe = bild_breite *4/3 
rand_links = 1 * cm
rand_rechts = 1 * cm
rand_oben = 1 * cm
oben =seitenhoehe - rand_oben
links = seitenbreite - rand_links
rand_unten = 1.5 * cm
breite = seitenbreite - rand_links - rand_rechts
abstand_x = (breite -8*bild_breite)/7
leading =1.2
schriftgroesse = 6 
stimmschriftgroesse = 12
ueberschriftgroesse = 15
name_hoehe = 4 * schriftgroesse
stimm_hoehe = stimmschriftgroesse * leading
abstand_reihe = bild_hoehe + name_hoehe 

#y = seitenhoehe - rand_oben 

heute = time.strftime("%d %m %Y")

def lade_daten():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT name,vorname,bildname,v_chor_a.Stimme as Stimme FROM v_chor_a INNER JOIN t_register ON v_chor_a.Stimme = t_register.StimmLage WHERE v_chor_a.Bildname Is Not Null order by t_register.sort_bild,name,vorname;")
    daten = cursor.fetchall()
    conn.close()
    return daten

def print_header(c,stimme,x,y):
    c.setFont("Helvetica", stimmschriftgroesse)
    c.drawString(x,y ,stimme) 

def print_bild(c,name,vorname,bildpfad,x,y1,text=True):
    if text:
        c.setFont("Helvetica", schriftgroesse)
        y1 = y + schriftgroesse * leading 
        text=c.beginText(x , y1)
        text.setFont("Helvetica",schriftgroesse)
        text.setLeading(schriftgroesse * leading)
        text.textLine(vorname)
        text.textLine(name)
        c.drawText(text)

    try:
        y1 += schriftgroesse * leading 
        img = Image.open(bildpfad)
        img.thumbnail((bild_breite, bild_hoehe))
        c.drawImage(ImageReader(img), x, y1 , width=bild_breite, height=bild_hoehe)
    except Exception as e:
        print(f"Fehler beim Laden des Bildes: {bildpfad} – {e}")
        return() 
        # Name als Bildunterschrift


def erstelle_pdf(daten):
    global y
    c = canvas.Canvas(output_pdf, pagesize=A4)

    x = rand_links
    y = oben
    bilder_in_zeile = 0
    save_stimme= "" 
    c.setFont("Helvetica", ueberschriftgroesse)
    c.drawString(rand_links ,seitenhoehe - rand_oben - ueberschriftgroesse,"Basilikachor St. Ulrich und Afra")
    for name,vorname,pfad,stimme in daten:
        # Bild skalieren mit PIL
        bildpfad= '/mnt/i/chor/sw/' + pfad 
        if stimme != save_stimme:
            save_stimme =stimme 
            new= True
        else:
           new = False 
        #print(bildpfad)
        if stimme == 'Chorleiter':
           y -= bild_hoehe
           x= 50
           c.setFont("Helvetica", stimmschriftgroesse)
           cl=f"Chorleiter {name} {vorname}"
           c.setFont("Helvetica", 8)
           c.drawRightString(seitenbreite-rand_rechts, seitenhoehe -rand_oben -10, heute) 
           c.drawString(rand_links +2 *cm ,y+bild_hoehe/2 ,cl)            
           x=seitenbreite/2 - bild_breite/2
           print_bild(c,name,vorname,bildpfad,x,y,False)
           continue
            
        if bilder_in_zeile == bilder_pro_zeile or new:
            bilder_in_zeile = 0
            x = rand_links
            if  new:
                y -= stimm_hoehe
                #y = seitenhoehe - rand_oben - stimm_hoehe
                if y < rand_unten + abstand_reihe:
                    c.showPage()
                    y = seitenhoehe - rand_oben - stimm_hoehe
                print_header(c,stimme,rand_links,y)
            y -= abstand_reihe
            
            if y < rand_unten:
                c.showPage()
                y = seitenhoehe - rand_oben +abstand_reihe

        print_bild(c,name,vorname,bildpfad,x,y)
        bilder_in_zeile += 1
        x += abstand_x + bild_breite

    c.save()

daten = lade_daten()
erstelle_pdf(daten)
print("PDF wurde erfolgreich erstellt.")

