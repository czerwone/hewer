# Groupe : Maxime FANTAUZZO et Ghislain ROIG

import pygame
import random
import math
import copy

FENETRE_LARGEUR = 800   # !!  ATTENTION A GARDER DES PROPORTIONS  !!
FENETRE_HAUTEUR = 700   # !! 6/5 POUR LA RESOLUTION DE LA FENETRE !!

BLANC = (255, 255, 255)
NOIR  = (0, 0, 0)
ROUGE = (128, 24, 24)

VIDE                = 0
TERRE               = 1
ROCHE_TENDRE        = 2
ROCHE_DURE          = 3
ROCHE_INCASSABLE    = 4
GOLD                = 10
DIAMANT             = 20

RESISTANCE_TERRE = 1
RESISTANCE_RT = 6
RESISTANCE_RD = 10
RESISTANCE_RI = 10**10
RESISTANCE_GOLD = 15
RESISTANCE_DIAMANT = 25

TEMPS_MAJ_SCENE_INIT = 4    #En secondes
TEMPS_MINIMAL = 1           #En secondes
COEFF_DECREMENT = 30        #Augmenter cette valeur diminue la difficultée

MOVE = 10
ACC_CHUTE = (0, FENETRE_HAUTEUR)
CENTRE         = 0
GAUCHE         = 1
DROITE         = 2
DESSUS         = 4
HAUT_GAUCHE    = 5
HAUT_DROITE    = 6
DESSOUS        = 8
DESSOUS_GAUCHE = 9
DESSOUS_DROITE = 10


#---------------------------------------## Définition MOUVEMENT ###

def mouvement(nom, duree):
    return (nom, duree) # dureé en msec

def nomMouvement(mvt):
    return mvt[0]

def dureeMouvement(mvt):
    return mvt[1]

#-----------------------------------## fin MOUVEMENT ###
#---------------------------------## Definition ANIMATION ###

def nouvelleAnimation():
    return {
        'boucle':False,
        'repetition': 0,
        'momentMouvementSuivant':None,
        'indexMouvement':None,
        'choregraphie':[] #liste de mouvements
    }

def repete(animation, fois):
    animation['repetition'] = fois
    animation['boucle'] = False

def enBoucle(animation):
    animation['boucle'] = True

def ajouteMouvement(animation, mvt):
    animation['choregraphie'].append(mvt)

def mouvementActuel(animation):
    if animation['indexMouvement'] == None:
        return None
    else:
        return nomMouvement(animation['choregraphie'][animation['indexMouvement']])

def commenceMouvement(animation, index):
    animation['indexMouvement'] = index
    animation['momentMouvementSuivant'] = pygame.time.get_ticks() + dureeMouvement(animation['choregraphie'][index])

def commence(animation):
    commenceMouvement(animation, 0)

def arrete(animation):
    animation['indexMouvement'] = None

def anime(animation):
    if animation['indexMouvement'] == None:
        commence(animation)
    elif animation['momentMouvementSuivant'] <= pygame.time.get_ticks():
        if animation['indexMouvement'] == len(animation['choregraphie']) - 1:
            if animation['boucle']:
                commence(animation)
            else:
                if animation['repetition'] > 0:
                    animation['repetition'] -= 1
                    commence(animation)
                else:
                    arrete(animation)
        else:
            commenceMouvement(animation, animation['indexMouvement'] + 1)

#--------------------------------------## Fin ANIMATION ###
#----------------------------------------Joueur------------------------

def joueur():
    return {
        'visible' :False,
        'position'  : [0, 0],
        'vitesse'   : [0, 0],
        'acceleration'   : [0, 0],
        'momentDeplacement': 0,
        'sprite'    : None,
        'poses' : {},
        'animationActuelle':None,
        'animations':{}
    }

def visible(joueur):
    joueur['visible'] = True

def invisible(joueur):
    joueur['visible'] = False

def estVisible(joueur):
    return joueur['visible']

def place(joueur, x, y):
    joueur['position'][0] = x
    joueur['position'][1] = y

def vitesse(entite, vx, vy):
    entite['vitesse'][0] = vx
    entite['vitesse'][1] = vy

def acceleration(entite, ax, ay):
    entite['acceleration'][0] = ax
    entite['acceleration'][1] = ay

def deplace(entite, maintenant):
    dt = (maintenant - entite['momentDeplacement']) / 1000
    #maj vitesse
    entite['vitesse'][0] += entite['acceleration'][0] * dt
    entite['vitesse'][1] += entite['acceleration'][1] * dt
    #maj position
    entite['position'][0] += entite['vitesse'][0] * dt
    entite['position'][1] += entite['vitesse'][1] * dt
    #maj moment déplacement
    entite['momentDeplacement'] = maintenant

def position_joueur(joueur):


    return joueur['position']

def ajoutePose(joueur, nom, image):
    joueur['poses'][nom] = image

def prendsPose(joueur, nom_pose):
    joueur['sprite'] = joueur['poses'][nom_pose]
    visible(joueur)

