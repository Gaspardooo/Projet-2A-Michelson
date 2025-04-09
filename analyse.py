"""
Created on Fri Feb  7 22:17:24 2025

@author: gaspa
"""

#%%

import cv2
import numpy as np
from scipy.signal import savgol_filter

#%%

def get_position(event, x, y, flags, param):
    """
    Capture la position du clic gauche de la souris et l'enregistre dans param.
    
    """
    if event == cv2.EVENT_LBUTTONDOWN:  
        param["click_position"] = (x, y)  
        

#%% 

def get_position_luminosity(center,frame):
    """
   Calcule la luminosité moyenne dans un carré de 10*10 autour du centre sélectionné.
   
   """
    frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x,y=center
    pixels=frame[y-5:y+6,x-5:x+6]
    return int(np.mean(pixels))
      
#%% 

def luminosity_array(frame, center):
    """
        Extrait et lisse le profil de luminosité horizontal à partir d'une image en niveaux de gris.
        
        - Applique un filtre bilatéral pour réduire le bruit tout en préservant les contours.
        - Extrait la ligne de luminosité passant par le centre donné.
        - Utilise un filtre de Savitzky-Golay pour lisser les variations.
    """
    
    x, y = center

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Conversion en niveaux de gris

    height, width = frame.shape
    filtered_frame = cv2.bilateralFilter(frame, 15, 75, 100) # Filtrage pour réduire le bruit
    
    # Extraction du profil de luminosité le long de la ligne horizontale passant par y
    L = [filtered_frame[y, k] for k in range(width)]
    
    # Paramètres du filtre Savitzky-Golay déterminés empiriquement
    window_length = 13  
    polyorder = 3
    
    # Lissage du profil de luminosité
    L_smooth = savgol_filter(L, window_length, polyorder)
    # Conversion en entiers
    L_smooth = list(map(int, L_smooth))

    return L_smooth

#%%
def get_interval(L):
    
    l_max=max(L)
    l_min=min(L)
    
    mean_luminosity=int((l_max+l_min)/2)# Moyenne des valeurs extrêmes
         
    luminosity1 = int((mean_luminosity + l_min)/2)# Seuil inférieur
    luminosity2 = int((mean_luminosity + l_max)/2)# Seuil supérieur
    
    interval=(luminosity1,luminosity2)
        
    return interval,mean_luminosity

#%%

def luminosity_analyse(L):
    
    nb_dp = 0
    interval, l_mean = get_interval(L)  # Définition des seuils initiaux
    position = L[0] >= l_mean  # Détermine si la première valeur est au-dessus ou en dessous du seuil moyen
    
    for k in range(len(L)):
        
        if L[k] >= interval[1] and not position:  # Passage au-dessus du seuil haut
            nb_dp += 1
            position = True  
            

        if L[k] <= interval[0] and position:  # Passage en dessous du seuil bas
            nb_dp += 1
            position = False
           
    
    if nb_dp % 2 != 0:
        print(nb_dp // 2)
        print("Attention : le programme s'est arrêté sur une demi-période")
        print(f"Nombre d'extinctions : {nb_dp // 2} (+1) ")
    else:
        print(nb_dp // 2)
        print(f"Nombre d'extinctions : {nb_dp // 2}")

    return 
    
