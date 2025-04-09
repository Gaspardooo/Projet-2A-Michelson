"""
Created on Fri Feb  7 22:14:01 2025

@author: gaspa
"""

import cv2
from datetime import datetime
import analyse as an

#%% 
def nothing(x):
    """
    Fonction vide utilisée pour les trackbars.
    """
    pass

#%% 

def video_from_camera(index=0, codec='MJPG'):
    """
    Capture un flux vidéo depuis la caméra et permet :
    - d'ajuster contraste, luminosité et gain avec des trackbars,
    - de basculer en mode noir et blanc avec 'g',
    - de démarrer/arrêter l'enregistrement de la vidéo avec la touche 'r',
    - de quitter avec 'Échap'.
    """
    
    # Ouvre la caméra avec l'index spécifié
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra.")
        return
    
    # Crée une fenêtre pour afficher la vidéo
    cv2.namedWindow("Video")
    
    # Récupération des paramètres initiaux de la caméra
    init_contrast = int(cap.get(cv2.CAP_PROP_CONTRAST))
    init_brightness = int(cap.get(cv2.CAP_PROP_BRIGHTNESS))
    init_gain = int(cap.get(cv2.CAP_PROP_GAIN))
    
    # Création des trackbars pour ajuster les paramètres d'image en temps réel
    cv2.createTrackbar('Contrast', 'Video', init_contrast, 300, nothing)
    cv2.createTrackbar('Brightness', 'Video', init_brightness, 300, nothing)
    cv2.createTrackbar('Gain', 'Video', init_gain, 300, nothing)
    
    grayscale = False  # Indicateur du mode noir et blanc
    recording = False  # Indicateur d'enregistrement vidéo
    video_writer=None
    
    
    while cap.isOpened():
        # Capture une image depuis la caméra
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire une image depuis la caméra.")
            break
        
        # Lecture des valeurs des trackbars
        contrast = cv2.getTrackbarPos('Contrast', 'Video')
        brightness = cv2.getTrackbarPos('Brightness', 'Video')
        gain = cv2.getTrackbarPos('Gain', 'Video')
        
        # Application des nouveaux paramètres à la caméra
        cap.set(cv2.CAP_PROP_CONTRAST, contrast)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        cap.set(cv2.CAP_PROP_GAIN, gain)
        
        # Gestion des entrées clavier
        key = cv2.waitKey(1) & 0xFF
        
        # Activation/désactivation du mode noir et blanc
        if key == ord('g'):
            grayscale = not grayscale
            
        
        # Gestion de l'enregistrement vidéo
        if key == ord('r'):
            recording = not recording  # Basculer l'état de l'enregistrement
            
            if recording:
                # Configuration du codec et des paramètres de sortie
                fourcc = cv2.VideoWriter_fourcc(*codec)
                fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
                frame_size = (frame.shape[1], frame.shape[0])
                output_filename = '{}.avi'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
                video_writer = cv2.VideoWriter(output_filename, fourcc, fps, frame_size)
                
            else:
                video_writer.release()
                
        if grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Conversion en niveaux de gris
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Conversion en 3 canaux pour compatibilité
            
        # Écriture de l'image dans le fichier si l'enregistrement est actif
        if recording:
            video_writer.write(frame)
            # Ajout d'un indicateur visuel lorsque l'enregistrement est actif
            cv2.circle(frame, (10, 10), 10, (0, 0, 255), -1)  # Ajout d'un point rouge
            cv2.putText(frame, 'REC', (30, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        
        # Affichage de l'image dans la fenêtre
        cv2.imshow("Video", frame)
        
        # Quitter si la touche Échap est appuyée
        if key == 27:
            break
    
    # Restauration des paramètres initiaux de la caméra
    cap.set(cv2.CAP_PROP_CONTRAST, init_contrast)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, init_brightness)
    cap.set(cv2.CAP_PROP_GAIN, init_gain)
    
    # Libération des ressources et fermeture des fenêtres
    if video_writer:
        video_writer.release()
        
    cap.release()
    cv2.destroyAllWindows() 
    
    return

#%%

def play_file(file_name):
    """
    Lit un fichier vidéo et permet :
    - de mettre en pause avec la touche ESPACE,
    - de basculer en mode noir et blanc avec la touche 'g',
    - d'accélérer la lecture avec la touche '+',
    - de ralentir la lecture avec la touche '-',
    - de quitter avec la touche ÉCHAP.
    """
    
    # Ouvre le fichier vidéo
    cap = cv2.VideoCapture(file_name)
    
    # Récupère le nombre d'images par seconde (FPS) de la vidéo
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calcul du délai entre chaque image en millisecondes 
    delay = int(1000 / fps) if fps > 0 else 20  # Valeur par défaut de 20 ms si FPS inconnu
    
    grayscale = False  # Indicateur du mode noir et blanc
    pause = False  # Indicateur de pause
    
    while cap.isOpened():
        
        if not pause:  # Lire une nouvelle image seulement si la vidéo n'est pas en pause
            ret, frame = cap.read()  # Capture une image
            
            if not ret:
                print("Fin de la vidéo")
                break  # Quitte la boucle si la vidéo est terminée ou si une erreur survient
            
            if grayscale:  # Applique un filtre noir et blanc si activé
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
            cv2.imshow("Video", frame)  # Affiche l'image
        
        # Gestion des entrées clavier avec délai ajustable
        key = cv2.waitKey(delay if not pause else 1) & 0xFF
        
        # Ralentit la lecture en augmentant le délai entre les images
        if key == ord('-'):
            delay += 5
        
        # Accélère la lecture en réduisant le délai (minimum 5 ms)
        if key == ord('+'):
            if delay - 5 > 0:
                delay -= 5
        
        # Quitter la lecture si la touche ÉCHAP est appuyée
        if key == 27:
            break
        
        # Met en pause ou reprend la lecture si ESPACE est appuyé
        if key == ord(' '):
            pause = not pause
        
        # Active/désactive le mode noir et blanc
        if key == ord('g'):
            grayscale = not grayscale
    
    # Libération des ressources et fermeture des fenêtres 
    cap.release()
    cv2.destroyAllWindows()
    return


#%%
def fringe_counter_from_camera(index=0):
    """
    Capture un flux vidéo depuis la caméra et compte le nombre de frange 
    ayant défilées au niveau d'un point sélectionné par l'utilisateur et permet:
    - de lancer/arrêter le comptage des franges avec la touche 'c',
    - de quitter la fonction avec la touche ÉCHAP.
    
    """
    
    # Ouvre la caméra avec l'index spécifié
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) 
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra.")
        return
    
    # Initialisation des paramètres
    counting = False  # Indique si le comptage est en cours
    center = None  # Coordonnées du point sélectionné
    click_data = {"click_position": None}  # Stocke la position du clic
    L = []  # Liste des valeurs de luminosité
    res=None

    
    cv2.namedWindow("Video")  # Crée une fenêtre pour l'affichage
    cv2.setMouseCallback("Video", an.get_position, click_data)  # Associe une fonction de récupération des clics à la souris
    
    while cap.isOpened():
        # Capture une image depuis la caméra
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire une image depuis la caméra.")
            break
        
        
        cv2.imshow('Video', frame)  # Affiche l'image capturée
        
        # Si le comptage est activé et que le centre est défini, on enregistre la luminosité
        if counting and center:
            luminosity = an.get_position_luminosity(center, frame)
            L.append(luminosity)
        
        # Si le comptage est activé mais que le centre n'est pas encore défini
        if counting and not center:
            click_data["click_position"] = None
            
            #recupération du centre 
            while not center:
                ret, frame = cap.read()
                if not ret:
                    print("Erreur : Impossible de lire une image depuis la caméra.")
                    break
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                og_frame = frame.copy()  # Sauvegarde de l'image originale
                #créer et affiche une image donnant les instructions à l'utilisateur
                cv2.putText(frame, 'Cliquez au centre des anneaux', (30, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow('Video', frame)
                
                if click_data["click_position"] is not None:
                    center = click_data["click_position"]
                    
                    # Demande confirmation de la position du centre
                    satisfaction_frame = og_frame.copy()
                    cv2.circle(satisfaction_frame, (center[0], center[1]), 10, (0, 0, 255), -1) #trace un point au niveau du centre séléctionné
                    cv2.putText(satisfaction_frame, 'Voulez vous garder cette coordonnee ? [y/n]', (30, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.imshow('Video', satisfaction_frame)
                    cv2.waitKey(1)
                    
                    while True:
                        key = cv2.waitKey(0) & 0xFF
                        if key == ord('y'):  # Validation de la sélection
                            break
                        if key == ord('n'):  # Réinitialisation de la sélection
                            center = None
                            click_data["click_position"] = None
                            break
                        if key == 27:  # Quitter si la touche ÉCHAP est pressée
                            cap.release()
                            cv2.destroyAllWindows()
                            return
            
            # Enregistre la première valeur de luminosité
            luminosity = an.get_position_luminosity(center, og_frame)
            L.append(luminosity)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Activation/désactivation du comptage des franges
        if key == ord('c'):
            counting = not counting
            if not counting:
                res=an.luminosity_analyse(L)  # Analyse des valeurs enregistrées
                center = None  # Réinitialisation des paramètres
                click_data["click_position"] = None
                L = []
        
        # Quitter si la touche ÉCHAP est pressée
        if key == 27:
            break
        
    
    # Libération des ressources et fermeture des fenêtres
    cap.release()
    cv2.destroyAllWindows()
    
    # Analyse si des données étaient en train d'êtres enregistrées
    if L!=[]:
        res=an.luminosity_analyse(L)
    
    return res

#%%
def fringe_counter_from_file(file_name):
    
    """
    Capture un flux vidéo depuis un fichier vidéo et compte le nombre de frange 
    ayant défilées au niveau d'un point sélectionné par l'utilisateur.
    Même fonctionnement que fringe_counter_from_camera
    
    """
    
    cap = cv2.VideoCapture(file_name)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000/fps) if fps > 0 else 20  
       
    counting=False
    center=None
    click_data = {"click_position": None} 
    L=[]
    

    cv2.namedWindow("Video")
    cv2.setMouseCallback("Video",an.get_position,click_data)
    
    while cap.isOpened():
        
        ret, frame = cap.read()
        if not ret:
            print("Fin de la vidéo.")
            break  
        
        cv2.imshow('Video',frame)
        
        if counting and center:
            
            luminosity = an.get_position_luminosity(center, frame)
            
            L.append(luminosity)
            
            
            
        if counting and not center:
            
            click_data["click_position"] = None
            og_frame=frame.copy()
            cv2.putText(frame, 'cliquer au centre des anneaux', (30,30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            
            while not center:
                               
                
                cv2.imshow('Video',frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                if click_data["click_position"] is not None:
                    
                    center=click_data["click_position"]
                    cv2.imshow("Video", og_frame)  
                    cv2.waitKey(1)  

                    satisfaction_frame = og_frame.copy()
                    cv2.circle(satisfaction_frame, (center[0], center[1]), 10, (0, 0, 255), -1)
                    cv2.putText(satisfaction_frame, 'Voulez-vous garder cette coordonnee ? [y/n]',(30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA) 
                                                                                                    
                    cv2.imshow('Video', satisfaction_frame)
                    cv2.waitKey(1)  
                    
                    while(True):
                        
                        key = cv2.waitKey(0) & 0xFF

                        if key == ord('y'):  
                            break
                        
                        if key == ord('n'):  
                            center = None
                            click_data["click_position"] = None
                            break
                        
                        if key == 27:
                            cap.release()
                            cv2.destroyAllWindows()
                            return
                        
            x,y = center
            
            luminosity = an.get_position_luminosity(center, og_frame)
            
            L.append(luminosity)
            
        
        key = cv2.waitKey(delay) & 0xFF
        
        if key == ord('c'):
            counting = not counting
            if not counting:
                an.luminosity_analyse(L)
                center=None
                click_data["click_position"]=None
                L=[]
                
            
        if key == 27:
            break
        
    cap.release()
    cv2.destroyAllWindows()
    
    if L:
        an.luminosity_analyse(L)
        
    return


#%%
def luminosity_graph_from_camera(index=0):
    """
    Capture un flux vidéo depuis une caméra et affiche une courbe de luminosité selon les 
    point d'une droite horizontale en fonction d'un point sélectionné par l'utilisateur et permet:
    - de lancer/arrêter l'affichage de la courbe de luminosité avec la touche 'g',
    - de quitter la fonction avec la touche ÉCHAP
    
    """
    # Ouvre la caméra avec l'index spécifié
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la caméra.")
        return
    
    cv2.namedWindow("Video")  # Crée une fenêtre pour afficher la vidéo
    
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Récupère la hauteur de la vidéo
    graph = False  # Indique si l'affichage de la courbe est activé
    center = None  # Stocke la position du point sélectionné
    click_data = {"click_position": None}  # Dictionnaire pour stocker la position du clic

    # Associe une fonction de rappel pour récupérer la position du clic de la souris
    cv2.setMouseCallback("Video", an.get_position, click_data)
    
    while cap.isOpened():
        ret, frame = cap.read()  # Capture une image de la caméra
        if not ret:
            print("Erreur : Impossible de lire une image depuis la caméra.")
            break
        
        if not graph:
            cv2.imshow('Video', frame)  # Affiche l'image
        
        if graph and center:  # Si la courbe est activé et qu'un point est sélectionné
            L = an.luminosity_array(frame, center)  # Récupère les valeurs de luminosité
            
            # Trace la courbe de luminosité sur l'image
            for i in range(1, len(L)):
                cv2.line(frame, (i - 1, height - L[i - 1]), (i, height - L[i]), (255, 0, 0), 2)
            
            cv2.imshow('Video', frame)  #Affiche l'image
        
        if graph and not center:  # Si la courbe est activé mais qu'aucun point n'est défini
            click_data["click_position"] = None  # Réinitialise la position du clic
            
            while not center:  # Attente d'un clic pour sélectionner un point
                ret, frame = cap.read()
                if not ret:
                    print("Erreur : Impossible de lire une image depuis la caméra.")
                    break
                
                key = cv2.waitKey(1) & 0xFF  # Vérifie si une touche est pressée
                if key == 27:  # Si "Échap" est pressé, quitte la boucle
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                og_frame = frame.copy()  # Sauvegarde une copie de l'image actuelle
                
                # Affiche un message invitant à cliquer
                cv2.putText(frame, 'Cliquez ou suivre la luminosite', (30, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow('Video', frame)
                
                if click_data["click_position"] is not None:  # Si un clic a été détecté
                    center = click_data["click_position"]  # Enregistre la position sélectionnée
                    
                    # Affiche un cercle rouge à l'endroit cliqué
                    satisfaction_frame = og_frame.copy()
                    cv2.circle(satisfaction_frame, (center[0], center[1]), 10, (0, 0, 255), -1)
                    
                    # Demande confirmation à l'utilisateur
                    cv2.putText(satisfaction_frame, 'Voulez vous garder ce point ? [y/n]', (30, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.imshow('Video', satisfaction_frame)
                    cv2.waitKey(1)
                    
                    while True:  # Boucle pour attendre une réponse de l'utilisateur
                        key = cv2.waitKey(0) & 0xFF

                        if key == ord('y'):  # Si 'y' est pressé, valide la sélection
                            break
                        
                        if key == ord('n'):  # Si 'n' est pressé, annule la sélection
                            center = None
                            click_data["click_position"] = None
                            break
                        
                        if key == 27:  # Si "Échap" est pressé, quitte le programme
                            cap.release()
                            cv2.destroyAllWindows()
                            return

            x, y = center  # Récupère les coordonnées du point sélectionné
            
            # Calcule les valeurs de luminosité et trace la courbe
            L = an.luminosity_array(og_frame, center)
            for i in range(1, len(L)):
                cv2.line(frame, (i - 1, height - L[i - 1]), (i, height - L[i]), (255, 0, 0), 3)
            
            cv2.imshow('Video', frame)  # Met à jour l'affichage
        
        key = cv2.waitKey(1) & 0xFF  # Attend une entrée clavier
        
        if key == ord('g'):  # Active/désactive l'affichage du graphique
            graph = not graph
            
            if not graph:  # Réinitialisation en cas de désactivation
                cv2.destroyWindow('Luminosity graph')
                center = None
                click_data["click_position"] = None
                
        if key == 27:  # Quitte le programme si "Échap" est pressé
            break

    cap.release()  # Libère la caméra
    cv2.destroyAllWindows()  # Ferme toutes les fenêtres ouvertes

    return

#%%

def luminosity_graph_from_file(file_name):
    """
    Capture un flux vidéo depuis un fichier vidéo et affiche une courbe de luminosité selon les 
    point d'une droite horizontale en fonction d'un point sélectionné par l'utilisateur.
    Même fonctionnement que luminosity_graph_from_camera
    
    """
    
    cap = cv2.VideoCapture(file_name)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir le fichier.")
        return
    
    # Calculer le délai correct
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000/fps) if fps > 0 else 20  
    
    
    
    cv2.namedWindow("Video")
    
    height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    graph=False
    center=None
    click_data = {"click_position": None}
    cv2.setMouseCallback("Video",an.get_position,click_data)
    
    
    
    
    while cap.isOpened():
        
        ret, frame = cap.read()
        if not ret:
            print("Fin de la vidéo.")
            break  
        
        cv2.imshow('Video',frame)
        
        if graph and center:
            
            L=an.luminosity_array(frame,center)
            
            for i in range(1, len(L)):
                cv2.line(frame,(i - 1,height-L[i - 1]),(i,height-L[i]),(255,0, 0), 2)
            
            cv2.imshow('Video',frame)
            
        
        if graph and not center:
            
            click_data["click_position"] = None
            og_frame=frame.copy()
            cv2.putText(frame, 'cliquer ou vous shouaiter suivre la luminositee', (30,30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            
            while not center:
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                
                
                cv2.imshow('Video',frame)
                
                if click_data["click_position"] is not None:
                    
                    center=click_data["click_position"]
                    cv2.imshow("Video", og_frame)  
                    cv2.waitKey(1)  

                    satisfaction_frame = og_frame.copy()
                    cv2.circle(satisfaction_frame, (center[0], center[1]), 10, (0, 0, 255), -1)
                    cv2.putText(satisfaction_frame, 'Voulez-vous garder cette coordonnee ? [y/n]',(30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA) 
                                                                                                    
                    cv2.imshow('Video', satisfaction_frame)
                    cv2.waitKey(1)  
                    
                    while(True):
                        
                        key = cv2.waitKey(0) & 0xFF

                        if key == ord('y'):  
                            break
                        
                        if key == ord('n'):  
                            center = None
                            click_data["click_position"] = None
                            break
                        
                        if key == 27:
                            cap.release()
                            cv2.destroyAllWindows()
                            return
                    
                        
            x,y=center
                
            L=an.luminosity_array(og_frame,center)
            
            for i in range(1, len(L)):
                cv2.line(frame,(i - 1,height-L[i - 1]),(i,height- L[i]),(255,0, 0), 3)
            
            cv2.imshow('Video',frame)
            
        key = cv2.waitKey(delay) & 0xFF
        
        if key == ord('g'):
            
            graph = not graph
            
            if not graph:
                cv2.destroyWindow('Luminosity graph')
                center=None
                click_data["click_position"]=None
                
            
        if key == 27:
            break
        
    
    cap.release()
    cv2.destroyAllWindows()
    return