def dessine(joueur, ecran):
    ecran.blit(joueur['sprite'], joueur['position'])

def commenceAnimation(joueur, nomAnimation, fois = 1):
    joueur['animationActuelle'] = joueur['animations'][nomAnimation]
    if fois == 0:
        enBoucle(joueur['animationActuelle'])
    else:
        repete(joueur['animationActuelle'], fois - 1)
    visible(joueur)

def arreteAnimation(joueur):
    arrete(joueur['animationActuelle'])
    joueur['animationActuelle'] = None

def ajouteAnimation(joueur, nom, animation):
    joueur['animations'][nom] = animation

def estEnAnimation(joueur):
    return joueur['animationActuelle'] != None


#-------------------------------------------## fin joueur ###

def affiche_joueur(entites, ecran):
    for objet in entites:
        if estVisible(objet):
            if estEnAnimation(objet):
                animationActuelle = objet['animationActuelle']
                poseActuelle = mouvementActuel(animationActuelle)
                anime(animationActuelle)
                nouvellePose = mouvementActuel(animationActuelle)
                if nouvellePose == None:
                    objet['animationActuelle'] = None
                    prendsPose(objet, poseActuelle)
                else:
                    prendsPose(objet, nouvellePose)
            dessine(objet, ecran)    

#--------------------------------------digger move----------------

#---------- Fontions

def scene_to_fenetre(pos):
    global scene
    ligne   = pos[0]
    colonne = pos[1]
    x = (FENETRE_LARGEUR / len(scene[0])) * colonne
    y = (FENETRE_HAUTEUR / len(scene)) * ligne
    return [x, y]

def fenetre_to_scene(pos):
    global scene
    x = pos[0]
    y = pos[1]
    colonne = math.floor(x/(FENETRE_LARGEUR/scene_largeur))
    ligne   = math.floor(y/(FENETRE_HAUTEUR/scene_hauteur))
    return [ligne, colonne]

#_ Définition des blocs

def new_bloc():
    return {
        'type'      : VIDE,
        'resistance': 0,
        'texture'   : None,
        'position'  : [0, 0],
        'calque'    : None
    }

def type_bloc(objet, type):
    objet['type'] = type

    if objet['type'] == TERRE:
        objet['resistance'] = RESISTANCE_TERRE
        objet['texture'] = texture_terre

    if objet['type'] == ROCHE_TENDRE:
        objet['resistance'] = RESISTANCE_RT
        objet['texture'] = texture_roche_tendre

    if objet['type'] == ROCHE_DURE:
        objet['resistance'] = RESISTANCE_RD
        objet['texture'] = texture_roche_dure

    if objet['type'] == ROCHE_INCASSABLE:
        objet['resistance'] = RESISTANCE_RI
        objet['texture'] = texture_roche_incassable

    if objet['type'] == GOLD:
        objet['resistance'] = RESISTANCE_GOLD
        objet['texture'] = texture_gold

    if objet['type'] == DIAMANT:
        objet['resistance'] = RESISTANCE_DIAMANT
        objet['texture'] = texture_diamant

def place_bloc(objet, x, y):
    objet['position'][0] = x
    objet['position'][1] = y

def afficher_bloc(objet):
    fenetre.blit(objet['texture'], objet['position'])
    if objet['calque'] != None:
        fenetre.blit(objet['calque'], objet['position'])

def nouvelle_scene(largeur, hauteur):

    scene_ligne = [copy.deepcopy(new_bloc()) for nb in range(largeur)]
    scene = [copy.deepcopy(scene_ligne) for sl in range(hauteur)]
    
    for ligne in range(hauteur - 3, hauteur):
        for colonne in range(largeur):
            type_bloc(scene[ligne][colonne], TERRE)

    return scene

def f_temps(t): #calculé en secondes, return en milisecondes
    t /= 1000
    t_updated = (COEFF_DECREMENT*(TEMPS_MAJ_SCENE_INIT - TEMPS_MINIMAL)) / (t+COEFF_DECREMENT)+ TEMPS_MINIMAL
    return t_updated*1000

def mode(compteur_maj, lim, coef, borne_depart):
    # Pipe le tirage au sort 'random.triangular'
    # en lui donnant pour argument mode une fonction telle que 
    # l'influence sur le tirage au sort évoluera au cours de la partie selon les arguments donnés.
    # Prends en argument le compteur de maj de la scene,
    # la limite vers laquelle va tendre le mode et 
    # le coef qui va déterminer la variation de la fonction
    # la borne de depart entre 0 et 2 inclus
    mode = (coef * (borne_depart - lim)) / (compteur_maj + coef)+ lim
    return mode

