"""
Todo:
mobility çizilmesinden dolayı oluşan yavaşlık
Mobility resetten sonra doğru çizmiyor
Uzun rokta at varken rok atılabiliyor
Geçerken alma sorunu
"""

import os
import pygame
from pygame import event
from pygame import color
import ChessEngine
from ChessEngine import GameState
import random
import time
import mobilityplots
from threading import Thread
import buttons
import AiMove



WIDTH=HEIGHT=400#genişlik ve boyu
WindowWidth=1535
WindowHeight=800#ekranın boyutu
DIMENSION=8 #8x8 tahtanın derinliği
SQUARE_SIZE=HEIGHT // DIMENSION #8 eşit parçaya böler 400lük uzunluğu
#MAX_FPS=15 #animasyonlar için
IMAGES={}#images için dictionary

#loading images----
ICON=pygame.image.load('bN.png')#icon surface,
RESTART=pygame.image.load("restart.png")
RESIGN=pygame.image.load("resign.png")
CUSTOM=pygame.image.load("custom.png")
STARTFROMW=pygame.image.load("customW.png")
STARTFROMB=pygame.image.load("customB.png")
#mobility begining---
beginingMobilityPng=pygame.image.load("beginingMobility.png") 

#bunlar mobility grafiği için----
moveNumw=0
moveNumb=0

#locations--------
#400 400
boardxr=1400
boardxl=1000
boardyt=200
boardyb=600

#50 57
restartxr=1485
restartxl=1435
restartyt=300
restartyb=357

#50 42
resignxr=1485
resignxl=1435
resignyt=400
resignyb=442

#50 50
customxr=1485
customxl=1435
customyt=500
customyb=550

#25 25 startW
startWxr=1450
startWxl=1425
startWyt=560
startWyb=585

#25 26 startB
startBxr=1510
startBxl=1485
startByt=560
startByb=586

