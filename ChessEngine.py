#şimdiki durum ile ilgili bütün bilgileri barındıran classımız
import datetime
import random
import time

class GameState():
    def __init__(self):
        #her karakter 2char kaplıyor sonradan refere edebilmek için
        #küçük harf rengini büyük harf türünü tutuyor normal satranç notasyonunda da öyle
        #iki nokta (..) boş kareleri temsil ediyor
        
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["..","..","..","..","..","..","..",".."],
            ["..","..","..","..","..","..","..",".."],
            ["..","..","..","..","..","..","..",".."],
            ["..","..","..","..","..","..","..",".."],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]

        self.moveFunctions={"P":self.getPawnMoves,"R":self.getRookMoves,"N":self.getKnightMoves,
                            "B":self.getBishopMoves,"Q":self.getQueenMoves,"K":self.getKingMoves}

        self.whiteToMove=True
        self.moveLog=[]
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False
        self.enpassantPossible=()#geçerken almanın mümkün olduğu kare 6. sıra olmalı
        self.currentCastlingRight=CastleRights(True,True,True,True)
        self.castleRightsLog=[CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]

    """ 
    def restart(self):
        self.startPosition=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["..","..","..","..","..","..","..",".."],
            ["..","..","..","..","..","..","..",".."],
            ["..","..","..","..","..","..","..",".."],
            ["..","..","..","..","..","..","..",".."],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        
        
        self.board=self.startPosition
        self.whiteToMove=True
        self.moveLog=[]
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False
        self.enpassantPossible=()
        self.currentCastlingRight=CastleRights(True,True,True,True)
        self.castleRightsLog=[CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]
    """ 
    #BU FONSKİYON SON ALINAN TAŞI DÖNDÜRÜYOR!!!
    #bir hamle alır parametre olarak ancak rok ve geçerken almak (en passant) kuralları için geçerli değil
    def makeMove(self,move):
        self.board[move.startRow][move.startColumn]=".."
        self.lastPieceCaptured=self.board[move.endRow][move.endColumn]#on karenin içeriği değişmeden o karedeki taşı tutuyorum yenilenleri yazacağım için
        self.board[move.endRow][move.endColumn]=move.pieceMoved
        #BURAYA BOŞ KARELERE TIKLANDIĞINDA MOVELOGA KAYDETMESİN
        #if self.board[move.startRow][move.startColumn] != "..":#didnt worked
        self.moveLog.append(move)#loga moveu kaydetmek
        self.whiteToMove=not self.whiteToMove#siyaha geçirecek sırayı
        #şahın konumunu güncelle 
        if move.pieceMoved=="wK":
            self.whiteKingLocation=(move.endRow,move.endColumn)
        elif move.pieceMoved=="bK":
            self.blackKingLocation=(move.endRow,move.endColumn)
        
        #piyon promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn]=move.pieceMoved[0]+"Q"

        #enpassant geçerken alma
        if move.isEnpassantMove:
            self.board[move.startRow][move.endColumn]=".."#piyonu alıyor
        #* move.endColumn
        #updating enpassantPossible variable
        if move.pieceMoved[1]=="P" and abs(move.startRow - move.endRow)==2:
            self.enpassantPossible=((move.startRow + move.endRow)//2,move.endColumn)
        else:
            self.enpassantPossible=()

        #castle move
        if move.isCastleMove:
            if move.endColumn-move.startColumn==2:#şah kanadı roku (kısa rok)
                self.board[move.endRow][move.endColumn-1] = self.board[move.endRow][move.endColumn+1]#kaleyi taşı yeni karesine şahın yanına
                self.board[move.endRow][move.endColumn+1] = ".."#eski kale karesini boşalt
            else:#queenside castle(uzun rok)
                self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-2]
                self.board[move.endRow][move.endColumn-2] = ".."


        #update castling rigts-ne zaman kale ya da şah oynarsa güncellemeliyiz
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))
        
        return self.lastPieceCaptured

    #yapılan son hamleyi geri almak---------------------------------
    def undoMove(self): 
        if len(self.moveLog)!=0:#geri alınacak bi hamle olmalı
            move=self.moveLog.pop()#son hamleyi çıkarmak
            self.board[move.startRow][move.startColumn]=move.pieceMoved
            self.board[move.endRow][move.endColumn]=move.pieceCaptured
            self.whiteToMove=not self.whiteToMove #sıra siyahta
            #şahın konumunu tekrar güncelle
            if move.pieceMoved=="wK":
                self.whiteKingLocation=(move.startRow,move.startColumn)
            elif move.pieceMoved=="bK":
                self.blackKingLocation=(move.startRow,move.startColumn)
            
            #undo geçerken alma
            if move.isEnpassantMove:
                self.board[move.endRow][move.endColumn]=".."#ayrıldığın kareyi boşaltıyor
                self.board[move.startRow][move.endColumn]=move.pieceCaptured
                self.enpassantPossible=(move.endRow,move.endColumn)
            
            #undo 2 kare piyon hamlesi
            if move.pieceMoved[1]=="P" and abs(move.startRow-move.endRow)==2:
                self.enpassantPossible=()

            #undo rok hakları
            self.castleRightsLog.pop()#geri aldığımız hamlelerden gelen yeni hakları siliyoruz listeden
            newRights=self.castleRightsLog[-1]#listenin son elemanına current rok hakkını atıyoruz
            self.currentCastlingRight=CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)
            #undo castle move
            if move.isCastleMove:
                if move.endColumn-move.startColumn == 2:#kingside kısa rok
                    self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-1]
                    self.board[move.endRow][move.endColumn-1] = ".."
                
                else:#uzun rok
                    self.board[move.endRow][move.endColumn-2] = self.board[move.endRow][move.endColumn+1]
                    self.board[move.endRow][move.endColumn+1] = ".."
            
            #buraya çizilen capturedları silmeyi de yapmamız lazım 
            
            self.checkMate=False
            self.staleMate=False

    def updateCastleRights(self,move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks=False
            self.currentCastlingRight.wqs=False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks=False
            self.currentCastlingRight.bqs=False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startColumn==0:#soldaki kale
                    self.currentCastlingRight.wqs=False
                elif move.startColumn==7:#sağdaki kale
                    self.currentCastlingRight.wks=False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startColumn==0:#soldaki kale
                    self.currentCastlingRight.bqs=False
                elif move.startColumn==7:#sağdaki kale
                    self.currentCastlingRight.bks=False

    #checks dair tüm hamleler açarak şah olduğu için şahın önündeki taşı oynatamazsın
    def getValidMoves(self):
        tempEnpassantPossible=self.enpassantPossible
        tempCastleRights=CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                      self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)

        #AÇMAZ kontrolü için------------------------------
        #1.bütün mümkün hamleleri oluştur
        moves=self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)

        #2.her hamle için karşı hamleyi yap
        for i in range(len(moves)-1,-1,-1):#listeden eleman silerken sondan başlıyoruz
            self.makeMove(moves[i])#beyaz hamlesini yaptı*
            #3.bütün düşman hamlelerini oluştur
            #4.her bir düşman hamlesi için şaha atak var mı bak
            self.whiteToMove=not self.whiteToMove#tekrar sırayı değştirdik
            if self.inCheck():
                moves.remove(moves[i])#burada sıra tekrar değişeceği için eğer yukarıda sırayı değişmezsek kendi şah karesine değiş düşmanın şah karesine olabilecek olan saldırıları kontrol etmiş oluruz ki saçma olur çünkü hamleyi yapacak olan düşman o yüzden kendi şah karemize olabilecek saldırılara bakmalıyız**
                #5.eğer varsa şaha atak validMove'dan sil        
            self.whiteToMove=not self.whiteToMove#tekrar sırayı değştirdik
            self.undoMove()
        if len(moves)==0:#şah mat veya pat durumu
            if self.inCheck():
                self.checkMate=True
            else:
                self.staleMate=True
        else:#hamleni geri aldığında tekrar false yapıyoruz ki tekrar oynanabilsin
            self.checkMate=False
            self.staleMate=False
        
        self.enpassantPossible=tempEnpassantPossible
        self.currentCastlingRight=tempCastleRights
        return moves

    #checkler olmadan tüm hamleler açarak şah kontrol edilmiyor
    def getAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):#number of rows
            for c in range(len(self.board[r])):#number of columns in perticular row
                turn=self.board[r][c][0] 
                if (turn =="w" and self.whiteToMove) or (turn=="b" and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    #i will use this
                    self.moveFunctions[piece](r,c,moves)
                    """#instead of doing this 
                    if piece=="P":
                        self.getPawnMoves(r,c,moves)
                    elif piece=="R":
                        self.getRookMoves(r,c,moves)
                    """
        return moves                
    
    #oyuncu şah çekilme durumunda mı
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])

    #düşman r,c karesine saldırabiliyor mu r,c şahın bulunduğu kare olacak
    def squareUnderAttack(self,r,c):
        self.whiteToMove=not self.whiteToMove #düşmanı değiştir düşmanın açısından bakmak gerkecek
        opponentsMoves=self.getAllPossibleMoves()#o düşmana göre olası hamleleri aldık
        self.whiteToMove=not self.whiteToMove#düşmanı tekrar değiştik
        for move in opponentsMoves:
            if move.endRow==r and move.endColumn==c:#kare atakta
                return True#kare ataktaysa True döndürdük
        return False#değişse false döndürdük

    #taş türüne göre hamle izin fonksiyonları başlangıcı-------------------------------
    #row,column'da konumlanmış olan piyonun bütün yapabileceği hamleeler,listeye eklenecek 
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:#beyaz piyonlar için
            if self.board[r-1][c]=="..":#bir önündeki kare boş mu
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c]=="..":#2 kare ilerleme durumu
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1>=0:#soldakini alır solda kare var mı diye checkledik ifte
                if self.board[r-1][c-1][0]=="b":#alınacak rakip taş sol üst köşe
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnpassantMove=True))

            if c+1<= 7:#sağdakini alır,sağdaki kare sınırını kontrol ettik yine
                if self.board[r-1][c+1][0]=="b":#beyazın düşmanı
                    moves.append(Move((r,c),(r-1,c+1),self.board))#sağ üst
                elif (r-1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnpassantMove=True))

        else:#siyah piyonların hamleleri
            
            if self.board[r+1][c]=="..":#1 adım siyah
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="..":#2adım siyah
                    moves.append(Move((r,c),(r+2,c),self.board))
                
            #alma
            if c-1>=0:
                if self.board[r+1][c-1][0]=="w":#ön sağ taş düşman mı
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnpassantMove=True))

            if c+1<=7:
                if self.board[r+1][c+1][0]=="w":
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantMove=True))

        #piyon son kareye gelince istediği taşa dönüşebilmeyi ekle
    #aynı şeyleri kale için
    def getRookMoves(self,r,c,moves):
        directions=((-1,0),(0,-1),(1,0),(0,1))#up left down right
        enemyColor="b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endColumn=c+d[1]*i
                if 0<= endRow <8 and 0 <= endColumn <8: #tahta sınırlarını çizdik
                    endPiece=self.board[endRow][endColumn]
                    if endPiece=="..":
                        #boşluksa gidebiliriz o kareye
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                    elif endPiece[0]==enemyColor:
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                        break#taşa çarptık düşmansa alabiliriz
                    else:#kendi taşımız
                        break
                else:#tahta dışında 
                    break
    #tek önemli olan varış noktasındaki taş.Kendi takım arkadaşının taşı ise gidemez
    def getKnightMoves(self,r,c,moves):
        knightMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,2),(1,-2),(2,-1),(2,1))
        allyColor="w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow=r+m[0]
            endColumn=c+m[1]
            if 0 <= endRow <8 and 0<=endColumn <8:
                endPiece=self.board[endRow][endColumn]
                if endPiece[0] != allyColor:#kendi takım arkadaşı değil
                    moves.append(Move((r,c),(endRow,endColumn),self.board))
    #kaleyle aynı şey yalnızca directions değişiyor----------------------------------
    def getBishopMoves(self,r,c,moves):
        directions=((-1,-1),(-1,1),(1,-1),(1,1))#çaprazların yönleri
        enemyColor="b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endColumn=c+d[1]*i
                if 0<= endRow <8 and 0 <= endColumn <8: #tahta sınırlarını çizdik
                    endPiece=self.board[endRow][endColumn]
                    if endPiece=="..":
                        #boşluksa gidebiliriz o kareye
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                    elif endPiece[0]==enemyColor:
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                        break#taşa çarptık düşmansa alabiliriz
                    else:#kendi taşımız
                        break
                else:#tahta dışında 
                    break
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
    def getKingMoves(self,r,c,moves):
        kingMoves=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor="w" if self.whiteToMove else "b"
        for i in range(8):
            endRow=r+kingMoves[i][0]
            endColumn=c+kingMoves[i][1]
            if 0 <= endRow <8 and 0<=endColumn<8:
                endPiece=self.board[endRow][endColumn]
                if endPiece[0] != allyColor:#kendi rengini checkliyor kendi rengi dışındaki yere gidebilir ata benzer
                    moves.append(Move((r,c),(endRow,endColumn),self.board))
        
    #yapılmasına izin verilen bütün rok hamlelerini al ancak r,c konumundaki şah için
    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return #şah çekildiyse rok yapamayız
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves)

    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]==".." and self.board[r][c+2]=="..":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))

    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1]==".." and self.board[r][c-2]==".." and self.board[r][c-3]:
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))
    #taş türüne göre hamle izin fonksiyonları sonu---------------------------------------------------------------
    
    """
    def playRandom(self):
        moves=self.getValidMoves()
        
        if(len(moves)>0):
            self.makeMove(moves[random.randint(0,len(moves)-1)])
        else:
            if(self.whiteToMove and self.inCheck()):
                print("Siyah kazandı.")
            elif(not self.whiteToMove and self.inCheck()):
                print("Beyaz kazandı.")
            else:
                print("Berabere.")     
        moveMade=True
    """