def probabilites_bloc(compteur_maj):
    minerai_type = [GOLD, DIAMANT]
    roche_type   = [VIDE, TERRE, ROCHE_TENDRE, ROCHE_DURE, ROCHE_INCASSABLE]

    bloc_minerai = random.choices(minerai_type, cum_weights = [70, 100], k = 1)[0]

    pv = random.triangular(0, 2, mode(compteur_maj, 1, 1, 0.5))
    pt  = random.triangular(0, 2, mode(compteur_maj, 0, 2, 0.5))
    prt = random.triangular(0, 2, mode(compteur_maj, 1, 2, 0))
    prd = random.triangular(0, 2, mode(compteur_maj, 2, 5, 0))
    if compteur_maj >= 25:
        pri = random.triangular(0, 2, mode(compteur_maj, 2, 200, 0))
    else:
        pri = 0
    bloc_roche = random.choices(roche_type, weights = [pv, pt, prt, prd, pri], k = 1)[0]

    bloc_genere = random.choices([bloc_roche, bloc_minerai], cum_weights = [90, 100], k = 1)[0]
    return bloc_genere

def maj_scene():
    global timer, temps_maj_scene, compteur_maj, scene

    if timer >= temps_maj_scene:

        nouvelle_ligne = [copy.deepcopy(new_bloc()) for nb in range(scene_largeur)]

        for colonne in range(scene_largeur):
            type_bloc(nouvelle_ligne[colonne], probabilites_bloc(compteur_maj))

        scene.pop(0)
        scene.append(nouvelle_ligne)
        [x, y] = digger['position']
        place(digger, x, y - dimension_bloc)
        compteur_maj += 1
        temps_maj_scene = f_temps(chrono)
        timer = 0

def dessiner_scene():
    global scene

    for ligne in range(scene_hauteur):
        for colonne in range(scene_largeur):
            bloc = scene[ligne][colonne]
            if bloc['type'] != VIDE:
                bloc = scene[ligne][colonne]
                pos = [ligne, colonne]
                x = scene_to_fenetre(pos)[0]
                y = scene_to_fenetre(pos)[1]
                place_bloc(bloc, x, y)
                afficher_bloc(bloc)

    for x in range(scene_largeur):
        fenetre.blit(texture_lave, (dimension_bloc*x, FENETRE_HAUTEUR-dimension_bloc))
    for x in range(scene_largeur*2):
        fenetre.blit(texture_pics,((dimension_bloc/2)*x,0))

def crop_texture(x, y):
    textures = pygame.image.load('assets/textures.png').convert_alpha(fenetre)
    tile = textures.subsurface((x, y), (32, 32))
    tile = pygame.transform.scale(tile, (dimension_bloc, dimension_bloc))
    return tile

def casser_bloc(objet):
    global compteur_gold, compteur_diamant

    if objet['resistance'] == 0:
        if objet['type'] == GOLD:
            compteur_gold += 1
            bruitages.play(sons['score'])
        elif objet['type'] == DIAMANT:
            compteur_diamant += 1
            bruitages.play(sons['score'])
        objet['type'] = VIDE
    return objet

def bloc_rect(bloc):
    rect = pygame.Rect((bloc['position'][0]-1, bloc['position'][1]-1), (dimension_bloc+1, dimension_bloc+1))
    return rect