def main():
    #değişkenler ve listeler---------
    pieceCaptured=".."
    moveNumw=0
    moveNumb=0
    wValidMovesLen=[20,]
    bValidMovesLen=[20,]
    moveNumListw=[0,]
    moveNumListb=[0,]    
    pieceCapturedListW=[] #alınan taşları tutan liste 
    pieceCapturedListB=[]
    #-----------------------------
    #ekranı başlatmak-----
    pygame.init()
    pygame.display.set_caption('Chess')
    pygame.display.set_icon(ICON)#ICON yukarıda hazırladığımız surface
    screen=pygame.display.set_mode((WindowWidth,WindowHeight),pygame.SWSURFACE)#büyük ekran oluştu
    #clock=pygame.time.Clock()
    screen.fill(pygame.Color(0,0,0,0))#arkaplan rengi
    #-------------------------

    gamestate=ChessEngine.GameState()#sınıfa erişim ve gamestate objesi oluşturmak
    validMoves=gamestate.getValidMoves()

    #flags    
    moveMade=False #hamle yapıldığını tutan bir flag
    gameOver=False #oyun bitti mi
    resigned=False 
    customing=False
    #ikisi true demek insan demek gibi düşün ikisi de true olursa 2 insan ikisi de false olursa iki ai oynuyor
    firstPlayer=True
    secondPlayer=False

    #buttons ---------
    restartButton=buttons.Button(screen,1435,300,RESTART)
    resignButton=buttons.Button(screen,1435,400,RESIGN)
    customButton=buttons.Button(screen,1435,500,CUSTOM)
    customStartW=buttons.Button(screen,1425,560,STARTFROMW)
    customStartB=buttons.Button(screen,1485,560,STARTFROMB)

    #button calls
    restartButton.draw()
    resignButton.draw()
    customButton.draw()
    customStartW.draw()
    customStartB.draw()

    loadImages()#yalnızca bir kere yüklüyoruz
    #-----------------------------------------
    running=True
    sqSelected=()#hiçbir kare seçili değil burada,son clicklenen pozisyonu tutacak
    playerClicks=[]#oyuncunun tıkladığı kareleri tutacak


    while running:    
        humanTurn=(gamestate.whiteToMove and firstPlayer) or (not gamestate.whiteToMove and secondPlayer)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running=False

            if running==False:
                pygame.quit() 

            #mouse handler--------------------------------------------------------------------------------------------------------------------
            elif e.type==pygame.MOUSEBUTTONDOWN:
                location=pygame.mouse.get_pos()#x,y mouse location
                
                #customa tıklandı mı mobilityi burada da sıfırla 
                if (location[0]>customxl and location[0]<customxr and location[1]>customyt and location[1]<customyb):
                    customing=True # bunu customing işlemi bitince yani başlata tıklayınca False yapacağız
                    #konumu sıfırla
                    gamestate=ChessEngine.GameState()
                    validMoves=gamestate.getValidMoves()
                    sqSelected=()
                    playerClicks=[]
                    pieceCapturedListW=[]
                    pieceCapturedListB=[]
                    moveMade=False
                    resetMobility(screen,beginingMobilityPng)
                    gameOver=False
                    resigned=False
                      

                if customing==True:
                    
                    #if başlat clicked customing false yap
                    if (location[0]>startWxl and location[0]<startWxr and location[1]>startWyt and location[1]<startWyb):
                        gamestate.whiteToMove=True
                        validMoves=gamestate.getValidMoves()
                        customing=False
                         
                        
                    if (location[0]>startBxl and location[0]<startBxr and location[1]>startByt and location[1]<startByb):
                        gamestate.whiteToMove=False
                        validMoves=gamestate.getValidMoves()
                        customing=False
                         
                        
                        
                    #istediğin yere istediğin taşı koyabilmeyi sağla
                    #sıra değişme olmayacak istediği taşa tıklayıp istediği yere koyabilecek
                    if (location[0]>boardxl and location[0]<boardxr and location[1]>boardyt and location[1]<boardyb):
                        column = (location[0]-1000)//SQUARE_SIZE
                        row = (location[1]-200)//SQUARE_SIZE

                        if sqSelected == (row, column):  # aynı kareye mi tıkladı
                            sqSelected = ()  # selecti boşalt
                            playerClicks = []  # tıklanan kareleri boşalt
                        else:
                            # tıklanırsa seçilen kareye atanıyor
                            sqSelected = (row, column)
                            playerClicks.append(sqSelected)

                        # 2.tıklamadan sonra 2 click atandıysa 1 noktadan diğerine geçilmek isteniyorsa moveu yapabiliriz
                        if len(playerClicks) == 2:
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gamestate.board)
                            gamestate.makeMove(move)
                            moveMade = False
                            sqSelected = ()  # selected reset
                            playerClicks = []  # clicked reset
                            
                            """
                            if not moveMade:
                                # o an seçili kareyi player clickine ata
                                playerClicks = [sqSelected]
                            """
                        
                        
                else:#customing bittiyse normale dön
                    #resignea tıklandı mı
                    if (location[0]>resignxl and location[0]<resignxr and location[1]>resignyt and location[1]<resignyb):
                        resigned=True

                    #restarta tıklandı mı?
                    if (location[0]>restartxl and location[0]<restartxr and location[1]>restartyt and location[1]<restartyb):
                        gamestate=ChessEngine.GameState()
                        validMoves=gamestate.getValidMoves()
                        sqSelected=()
                        playerClicks=[]
                        pieceCapturedListW=[]
                        pieceCapturedListB=[]
                        moveMade=False
                        gameOver=False
                        humanTurn=True
                        resigned=False
                        wValidMovesLen=[20,]
                        bValidMovesLen=[20,]
                        moveNumListw=[0,]
                        moveNumListb=[0,]    
                        pieceCapturedListW=[] #alınan taşları tutan liste 
                        pieceCapturedListB=[]   
                        resetMobility(screen,beginingMobilityPng)                    

                    if not gameOver and humanTurn :
                        #satranç tahtasına tıklandı mı?----------------------------------------------------------
                        if (location[0]>boardxl and location[0]<boardxr and location[1]>boardyt and location[1]<boardyb):

                            column=(location[0]-1000)//SQUARE_SIZE
                            row   =(location[1]-200)//SQUARE_SIZE
                            if sqSelected==(row,column):#aynı kareye mi tıkladı
                                sqSelected=()#selecti boşalt
                                playerClicks=[]#tıklanan kareleri boşalt
                            else :
                                sqSelected=(row,column)#tıklanırsa seçilen kareye atanıyor
                                playerClicks.append(sqSelected)

                            if len(playerClicks)==2:#2.tıklamadan sonra 2 click atandıysa 1 noktadan diğerine geçilmek isteniyorsa moveu yapabiliriz
                                move=ChessEngine.Move(playerClicks[0],playerClicks[1],gamestate.board)
                                pieceCaptured=move.pieceCaptured
                                print(move.getChessNotation())
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        gamestate.makeMove(validMoves[i])
                                        moveMade=True                  
                                        sqSelected=()#selected reset
                                        playerClicks=[]#clicked reset

                                if not moveMade:
                                    playerClicks=[sqSelected]#o an seçili kareyi player clickine ata
                    #--------------------------------------------------------------------------------------------------------------------------            
                        """
                        #bu yolla oyunu resetlersek çizimler doğru olmuyo
                        gamestate.restart()       
                        
                        sqSelected=()
                        playerClicks=[]
                        moveNumw=0
                        moveNumb=0
                    
                        validMoves=gamestate.getValidMoves()
                        wValidMovesLen=[20,]
                        bValidMovesLen=[20,]
                        moveNumListw=[0,]
                        moveNumListb=[0,]    
                        moveMade=False
                        """        
            #key handler--------------------------------------------------
            elif e.type==pygame.KEYDOWN:
                if e.key==pygame.K_z:#zye basıldığında hamleyi geri alır son hamleyi
                    gamestate.undoMove()
                    moveMade=True
            
        #Ai hamleleri-----------------------------------------
        if not gameOver and not humanTurn and not customing:  
            aiMove=AiMove.bestMove(gamestate,validMoves)
            if aiMove is None:
                aiMove=AiMove.moveRandomly(validMoves) 
            pieceCaptured=gamestate.makeMove(aiMove)           
            moveMade=True

        #hamle yapıldığında gerçekleşecek olanlar--------------------------------------------------------------
        if moveMade:   
            #bunlar alınan taşların tutulduğu liste ordan  kıyaslama yapıp ekrana bastırıyorum     
            if pieceCaptured[0]=="w" :
                pieceCapturedListW.append(pieceCaptured)    
            if pieceCaptured[0]=="b" :
                pieceCapturedListB.append(pieceCaptured)
                    
            #---------------------------------------------------
            #moblity çizmek için gerekenler-----------------------------------------------------------------    
            if gamestate.whiteToMove:
                moveNumw=moveNumw+1
                moveNumListw.append(moveNumw)
                wValidMovesLen.append(len(gamestate.getValidMoves()))
            else :
                moveNumb=moveNumw+1
                moveNumListb.append(moveNumb)
                bValidMovesLen.append(len(gamestate.getValidMoves()))

            #mobility çiz her hamlede-----------------------------  
            """
            mobilityplots.drawPlot(wValidMovesLen,bValidMovesLen,moveNumListw,moveNumListb)
            mobilityPng=pygame.image.load("Mobility.png")
            screen.blit(mobilityPng,(200,200))
            """
            
            
            #-------------------------------------------------------------------------------------------------        
            validMoves=gamestate.getValidMoves()
            moveMade=False
            
        drawGameState(screen,gamestate,validMoves,sqSelected,pieceCapturedListW,pieceCapturedListB)
        #oyun bitince ekranda yazı göster
        if gamestate.checkMate:
            gameOver=True
            if gamestate.whiteToMove:
                drawText(screen,"Black wins.","gray","black")
            else:
                drawText(screen,"White wins.","black","white")
        elif gamestate.staleMate:
            gameOver=True
            drawText(screen,"Stalemate.","black","black")
        if resigned==True:
            gameOver=True
            if gamestate.whiteToMove:
                drawText(screen,"Black Wins","white","black")
            else:
                drawText(screen,"White Wins","black","gray")
            
        pygame.display.flip()