#---------------------------------------------
class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):#olası 4 rok parametre
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs

class Move():
    #burada tahtanın kenarındaki sayıları ve harfleri value key dictionary yöntemiyle eşleştiriyoruz
    #notasyon için
    ranksToRows={"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks={value:key for key,value in ranksToRows.items()}
    
    filesToColumns={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    columnsToFiles={value:key for key,value in filesToColumns.items()}
    
    def __init__(self,startSq,endSq,board,isEnpassantMove=False,isCastleMove=False,):
        self.startRow=startSq[0]
        self.startColumn=startSq[1]
        self.endRow=endSq[0]
        self.endColumn=endSq[1]
        self.board=board
        self.pieceMoved=board[self.startRow][self.startColumn]
        self.pieceCaptured=board[self.endRow][self.endColumn]
        
        #vezir yapmak
        self.isPawnPromotion=(self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved=="bP" and self.endRow== 7)
        #geçerken almak
        self.isEnpassantMove=isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured="wP" if self.pieceMoved =="bP" else "bP"
        #rok atma
        self.isCastleMove=isCastleMove

        self.moveID=self.startRow*1000+self.startColumn*100+self.endRow*10+self.endColumn
        #moveID hamleye eşsiz bir id verir ve her hamle için farklı olur
        
    #overriding the equals method
    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False
        
    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startColumn)+self.getRankFile(self.endRow,self.endColumn)

    def getRankFile(self,r,c):
        return self.columnsToFiles[c] + self.rowsToRanks[r]