def test_collision(joueur):

    hitbox_joueur = pygame.Rect((joueur['position'][0] + ((4.5*digger_largeur)/8),joueur['position'][1]),(((1.5*digger_largeur)/4),digger_hauteur))
    pos_joueur_middle = [(2*hitbox_joueur[0] + hitbox_joueur[2])//2, joueur['position'][1] + digger_largeur/2]
    [ligne, colonne] = fenetre_to_scene(pos_joueur_middle)

    if colonne < scene_largeur-1:
        bloc_d = scene[ligne][colonne + 1]
        if hitbox_joueur.colliderect(bloc_rect(bloc_d)) and bloc_d['type'] != VIDE:
            place(joueur, (bloc_d['position'][0]-dimension_bloc), joueur['position'][1])
    if colonne != 0:
        bloc_g = scene[ligne][colonne - 1]
        if hitbox_joueur.colliderect(bloc_rect(bloc_g)) and bloc_g['type'] != VIDE:
            place(joueur, bloc_g['position'][0] + (dimension_bloc - (4.5*digger_largeur)/8), joueur['position'][1])
    if ligne != scene_hauteur - 1:
        bloc_s = scene[ligne + 1][colonne]
        if hitbox_joueur.colliderect(bloc_rect(bloc_s)) and bloc_s['type'] != VIDE:
            place(joueur, joueur['position'][0], bloc_s['position'][1] - dimension_bloc)
            acceleration(joueur, 0, 0)
            vitesse(joueur, 0, 0)
        else:
            acceleration(joueur, ACC_CHUTE[0], ACC_CHUTE[1])
    if joueur['position'][0] < 0-((4.5*digger_largeur)/8):
        place(joueur, 0-((4.5*digger_largeur)/8), joueur['position'][1])
    elif joueur['position'][0] + digger_largeur > FENETRE_LARGEUR:
        place(joueur, (FENETRE_LARGEUR-dimension_bloc), joueur['position'][1])

def fissurer_bloc(objet): # MODIFIE

    if objet['type'] == ROCHE_TENDRE:
        if objet['resistance'] <= RESISTANCE_RT:
            objet['calque'] = calque_fissure1
        if objet['resistance'] <= (2*RESISTANCE_RT)//3:
            objet['calque'] = calque_fissure2

    if objet['type'] == ROCHE_DURE:
        if objet['resistance'] <= RESISTANCE_RD:
            objet['calque'] = calque_fissure1
        if objet['resistance'] <= (2*RESISTANCE_RD)//3:
            objet['calque'] = calque_fissure2

    if objet['type'] == GOLD:
        if objet['resistance'] <= RESISTANCE_GOLD:
            objet['calque'] = calque_fissure1
        if objet['resistance'] <= (2*RESISTANCE_GOLD)//3:
            objet['calque'] = calque_fissure2

    if objet['type'] == DIAMANT:
        if objet['resistance'] <= RESISTANCE_DIAMANT:
            objet['calque'] = calque_fissure1
        if objet['resistance'] <= (2*RESISTANCE_DIAMANT)//3:
            objet['calque'] = calque_fissure2
    return objet

def miner_bloc(joueur, touche):
    distance_minimale = 50

    stone_sound = random.choice([sons['digging1'], sons['digging2'], sons['digging3'], sons['digging4']])

    hitbox_joueur = pygame.Rect((joueur['position'][0] + ((4.5*digger_largeur)/8),joueur['position'][1]),(((1.5*digger_largeur)/4),digger_hauteur))
    pos_joueur_middle = [(2*hitbox_joueur[0] + hitbox_joueur[2])//2, joueur['position'][1] + digger_largeur/2]
    [ligne, colonne] = fenetre_to_scene(pos_joueur_middle)
    if 0 <= ligne and ligne < scene_hauteur - 1:
        if colonne < scene_largeur-1 and touche == pygame.K_d:
            bloc_d = scene[ligne][colonne + 1]
            if bloc_d['position'][0] - pos_joueur_middle[0] <= distance_minimale:
                bloc_d['resistance'] -= 1
                bloc_d = fissurer_bloc(bloc_d)
                bloc_d = casser_bloc(bloc_d)
                if not bruitages.get_busy():
                    bruitages.play(stone_sound)
        if colonne != 0 and  touche == pygame.K_q:
            bloc_g = scene[ligne][colonne - 1]
            if (pos_joueur_middle[0] - (bloc_g['position'][0] + dimension_bloc)) <= distance_minimale:
                bloc_g['resistance'] -= 1
                bloc_g = fissurer_bloc(bloc_g)
                bloc_g = casser_bloc(bloc_g)
                if not bruitages.get_busy():
                    bruitages.play(stone_sound)
        if touche == pygame.K_s:
            try:
                bloc_s = scene[ligne + 1][colonne]
            except:
                print("Index error bloc_s")
                print("Taille de la matrice :", [scene_hauteur - 1, scene_largeur - 1])
                print("Coordonnées joueur :", [ligne, colonne])
                print("Coordonnées bloc_s :", [ligne + 1, colonne])
            else:
                if bloc_s['position'][1] - (pos_joueur_middle[1] + digger_hauteur) <= distance_minimale:
                    bloc_s['resistance'] -= 1
                    bloc_s = fissurer_bloc(bloc_s)
                    bloc_s = casser_bloc(bloc_s)
                    if not bruitages.get_busy():
                        bruitages.play(stone_sound)



def texte(texte, font, taille, couleur, a_contour = False, couleur_contour = (0, 0, 0)):

    police = pygame.font.SysFont(font, taille, True)
    message = police.render(texte, True, couleur)
    texteLargeur, texteHauteur = police.size(texte)
    if not a_contour:
        return (message, texteLargeur, texteHauteur)
    if a_contour:
        taille_c = int(taille + taille/20)
        police_c = pygame.font.SysFont(font, taille_c, True)
        contour = police_c.render(texte, True, couleur_contour)
        contourLageur, contourHauteur = police_c.size(texte)
        return (message, texteLargeur, texteHauteur, contour, contourLageur, contourHauteur)

def dessiner_pause():
    global pause
    if pause:
        message_pause, messageLargeur, messageHauteur = texte("Pause", 'monospace', int(FENETRE_LARGEUR*0.1875), BLANC)
        fenetre.blit(message_pause, ((FENETRE_LARGEUR - messageLargeur) // 2, (FENETRE_HAUTEUR - messageHauteur) // 4))

def dessiner_ecran_accueil():
    titre, tl, th, ctitre, ctl, cth = texte("HEWER", 'monospace', int(FENETRE_LARGEUR*0.1875), BLANC, True)
    l1, l1l, l1h, cl1, cl1l, cl1h = texte("Vous êtes tombé au fond de la mine.", 'monospace', int(FENETRE_LARGEUR*0.0393), BLANC, True)
    l2, l2l, l2h = texte("Combien de temps survivrez-vous ?", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l3, l3l, l3h = texte("Appuyez sur la touche ESPACE pour commencer.", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l4, l4l, l4h = texte("Commandes :", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l5, l5l, l5h = texte("Flèches gauche et droite pour se déplacer", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l6, l6l, l6h = texte("Q pour miner le bloc de gauche", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l7, l7l, l7h = texte("D pour miner le bloc de droite", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l8, l8l, l8h = texte("S pour miner le bloc de dessous", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    l9, l9l, l9h = texte("P pour pause, ESC pour quitter", 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)

    fenetre.blit(ctitre, ((FENETRE_LARGEUR - ctl) // 2, (FENETRE_HAUTEUR - cth) // 6))
    fenetre.blit(titre, ((FENETRE_LARGEUR - tl) // 2, (FENETRE_HAUTEUR - th) // 6))
    fenetre.blit(cl1, ((FENETRE_LARGEUR - cl1l) // 2, (FENETRE_HAUTEUR - cl1h) // 3))
    fenetre.blit(l1, ((FENETRE_LARGEUR - l1l) // 2, (FENETRE_HAUTEUR - l1h) // 3))
    fenetre.blit(l3, ((FENETRE_LARGEUR - l3l) // 2, 4*(FENETRE_HAUTEUR - l3h) // 6))
    fenetre.blit(l2, ((FENETRE_LARGEUR - l2l) // 2, 5*(FENETRE_HAUTEUR - l2h) // 8))
    fenetre.blit(l4, ((FENETRE_LARGEUR - l4l) // 2, 23*(FENETRE_HAUTEUR - l4h) // 32))
    fenetre.blit(l5, ((FENETRE_LARGEUR) // 6, 25*(FENETRE_HAUTEUR - l5h) // 32))
    fenetre.blit(l6, ((FENETRE_LARGEUR*11) // 48, 26*(FENETRE_HAUTEUR - l6h) // 32))
    fenetre.blit(l7, ((FENETRE_LARGEUR*11) // 48, 27*(FENETRE_HAUTEUR - l7h) // 32))
    fenetre.blit(l8, ((FENETRE_LARGEUR*11) // 48, 28*(FENETRE_HAUTEUR - l8h) // 32))
    fenetre.blit(l9, ((FENETRE_LARGEUR*11) // 48, 29*(FENETRE_HAUTEUR - l9h) // 32))

def gerer_touche(touche):
    global pause, gameOver, enJeu, restart, previous, accueil

    if touche == pygame.K_p and enJeu:
        pause = not pause


    elif touche == pygame.K_y and gameOver:
        restart = True
    if touche == pygame.K_n and gameOver:
        pygame.display.quit()
        pygame.quit()
        exit()
    if touche == pygame.K_SPACE and accueil and not enJeu:
        previous = pygame.time.get_ticks()
        enJeu = True
        accueil = not accueil

    if not pause:
        positionJoueur = position_joueur(digger)
        if touche == pygame.K_RIGHT:
            place(digger, positionJoueur[0] + MOVE, positionJoueur[1])
            commenceAnimation(digger, 'moveR', 1)
        if touche == pygame.K_LEFT:
            place(digger, positionJoueur[0] - MOVE, positionJoueur[1])
            commenceAnimation(digger, 'moveL', 1)
        if touche == pygame.K_q:
            commenceAnimation(digger, 'diggingL', 3)
            miner_bloc(digger, touche)
        if touche == pygame.K_d:
            commenceAnimation(digger, 'diggingR', 3)
            miner_bloc(digger, touche)
        if touche == pygame.K_s:
            commenceAnimation(digger, 'digging', 3)
            miner_bloc(digger, touche)

def traiter_entrees():

    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            exit()
        
        elif evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
            pygame.display.quit()
            pygame.quit()
            exit()

        elif evenement.type == pygame.KEYDOWN:
                gerer_touche(evenement.key)

        elif evenement.type == pygame.KEYUP and enJeu and not gameOver:
                commenceAnimation(digger, 'stand', 0)

def verif_gameOver(joueur): #La vérification se fait via une fonction afin de l'appliquer facilement à plusieurs joueurs dans le cas de l'ajout d'un mode multijoueur.
    global gameOver, enJeu, scene, scene_joueur, opacite, pause

    if joueur['position'][1] < -10 or joueur['position'][1] + dimension_bloc > FENETRE_HAUTEUR:
        fenetre.blit(ecran_noir, (0, 0))
        scene.clear()
        bruitages.play(sons['game-over'])
        opacite = 255
        pause = False
        gameOver = True
        enJeu = False

def dessiner_ecran_fin():
    global prof, gld, dmt, lingot, gemme

    gameover, gml, gmh, cgameover, cgml, cgmh = texte("Game Over", 'monospace', int(FENETRE_LARGEUR*0.1375) , BLANC, True, ROUGE)
    reset, rl, rh, creset, crl, crh = texte("Recommencer une partie ?", 'monospace', int(FENETRE_LARGEUR*0.05), BLANC, True)
    reset2, r2l, r2h, creset2, cr2l, cr2h = texte("Y / N", 'monospace', int(FENETRE_LARGEUR*0.05), BLANC, True)

    fenetre.blit(cgameover, ((FENETRE_LARGEUR - cgml) // 2, (FENETRE_HAUTEUR - cgmh) // 4))
    fenetre.blit(gameover, ((FENETRE_LARGEUR - gml) // 2, (FENETRE_HAUTEUR - gmh) // 4))

    fenetre.blit(creset, ((FENETRE_LARGEUR - crl) // 2, (FENETRE_HAUTEUR*13) // 16))
    fenetre.blit(reset, ((FENETRE_LARGEUR - rl) // 2, (FENETRE_HAUTEUR*13) // 16))
    fenetre.blit(creset2, ((FENETRE_LARGEUR - cr2l) // 2, (FENETRE_HAUTEUR*14) // 16))
    fenetre.blit(reset2, ((FENETRE_LARGEUR - r2l) // 2, (FENETRE_HAUTEUR*14) // 16))

    profondeur, pl, ph = texte(prof, 'monospace', int(FENETRE_LARGEUR*0.043), BLANC)
    gold, gl, gh = texte(gld, 'monospace', int(FENETRE_LARGEUR*0.043), BLANC)
    diamant, dl, dh = texte(dmt, 'monospace', int(FENETRE_LARGEUR*0.043), BLANC)
    

    lingot = pygame.transform.scale(lingot, (int(FENETRE_LARGEUR*0.06), int(FENETRE_HAUTEUR*0.072)))
    gemme  = pygame.transform.scale(gemme,  (int(FENETRE_LARGEUR*0.06), int(FENETRE_HAUTEUR*0.072)))

    fenetre.blit(profondeur, ((FENETRE_LARGEUR - pl) // 2, (FENETRE_HAUTEUR - ph) // 2))

    fenetre.blit(lingot, ((FENETRE_LARGEUR*5)//12, (FENETRE_HAUTEUR*9)//16))
    fenetre.blit(gemme, ((FENETRE_LARGEUR*5)//12, (FENETRE_HAUTEUR*9)//16 + 50))

    fenetre.blit(gold, ((FENETRE_LARGEUR - gl)*7 // 12, (((FENETRE_HAUTEUR+gh/2))*9) // 16))
    fenetre.blit(diamant, ((FENETRE_LARGEUR - gl)*7 // 12, (((FENETRE_HAUTEUR+dh/2))*9) // 16 + 50))

def maj(scene_joueur):
    maintenant = pygame.time.get_ticks()
    for objet in scene_joueur:
        deplace(objet, maintenant)

def affichage_stats():
    global compteur_maj, compteur_gold, compteur_diamant, prof, gld, dmt, lingot, gemme
    prof    = "Profondeur : {}".format(compteur_maj)
    gld     = "{}".format(compteur_gold)
    dmt     = "{}".format(compteur_diamant)

    profondeur, pl, ph = texte(prof, 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    gold, gl, gh = texte(gld, 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)
    diamant, dl, dh = texte(dmt, 'monospace', int(FENETRE_LARGEUR*0.025), BLANC)

    lingot = pygame.image.load('assets/gold_ingot.png').convert_alpha(fenetre)
    gemme = pygame.image.load('assets/diamond_gem.png').convert_alpha(fenetre)

    lingot = pygame.transform.scale(lingot, (int(FENETRE_LARGEUR*0.04), int(FENETRE_HAUTEUR*0.048)))
    gemme  = pygame.transform.scale(gemme,  (int(FENETRE_LARGEUR*0.04), int(FENETRE_HAUTEUR*0.048)))

    fenetre.blit(profondeur, ((FENETRE_LARGEUR*23)//32, (FENETRE_HAUTEUR)//24))
    fenetre.blit(lingot, (((FENETRE_LARGEUR*23)//32) + (2*pl)//3, (FENETRE_HAUTEUR*2)//24))
    fenetre.blit(gold, (((FENETRE_LARGEUR*23)//32) + pl - gl, (FENETRE_HAUTEUR*2)//24 + gh//2))
    fenetre.blit(gemme, (((FENETRE_LARGEUR*23)//32) + (2*pl)//3, (FENETRE_HAUTEUR*13)//96))
    fenetre.blit(diamant, (((FENETRE_LARGEUR*23)//32) + pl - dl, (FENETRE_HAUTEUR*13)//96 + dh//2))

#---------- Paramamètres

scene_largeur = FENETRE_LARGEUR//100
scene_hauteur = FENETRE_HAUTEUR//100
dimension_bloc = FENETRE_LARGEUR // scene_largeur
digger_largeur = dimension_bloc 
digger_hauteur = dimension_bloc 


#---------- Boucle de jeu principale


pygame.init()
pygame.mixer.init()
random.seed()
pygame.event.set_allowed(pygame.QUIT)
pygame.event.set_allowed(pygame.KEYDOWN)
pygame.event.set_allowed(pygame.KEYUP)

sons = {
    'musique'       : pygame.mixer.Sound('assets/sounds/musique.mp3'),
    'digging1'      : pygame.mixer.Sound('assets/sounds/stone1.ogg'),
    'digging2'      : pygame.mixer.Sound('assets/sounds/stone2.ogg'),
    'digging3'      : pygame.mixer.Sound('assets/sounds/stone3.ogg'),
    'digging4'      : pygame.mixer.Sound('assets/sounds/stone4.ogg'),
    'score'         : pygame.mixer.Sound('assets/sounds/score.wav'),
    'game-over'     : pygame.mixer.Sound('assets/sounds/game-over.wav')
}

bruitages = pygame.mixer.Channel(5)

fenetre_taille = (FENETRE_LARGEUR, FENETRE_HAUTEUR)
fenetre = pygame.display.set_mode(fenetre_taille)
pygame.display.set_caption('Hewer Fusion')

background = pygame.image.load('assets/background.jpeg').convert_alpha(fenetre)
background = pygame.transform.scale(background, (FENETRE_LARGEUR, FENETRE_HAUTEUR))

ecran_fin = pygame.image.load('assets/gameover_screen.png').convert_alpha(fenetre)
ecran_fin = pygame.transform.scale(ecran_fin, (FENETRE_LARGEUR, FENETRE_HAUTEUR))

ecran_noir = pygame.Surface((FENETRE_LARGEUR, FENETRE_HAUTEUR)).convert_alpha(fenetre)
ecran_noir.fill(NOIR)

texture_roche_tendre = pygame.image.load('assets/roche_tendre.jpg').convert_alpha(fenetre)
texture_roche_tendre = pygame.transform.scale(texture_roche_tendre, (dimension_bloc, dimension_bloc))

texture_roche_dure = pygame.image.load('assets/roche_dure.jpg').convert_alpha(fenetre)
texture_roche_dure = pygame.transform.scale(texture_roche_dure, (dimension_bloc, dimension_bloc))

texture_gold = pygame.image.load('assets/gold.jpg').convert_alpha(fenetre)
texture_gold = pygame.transform.scale(texture_gold, (dimension_bloc, dimension_bloc))

texture_diamant = pygame.image.load('assets/diamant.jpg').convert_alpha(fenetre)
texture_diamant = pygame.transform.scale(texture_diamant, (dimension_bloc, dimension_bloc))

calque_fissure1 = pygame.image.load('assets/fissure1.png').convert_alpha(fenetre)
calque_fissure1.set_alpha(220)
calque_fissure1 = pygame.transform.scale(calque_fissure1, (dimension_bloc, dimension_bloc))

calque_fissure2 = pygame.image.load('assets/fissure2.png').convert_alpha(fenetre)
calque_fissure2.set_alpha(200)
calque_fissure2 = pygame.transform.scale(calque_fissure2, (dimension_bloc, dimension_bloc))

texture_pics = pygame.image.load('assets/pics.png').convert_alpha(fenetre)
texture_pics = pygame.transform.scale(texture_pics, (dimension_bloc/2, dimension_bloc/2))

texture_terre = crop_texture(256, 160)

texture_lave = crop_texture(192, 1600)

texture_roche_incassable = crop_texture(2016, 128)

sons['musique'].play(loops=-1)
scene = nouvelle_scene(scene_largeur, scene_hauteur)
digger = joueur()

for nom_image, nom_fichier in  (('DIGGER_STAND1','digger_stand1.png'),
                                ('DIGGER_STAND2','digger_stand2.png'),
                                ('DIGGER_STAND3','digger_stand3.png'),
                                ('PICKAXE_UP','digger_up.png'),
                                ('PICKAXE_MIDUP','digger_midup.png'),
                                ('PICKAXE_MID','digger_mid.png'),
                                ('PICKAXE_MIDDOWN','digger_middown.png'),
                                ('PICKAXE_DOWN','digger_down.png'),
                                ('PICKAXE_UP2','digger_up copie.png'),
                                ('PICKAXE_MIDUP2','digger_midup copie.png'),
                                ('PICKAXE_MID2','digger_mid copie.png'),
                                ('PICKAXE_MIDDOWN2','digger_middown copie.png'),
                                ('PICKAXE_DOWN2','digger_down copie.png'),
                                ('DIGGER_MOVE_R1','digger_run_1.png'),
                                ('DIGGER_MOVE_R2','digger_run_2.png'),
                                ('DIGGER_MOVE_R3','digger_run_3.png'),
                                ('DIGGER_MOVE_R4','digger_run_4.png'),
                                ('DIGGER_MOVE_R5','digger_run_5.png'),
                                ('DIGGER_MOVE_R6','digger_run_6.png'),
                                ('DIGGER_MOVE_L1','digger_run_1 copie.png'),
                                ('DIGGER_MOVE_L2','digger_run_2 copie.png'),
                                ('DIGGER_MOVE_L3','digger_run_3 copie.png'),
                                ('DIGGER_MOVE_L4','digger_run_4 copie.png'),
                                ('DIGGER_MOVE_L5','digger_run_5 copie.png'),
                                ('DIGGER_MOVE_L6','digger_run_6 copie.png')):

    chemin = 'assets/digger/' + nom_fichier
    image = pygame.image.load(chemin).convert_alpha(fenetre)
    image = pygame.transform.scale(image, (digger_largeur*1.5, digger_hauteur))
    ajoutePose(digger, nom_image, image)

    animation = nouvelleAnimation()
    ajouteMouvement(animation, mouvement('DIGGER_STAND1',250))
    ajouteMouvement(animation, mouvement('DIGGER_STAND2',250))
    ajouteMouvement(animation, mouvement('DIGGER_STAND3',250))
    ajouteMouvement(animation, mouvement('DIGGER_STAND2',250))
    ajouteAnimation(digger, 'stand', animation)

    animation_pickaxe = nouvelleAnimation()
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_UP',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_MIDUP',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_MID',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_MIDDOWN',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_DOWN',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_MIDDOWN',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_MID',35))
    ajouteMouvement(animation_pickaxe, mouvement('PICKAXE_MIDUP',35))
    ajouteAnimation(digger, 'digging', animation_pickaxe)
    
    animation_pickaxe1= nouvelleAnimation()
    ajouteMouvement(animation_pickaxe1, mouvement('PICKAXE_UP',50))
    ajouteMouvement(animation_pickaxe1, mouvement('PICKAXE_MIDUP',50))
    ajouteMouvement(animation_pickaxe1, mouvement('PICKAXE_MID',50))
    ajouteMouvement(animation_pickaxe1, mouvement('PICKAXE_MIDDOWN',50))
    ajouteMouvement(animation_pickaxe1, mouvement('PICKAXE_MID',50))
    ajouteMouvement(animation_pickaxe1, mouvement('PICKAXE_MIDUP',50))
    ajouteAnimation(digger, 'diggingR', animation_pickaxe1)

    animation_pickaxe2 = nouvelleAnimation()
    ajouteMouvement(animation_pickaxe2, mouvement('PICKAXE_UP2',50))
    ajouteMouvement(animation_pickaxe2, mouvement('PICKAXE_MIDUP2',50))
    ajouteMouvement(animation_pickaxe2, mouvement('PICKAXE_MID2',50))
    ajouteMouvement(animation_pickaxe2, mouvement('PICKAXE_MIDDOWN2',50))
    ajouteMouvement(animation_pickaxe2, mouvement('PICKAXE_MID2',50))
    ajouteMouvement(animation_pickaxe2, mouvement('PICKAXE_MIDUP2',50))
    ajouteAnimation(digger, 'diggingL', animation_pickaxe2)

    animation_moveR = nouvelleAnimation()
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R1',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R2',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R3',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R4',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R5',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R6',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R5',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R4',75))
    ajouteMouvement(animation_moveR, mouvement('DIGGER_MOVE_R3',75))
    ajouteAnimation(digger, 'moveR', animation_moveR)

    animation_moveL = nouvelleAnimation()
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L1',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L2',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L3',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L4',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L5',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L6',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L5',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L4',75))
    ajouteMouvement(animation_moveL, mouvement('DIGGER_MOVE_L3',75))
    ajouteAnimation(digger, 'moveL', animation_moveL)

    place(digger, 100, 100)


    scene_joueur = [digger]
    commenceAnimation(digger, 'stand', 0)

running = True
pause = False
temps = pygame.time.Clock()
accueil = True
enJeu = False
gameOver = False
opacite = 255
restart = False
pygame.key.set_repeat(100, 100)

while running:

    timer = 0
    chrono = 0
    compteur_maj = 0
    compteur_gold = 0
    compteur_diamant = 0
    temps_maj_scene = TEMPS_MAJ_SCENE_INIT*1000

    while accueil:
        fenetre.blit(background, (0,0))
        traiter_entrees()
        dessiner_ecran_accueil()
        pygame.display.flip()
        temps.tick(4)
    
    while enJeu:
        traiter_entrees()
        now = pygame.time.get_ticks()
        if not estEnAnimation(digger):
            commenceAnimation(digger, 'stand', 0)
        fenetre.blit(background, (0,0))
        if not pause:
            dt = now - previous
            timer += dt
            chrono += dt
            maj(scene_joueur)
            maj_scene()
        affiche_joueur(scene_joueur, fenetre)
        dessiner_scene()
        fenetre.blit(texture_lave, (0, FENETRE_HAUTEUR-dimension_bloc))
        affichage_stats()
        dessiner_pause()
        test_collision(digger)
        pygame.display.flip()
        temps.tick(40)
        previous = now
        verif_gameOver(digger)

        while gameOver:
            sons['musique'].stop()
            fenetre.blit(ecran_fin, (0, 0))
            dessiner_ecran_fin()
            opacite -=2
            ecran_noir.set_alpha(opacite)
            fenetre.blit(ecran_noir, (0, 0))
            traiter_entrees()
            pygame.display.flip()
            temps.tick(30)
            if restart:
                scene = nouvelle_scene(scene_largeur, scene_hauteur)
                acceleration(digger, 0, 0)
                vitesse(digger, 0, 0)
                place(digger, 100, 100)
                accueil = True
                restart = False
                sons['musique'].play(loops=-1)
                gameOver = False


pygame.display.quit()
pygame.quit()
exit()

