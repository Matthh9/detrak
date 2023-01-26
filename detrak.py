# -*- coding: utf-8 -*-
"""
Created 25/01/2023

@author: Matthieu
"""



import sys
from PyQt5 import QtWidgets
from PyQt5 import uic


from functools import partial

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
        self.des=[]
        
        self.cases = ((self.bouton_11, self.bouton_12, self.bouton_13, self.bouton_14, self.bouton_15),
                 (self.bouton_21, self.bouton_22, self.bouton_23, self.bouton_24, self.bouton_25),
                 (self.bouton_31, self.bouton_32, self.bouton_33, self.bouton_34, self.bouton_35),
                 (self.bouton_41, self.bouton_42, self.bouton_43, self.bouton_44, self.bouton_45),
                 (self.bouton_51, self.bouton_52, self.bouton_53, self.bouton_54, self.bouton_55)
                 )
        self.image_des = (self.de_1, self.de_2)
        
        self.jeu = [["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ["", "", "", "", ""],
               ]
        
        for ligne in self.cases:
            for case in ligne:
                case.clicked.connect(partial(self.click, case))
        
        #on initialise la 1ere case avec une valeur, variante apportée à la régle
        # normalement le joueur peut choisir son 1er symbol
        self.premiere_case()

        #on lance une 1ere fois les dès pour lancer la partie
        self.lancer()
        
        

    def premiere_case(self):
        valeur, image = random.choice(list(self.formes.items()))
        self.bouton_11.setStyleSheet("border-image : url("+image+".png) stretch;")
        self.bouton_11.setEnabled(False)
        self.jeu[0][0]=valeur
        
        
    def click(self, case):     
        #on récupère le nom de la case pour pouvoir stocker les infos des valeurs dans un tableau à part
        sending_button = self.sender()
        nom_bouton = sending_button.objectName().split("_")[1]
        ligne = int(nom_bouton[0])-1
        colonne = int(nom_bouton[1])-1
        self.jeu[ligne][colonne]=self.des[0]
        
        #on change le background de la case pour afficher le jeu
        # utiliser border-image permet d'étirer l'image et éviter les répétitions de l'image dans les boutons
        case.setStyleSheet("border-image : url("+self.formes[self.des[0]]+".png) stretch;")
        case.setEnabled(False)
        self.des.pop(0)
        
        
        #s'il n'y a plus de coup à jouer on relance les dès pour les prochains coups
        if len(self.des)==0:
            self.lancer()
        
        
    def lancer(self):
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

        
        




##############################################################################
### GENERAL
##############################################################################
if __name__ == "__main__":
    app = 0 # if not the core will die
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())