# -*- coding: utf-8 -*-
"""
Created 25/01/2023

@author: Matthieu
"""



import sys
from PyQt5 import QtWidgets
from PyQt5 import uic

import time
import random
#permet d'avoir un aléatoire un peu plus aléatoire
random.seed(int(time.time()))


#menu principal
MainFile = "ihm.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainFile)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        #self.formes = ('barre', 'croix', 'diagonal', 'diese', 'triangle')
        self.formes = {1: 'barre', 2: 'croix', 3: 'diagonal', 4:'diese', 5:'triangle', 6: 'rond'}
        
        self.cases = ((self.bouton_11, self.bouton_12, self.bouton_13, self.bouton_14, self.bouton_15),
                 (self.bouton_21, self.bouton_22, self.bouton_23, self.bouton_24, self.bouton_25),
                 (self.bouton_31, self.bouton_32, self.bouton_33, self.bouton_34, self.bouton_35),
                 (self.bouton_41, self.bouton_42, self.bouton_43, self.bouton_44, self.bouton_45),
                 (self.bouton_51, self.bouton_52, self.bouton_53, self.bouton_54, self.bouton_55)
                 )
        self.image_des = (self.de_1, self.de_2)
        
        #on attache le signal click sur les boutons représentant les cases à jouer afin d'y attribuer les valeurs des dès
        for ligne in self.cases:
            for case in ligne:
                case.clicked.connect(self.click)
        
        
        self.reset()
        
        

    def reset(self):
        #variable qui va stocker les valeur des dès randoms pour pouvoir les jouer
        self.des=[]
        
        for ligne in self.cases:
            for case in ligne:
                case.setStyleSheet("")
                case.setEnabled(True)
        
        #dictionnaire contenant les cases voisines pour chaque case de la grille
        self.voisin = {}
        for ligne in self.cases:
            for case in ligne:
                voisin=self.trouver_voisin(case)
                self.voisin[case]=voisin
               
        
        self.jeu = [["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ]
        
        #dictionnaire contenant les valeurs des cases pour faire les différents calculs de résultat
        self.jeu2 = {}
        for ligne in self.cases:
            for case in ligne:
                self.jeu2[case]=""
        
        
        self.nbr_case_restante = 25
        
        #cette variable permet de sélectionner la pénalité pour les lignes sans suite
        self.point_penalite = 0
        self.tableau_resultat = {self.resultat_L1: self.point_penalite,
                     self.resultat_L2: self.point_penalite,
                     self.resultat_L3: self.point_penalite,
                     self.resultat_L4: self.point_penalite,
                     self.resultat_L5: self.point_penalite,
                     self.resultat_C1: self.point_penalite,
                     self.resultat_C2: self.point_penalite,
                     self.resultat_C3: self.point_penalite,
                     self.resultat_C4: self.point_penalite,
                     self.resultat_C5: self.point_penalite
                     }
        self.calcul_resultat()
        
        #on initialise les labels contenant le résultat avec la valeur attachée, au début surtout le point de pénalité
        for key, value in self.tableau_resultat.items():
            key.setText(str(value))
    
        
        #on initialise la 1ere case avec une valeur aléatoire, variante apportée à la régle
        # normalement le joueur peut choisir son 1er symbol
        self.premiere_case()

        #on lance une 1ere fois les dès pour lancer la partie
        self.lancer_des()
        

    def premiere_case(self):
        valeur, image = random.choice(list(self.formes.items()))
        self.bouton_11.setStyleSheet("border-image : url("+image+".png) stretch;")
        self.bouton_11.setEnabled(False)
        self.jeu[0][0]=valeur
        self.jeu2[self.bouton_11]=valeur
        self.remove_voisin(self.bouton_11)
        self.nbr_case_restante-=1
        
        
    def click(self): 
        #on récupère le nom de la case pour pouvoir stocker les infos des valeurs dans un tableau à part
        sending_button = self.sender()
        nom_bouton = sending_button.objectName().split("_")[1]
        
        #on retire 1 pour le début des listes à 0 => voir si on ne peut pas intégrer ça avec un nom de case prenant ça déjà en compte
        ligne = int(nom_bouton[0])-1
        colonne = int(nom_bouton[1])-1
        self.jeu[ligne][colonne]=self.des[0]
        self.jeu2[sending_button]=self.des[0]

        coup_valide=False
        if len(self.des)==2:
            self.remove_voisin(sending_button)
            
            # groupe_isole=self.check_groupe_isole(sending_button)
            self.groupe_isole=self.check_groupe_isole(sending_button)
            
            self.activer_click_voisin(self.groupe_isole[1])
            
            coup_valide=True
            
        elif len(self.des)==1:
            groupe_isole=self.check_groupe_isole(sending_button)
            print("groupe isole ",groupe_isole)
            if groupe_isole==0:
                #ça veut dire qu'on vient d'isoler une case du coup il faut rejouer
                self.jeu[ligne][colonne]=""
                self.jeu2[sending_button]=""
                
                self.groupe_isole=self.groupe_isole[1]
                self.groupe_isole.remove(sending_button)
                
                
                # print("ERREUR : case imposée sinon une case sera isolée")
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Case impossible à jouer car elle entraine une isolation de case, merci de sélectionner une autre case")
                msg.setWindowTitle("Error")
                msg.exec_()
        
                self.activer_click_voisin(self.groupe_isole)
                for voisin in self.groupe_isole:
                    self.voisin[voisin].append(sending_button)
            elif groupe_isole==-1:
                self.message_fin("perdu")
            else:
                 coup_valide=True
        
        if coup_valide:
            #on change le background de la case pour afficher le jeu
            # utiliser border-image permet d'étirer l'image et éviter les répétitions de l'image dans les boutons
            sending_button.setStyleSheet("border-image : url("+self.formes[self.des[0]]+".png) stretch;")
            sending_button.setEnabled(False)
            
            self.maj_resultat(ligne, colonne)
            self.des.pop(0)
            self.image_des[0].setStyleSheet("")
            self.nbr_case_restante-=1
        
        #s'il n'y a plus de coup à jouer on relance les dès pour les prochains coups
        if len(self.des)==0:
            #on réactive toutes les cases ou on peut encore jouer
            for case in self.voisin.keys():
                case.setEnabled(True)
                
            self.lancer_des()
            
        if self.nbr_case_restante==0:
            self.message_fin("victoire")
            

        
    def lancer_des(self):
        #valeur, image = random.choice(list(self.formes.items()))
        # for de in self.image_des:
        #     de.setStyleSheet("border-image : url("+image+".png) stretch;")
        #     self.des.append(valeur)
        
        #test en faisant une boucle de 2 itérations pour avoir un random simulant un lancé de dès
        # => pb nous avions toujours des doubles
        # changement pour faire une liste de random limitant les doubles mais les rendants quand même possible
        # random sur un range plus grand puis on fait la division euclidienne par 6 et on prend cette valeur
        
        lance=random.sample(range(7,36), 2)
        
        for i in range (0,2):     
            valeur=lance[i]//6
            image=self.formes[valeur]
            self.image_des[i].setStyleSheet("border-image : url("+image+".png) stretch;")
            self.des.append(valeur)
        

    
    def maj_resultat(self, ligne, colonne):
        #on calcul les résultats rappel des résultats :
        #  2 symboles = 2 pts
        #  3 symboles = 3 pts
        #  4 symboles = 8 pts
        #  5 symboles = 10 pts
        
        score = {1:0, 2: 2, 3: 3, 4: 8, 5: 10}
        #on recupère les cles du dictionnaire des résultats pour trouver le bon label à mettre à jour pour l'affichage des résultats
        cle=list(self.tableau_resultat.keys())
        
        
        #on regarde la MAJ du résultat de la ligne
        symbole_precedent=self.jeu[ligne][0]
        repetition=1
        point=0
        for symbole in self.jeu[ligne][1:]:
            if symbole == symbole_precedent and symbole != "":
                repetition+=1
            else:
                point+=score[repetition]
                symbole_precedent=symbole
                repetition=1
        
        #permet de prendre en compte le cas d'une ligne complète avec le même symbole
        point+=score[repetition]
        
        #si on a effectivement marqué des points on fait la MAJ
        if point!=0:
            self.tableau_resultat[cle[ligne]]=point
            cle[ligne].setText(str(point))
        
             
        #on regarde la MAJ du résultat de la colonne
        symbole_precedent=self.jeu[0][colonne]
        repetition=1
        point=0
        for i in range(1,5):
            if self.jeu[i][colonne] == symbole_precedent and self.jeu[i][colonne] != "":
                repetition+=1
            else:
                point+=score[repetition]
                symbole_precedent=self.jeu[i][colonne]
                repetition=1
        
        #permet de prendre en compte le cas d'une ligne complète avec le même symbole
        point+=score[repetition]
        
        #si on a effectivement marqué des points on fait la MAJ
        if point!=0:
            self.tableau_resultat[cle[colonne+5]]=point
            cle[colonne+5].setText(str(point))
        
        self.calcul_resultat()
        
    
    def calcul_resultat(self):
        resultat=sum(self.tableau_resultat.values())
        self.resultat_general.setText(str(resultat))
        

    def trouver_voisin(self, case):
        nom_bouton=case.objectName().split("_")[1]
        ligne = int(nom_bouton[0])-1
        colonne = int(nom_bouton[1])-1
        voisin = []
        
        for x in range(ligne-1,ligne+2):
            if x>=0 and x<5:
                for y in range(colonne-1,colonne+2):
                    if y>=0 and y<5:
                        voisin.append(self.cases[x][y]) 
        #on retire la propre cases des voisins
        voisin.remove(case)
        
        return voisin
    
    
    def remove_voisin(self, case):
        #self.voisin[case]=[]
        # print("remove voisin")
        # print("case à supprimer ", case, " ",case.objectName())
        voisins=self.voisin[case]
        for voisin in voisins:
            # print(voisin.objectName())
            # print(self.voisin[voisin])
            #Try car si le voisin est passé dans les cases isolées il a déjà supprimé la case acutelle
            try:
                self.voisin[voisin].remove(case)
            except:
                pass
        
                
    def activer_click_voisin(self, voisins):
        for case in self.voisin.keys():
            case.setEnabled(False)
        
        for voisin in voisins:
            voisin.setEnabled(True)
            
        
    def check_groupe_isole(self, case_joue):
        #pour trouver les groupes isolés on va regarder si en parcourant tous les 
        #voisins possibles on a un nombre pair ou impair de case
        #si pair il n'y aura pas de case isolé dans le groupe
        #si impair on foit forcer le second dès dans ce groupe pour éviter les isolées
        dict_groupes=dict()
        groupes=[]
        
        case_a_visiter=[c for c in self.jeu2.keys() if self.jeu2[c] == '']
        
        while len(case_a_visiter)!=0:
            sous_groupe=[]
            sous_groupe_a_visiter=[case_a_visiter[0]]
            
            while len(sous_groupe_a_visiter)!=0:
                case=sous_groupe_a_visiter[0]
                
                case_a_visiter.remove(case)
                sous_groupe_a_visiter.remove(case)
                sous_groupe.append(case)
                
                #on recupère les voisins de la case que l'on calcule mais que nous n'avons pas encore visité
                #voisin=[v for v in self.voisin[case] if v in case_a_visiter]
                voisin=list( set(self.voisin[case]) & set(case_a_visiter) )
                #permet de regrouper les listes sous_groupe_a_visiter et voisin en supprimant les doublons
                sous_groupe_a_visiter=list(set(sous_groupe_a_visiter + voisin))
            
            if len(sous_groupe) % 2:
                groupes.append(sous_groupe)
                dict_groupes[ tuple(sous_groupe) ]=len(sous_groupe) % 2
        
        
        nbr_groupe_impair=len(dict_groupes)
        
        #On regarde s'il y a des groupes de case en nombre impair
        # 2 cas, si c'est le premier dés on évite de faire 1 groupe impair
        # si c'est le 2ème dés on évite de faire 2 groupes impairs
        print("nbr impair : ",nbr_groupe_impair)
        if len(self.des)==2 and nbr_groupe_impair==1:
            instersection=list( set( list(dict_groupes.keys())[0] ) & set(self.voisin[case_joue]) )
            return(1,instersection)
        elif len(self.des)==1 and nbr_groupe_impair==0:
            return(1,[])
        elif len(self.des)==1 and nbr_groupe_impair==1:
            return(0)
        else : return(-1)
        


    def message_fin(self, choix):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        
        msg.setStandardButtons( QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes )
        msg.setDefaultButton(QtWidgets.QMessageBox.Yes)
        
        if choix=="victoire":
            
            classement= [14,19,24,29]
            citation= ["Peut mieux faire","Moyen","Bon","Expert","Grand maître"]
            resultat_total = int(self.resultat_general.text())
            
            classement.append(resultat_total).sort()
            index = classement.index(resultat_total)
        
            msg.setWindowTitle("Félicitation")
            msg.setText( "Nombre de point : %d"%(resultat_total) )
            msg.setInformativeText(citation[index]+"\nVoulez-vous rejouer ?")
        else:
            msg.setWindowTitle("Game Over")
            msg.setText( "Perdu, trop de cases isolées" )
            msg.setInformativeText("Voulez-vous rejouer ?")
        
        choix=msg.exec_()
    
        if choix == QtWidgets.QMessageBox.Yes:
            self.reset()
        else:
            self.close()
        
        
                

##############################################################################
### GENERAL
##############################################################################
if __name__ == "__main__":
    app = 0 # if not the core will die
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())