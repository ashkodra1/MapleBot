from Data import Data

class grilleSalle: #Classe du grillage pour que chaque case ait les variables suivantes
    mur = False #sert à déteminer s'il y a présence d'un mur
    dataGrille = [] #grillage
    quantite = 0  #la quantité de données dans chaque case

    #On commence la séparation en haut à gauche des données
    limiteSuppX = 0 #la valeur maximale en X acceptée dans la case
    limiteInfX = 0 #la valeur minimale en X acceptée dans la case
    limiteSuppY = Data.trouverMaxY(Data.data) #la valeur maximale en Y acceptée dans la case 
    limiteInfY = Data.trouverMaxY(Data.data) #la valeur minimale en Y acceptée dans la case


    def creerGrille(data): #métode pour creer un grillage et séparer les données
        #création de la grille
        grille = [[grilleSalle for i in range(int((Data.trouverMaxY(data)-Data.trouverMinY(data))/Data.espacement)+1)] for j in range(int((Data.trouverMaxX(data)-Data.trouverMinX(data))/Data.espacement)+1)] 

        #initialisation des pointeurs
        pointeurLimSuppX = Data.trouverMinX(data) 
        pointeurLimInfX = Data.trouverMinX(data)
        
        for i in range(len(grille)): # on parcours les colonnes |
            #on met les pointeurs Y à leur position initiales
            pointeurLimSuppY = Data.trouverMaxY(data) 
            pointeurLimInfY = Data.trouverMaxY(data)
            pointeurLimInfX= pointeurLimSuppX #la limite inférieure de la nouvelle case est égale à la limite suppérieure de l'acienne case

            #Si il reste moins que l'espacement prévu, alors la valeur maximale en X correspond à la limite de la dernière colonne
            if (Data.trouverMaxX(data) - pointeurLimSuppX) < Data.espacement: 
                pointeurLimSuppX = Data.trouverMaxX(data)
            else: #Sinon la limite de la prochaine case est à une distance donnée de celle d'avant
                pointeurLimSuppX += Data.espacement

            for j in range (len(grille[0])): # on parcours les lignes -
                pointeurLimSuppY = pointeurLimInfY #la limite suppérieure de la nouvelle case est égale à la limite inférieure de l'acienne case
                if (pointeurLimInfY - Data.trouverMinY(data)) < Data.espacement:
                    pointeurLimInfY = Data.trouverMinY(data)
                else: 
                    pointeurLimInfY -= Data.espacement   

                grille[i][j].limiteSuppX = pointeurLimSuppX
                grille[i][j].limiteInfX = pointeurLimInfX
                grille[i][j].limiteSuppY = pointeurLimSuppY
                grille[i][j].limiteInfY = pointeurLimInfY
                #print("Point (", i, ", ", j, ") : LimiteSuppX = ", grille[i][j].limiteSuppX, "; LimiteInfX = ", grille[i][j].limiteInfX, "; LimiteSuppY = ", grille[i][j].limiteSuppY, "; LimiteInfY = ",grille[i][j].limiteInfY)

                for point in range(len(data)): # on parcours les points des données originales
                    if (data[point][0] >= grille[i][j].limiteInfX and data[point][0] <= grille[i][j].limiteSuppX) and (data[point][1] >= grille[i][j].limiteInfY and data[point][1] <= grille[i][j].limiteSuppY):
                        grille[i][j].dataGrille.append(data[point]) 

                grille[i][j].quantite = len(grille[i][j].dataGrille)
                print(grille[i][j].quantite)

                
                