#highlight yapacağız seçilen kareleri ve yapılabilecek hamlelerini
def highlightSquares(screen,gamestate,validMoves,sqSelected):
    
    if sqSelected != ():
        #print("SqSelectedDolu")
        r,c=sqSelected
        if gamestate.board[r][c][0] == ("w" if gamestate.whiteToMove else "b"):#seçilen kare oynanabilen bi yaş mı diye kontrol ettik
            #highlight seçilen kareyi
            highlight=pygame.Surface((SQUARE_SIZE,SQUARE_SIZE))
            highlight.set_alpha(150)#alpha 0 olursa görünmez 255 olursa altı hiç görünmez
            highlight.fill(pygame.Color("blue"))
            screen.blit(highlight,(1000+c*SQUARE_SIZE,200+r*SQUARE_SIZE))
            #gidebileceği kareleri highlightla
            highlight.fill(pygame.Color("red"))
            for move in validMoves:
                if move.startRow == r and move.startColumn == c:
                    screen.blit(highlight,(1000+move.endColumn*SQUARE_SIZE,200+move.endRow*SQUARE_SIZE))

#---------------------------------------------------------------
def loadImages():#imageleri images dictionarysine yüklüyoruz 
    pieces=["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK","bB","bN","bR"]
    for piece in pieces:
        IMAGES[piece]=pygame.transform.scale(pygame.image.load(f"{piece}.png"),(SQUARE_SIZE,SQUARE_SIZE))
    #istediğimiz imagee "IMAGES['wP'] ile ulaşabiliriz"        

