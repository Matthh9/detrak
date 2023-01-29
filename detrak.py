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
        #variable qui va stocker les valeur des dès randoms pour pouvoir les jouer
        self.des=[]
        
        self.cases = ((self.bouton_11, self.bouton_12, self.bouton_13, self.bouton_14, self.bouton_15),
                 (self.bouton_21, self.bouton_22, self.bouton_23, self.bouton_24, self.bouton_25),
                 (self.bouton_31, self.bouton_32, self.bouton_33, self.bouton_34, self.bouton_35),
                 (self.bouton_41, self.bouton_42, self.bouton_43, self.bouton_44, self.bouton_45),
                 (self.bouton_51, self.bouton_52, self.bouton_53, self.bouton_54, self.bouton_55)
                 )
        self.image_des = (self.de_1, self.de_2)
        
        self.voisin = {}
        
        for ligne in self.cases:
            for case in ligne:
                voisin=self.trouver_voisin(case)
                self.voisin[case]=voisin
               
        # print("init voisin")
        # print(self.voisin)
        # print()
        
        self.jeu = [["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ]
        
        self.jeu2 = {}
            
        for ligne in self.cases:
            for case in ligne:
                self.jeu2[case]=""
        
        # print(self.jeu2)
        
        self.nbr_case_restante = 25
        
        #cette variable permet de sélectionner la pénalité pour les lignes sans suite
        self.point_penalite = -5
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
        
        #on attache le signal click sur les boutons représentant les cases à jouer afin d'y attribuer les valeurs des dès
        for ligne in self.cases:
            for case in ligne:
                case.clicked.connect(self.click)
        
        #on initialise la 1ere case avec une valeur aléatoire, variante apportée à la régle
        # normalement le joueur peut choisir son 1er symbol
        self.premiere_case()

        #on lance une 1ere fois les dès pour lancer la partie
        self.lancer_des()
        
        print(self.jeu2)
        

    def premiere_case(self):
        valeur, image = random.choice(list(self.formes.items()))
        self.bouton_11.setStyleSheet("border-image : url("+image+".png) stretch;")
        self.bouton_11.setEnabled(False)
        self.jeu[0][0]=valeur
        self.jeu2[self.bouton_11]=valeur
        self.remove_voisin(self.bouton_11)
        
        
    def click(self):     
        #on récupère le nom de la case pour pouvoir stocker les infos des valeurs dans un tableau à part
        sending_button = self.sender()
        nom_bouton = sending_button.objectName().split("_")[1]
        #on retire 1 pour le début à 0
        ligne = int(nom_bouton[0])-1
        colonne = int(nom_bouton[1])-1
        self.jeu[ligne][colonne]=self.des[0]
        self.jeu2[sending_button]=self.des[0]
        
        #on change le background de la case pour afficher le jeu
        # utiliser border-image permet d'étirer l'image et éviter les répétitions de l'image dans les boutons
        sending_button.setStyleSheet("border-image : url("+self.formes[self.des[0]]+".png) stretch;")
        sending_button.setEnabled(False)
        self.des.pop(0)
        self.image_des[0].setStyleSheet("")
        
        self.maj_resultat(ligne, colonne)
        
        
        # self.activer_click_voisin(sending_button)
        self.remove_voisin(sending_button)
        # self.check_dependance()
        
        self.check_groupe_isole(sending_button)
        
        
        #s'il n'y a plus de coup à jouer on relance les dès pour les prochains coups
        if len(self.des)==0:
            #on réactive toutes les cases ou on peut encore jouer
            for case in self.voisin.keys():
                case.setEnabled(True)
                
            self.lancer_des()
        # else:
        #     #si on ne relance pas le des c'est qu'il reste un coup à jouer du coup on active juste les voisins
        #     print("pressions ",sending_button)
        #     self.activer_click_voisin(sending_button)
        
        
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
            self.voisin[voisin].remove(case)
            
        self.voisin[case]=[-1]
        # del self.voisin[case]
        
        print("fin remove voisin")
        
        
    def check_dependance(self):
        print("check_dependance")
        for case,voisins in self.voisin.items():
            if len(voisins)==1:
                print("1 seul voisin : dépendance")
                print(voisins[0].objectName())
                self.voisin[voisins[0]]=[case]
        
                
    def activer_click_voisin(self, case_joue):
        for case in self.voisin.keys():
            case.setEnabled(False)
        
        print(case_joue)
        print("activation case")
        print(self.voisin[case_joue])
        for case in self.voisin[case_joue]:
            case.setEnabled(True)
            
            
    def check_groupe_isole(self, case_joue):
        print("recherche de groupe isolé")
        groupes=[]
        for case in self.jeu2: #pour chaque case
            print("début traitement pour la case ", case.objectName())
            trouve=False
            
            
            if self.jeu2[case]=="": #si elle n'est pas jouée, on regarde si elle fait partie d'un groupe
                print("case vide")
                for n_groupe in range(0,len(groupes)): #pour chacun des groupes
                    if case in groupes[n_groupe]:
                        trouve=True
                        
                        for voisin in self.voisin[case]:
                            if not voisin in groupes[n_groupe]:
                                groupes[n_groupe].append(voisin)
                        
                        break
                
                if not trouve:
                    print("creation d'un nouveau groupe")
                    groupe=[case]
                    for voisin in self.voisin[case]:
                        groupe.append(voisin)
                    groupes.append(groupe)
                    
        print(groupes)
        
        #self.groupes=groupes
        
        
                

##############################################################################
### GENERAL
##############################################################################
if __name__ == "__main__":
    app = 0 # if not the core will die
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())