#-----------------------------------------------------
def resetMobility(screen,beginingMobilityPng):
    screen.blit(beginingMobilityPng,(200,200))

#---------------------------------------------------------
def drawGameState(screen,gamestate,validMoves,sqSelected,pieceCapturedListW,pieceCapturedListB):#anlık oyun durumunu çizer
    drawBoard(screen,gamestate.board)#tahtayı çizer ekrana önce çağrılmalı çünkü tahtanın üstüne taşlar gelecek
    highlightSquares(screen,gamestate,validMoves,sqSelected)
    drawPieces(screen,gamestate.board)#önce taşları çizseydik görünmeyecekti
    drawCapturedArea(screen,pieceCapturedListW,pieceCapturedListB)

#-------------------------------------------------------------------
#sol üst ve sağ alt her zaman beyaz olur
#BURADA SCREENE BAĞLI OLANLARDA HATA VEREBİLİR
def drawBoard(screen,board):
    colors=[pygame.Color("red"),pygame.Color("blue")]
    for r in range(4,12):
        for c in range(20,28):
            color=colors[((r+c)%2)]#r+c den kalan 0sa beyaz 1 ise siyah olur
            pygame.draw.rect(screen,color,pygame.Rect(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
            piece=board[r-4][c-20]
            if piece != "..":#boş olup olmadığını kontrol ediyoruz taşın karesinin
                screen.blit(IMAGES[piece],pygame.Rect(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
    
#--------------------------------------------------------------------

def drawPieces(screen,board):
    for r in range(4,12):
        for c in range(20,28):
            piece=board[r-4][c-20]
            if piece != "..":#boş olup olmadığını kontrol ediyoruz taşın karesinin
                screen.blit(IMAGES[piece],pygame.Rect(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
                #blit karenin üzerine taşları yapıştırmak için kullanılıyor
#----------------------------------------------------------------------

def drawCapturedArea(screen,pieceCapturedListW,pieceCapturedListB):
    compareCapturedLists(pieceCapturedListW,pieceCapturedListB)
    pygame.draw.rect(screen,"Gray",pygame.Rect(1000,149,400,50))
    pygame.draw.rect(screen,"Gray",pygame.Rect(1000,601,400,50))
    
    for i in range(len(pieceCapturedListW)):
        screen.blit(IMAGES[pieceCapturedListW[i]],pygame.Rect(1000+(i*40),149,0,0))
    for i in range(len(pieceCapturedListB)):
        screen.blit(IMAGES[pieceCapturedListB[i]],pygame.Rect(1000+(i*40),601,0,0))
         
#-------------------------------------------------------------------------
                
def compareCapturedLists(pieceCapturedListW,pieceCapturedListB):
    #son alınan taşın renginin zıttı olan renk alınan taşları kıyaslayacağım
    if len(pieceCapturedListW)!=0 and len(pieceCapturedListB)!=0:
        lastPieceCapturedW=pieceCapturedListW[len(pieceCapturedListW)-1]
        lastPieceCapturedB=pieceCapturedListB[len(pieceCapturedListB)-1]
        
        for i in pieceCapturedListB:
            if (len(pieceCapturedListW)==0 or len(pieceCapturedListB)==0): break
            if lastPieceCapturedW[1]==i[1] :
                pieceCapturedListB.remove(i)
                if (f"w{i[1]}" in pieceCapturedListW): 
                    pieceCapturedListW.remove(f"w{i[1]}")
        
        for i in pieceCapturedListW:
            if (len(pieceCapturedListW)==0 or len(pieceCapturedListB)==0): break
            if lastPieceCapturedB[1]==i[1]:
                pieceCapturedListW.remove(i)
                if (f"b{i[1]}" in pieceCapturedListB): 
                    pieceCapturedListB.remove(f"b{i[1]}")
               
    """
    removed=False
    for i in range(len(wCapturedList)):
        for j in range(len(bCapturedList)):
            if len(wCapturedList)>i and len(bCapturedList)>i and len(wCapturedList)>j and len(bCapturedList)>j :
                if wCapturedList[i][1]==bCapturedList[j][1]:
                    wCapturedList.remove(wCapturedList[i])
                    bCapturedList.remove(bCapturedList[j])
                    removed=True
        if removed: break
    """              
#----------------------------------------------------------------------
def drawText(screen,text,colorBackground,colorWins):    
    font=pygame.font.SysFont("Helvitca",32,True,False)
    textObject=font.render(text,0,pygame.Color(colorBackground))
    textLocation=pygame.Rect(1150,400,0,0)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,0,pygame.Color(colorWins))
    screen.blit(textObject,textLocation.move(2,2))

if __name__=="__main__":

    main()
