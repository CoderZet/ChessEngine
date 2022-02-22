import random

pieceScore={"K":100,"Q":9,"R":5,"B":3,"N":3,"P":1}

knightBetterPosition=[[1, 1, 1, 1, 1, 1, 1, 1],
                      [1, 2, 2, 2, 2, 2, 2, 1],
                      [1, 2, 3, 3, 3, 3, 2, 1],
                      [1, 2, 3, 4, 4, 3, 2, 1],
                      [1, 2, 3, 4, 4, 3, 2, 1],
                      [1, 2, 3, 3, 3, 3, 2, 1],
                      [1, 2, 2, 2, 2, 2, 2, 1],
                      [1, 1, 1, 1, 1, 1, 1, 1]]

bishopBetterPosition=[[4, 3, 2, 1, 1, 2, 3, 4],
                      [3, 4, 3, 2, 2, 3, 4, 3],
                      [2, 3, 4, 3, 3, 4, 3, 2],
                      [1, 2, 3, 4, 4, 3, 2, 1],
                      [1, 2, 3, 4, 4, 3, 2, 1],
                      [2, 3, 4, 3, 3, 4, 3, 2],
                      [3, 4, 3, 2, 2, 3, 4, 3],
                      [4, 3, 2, 1, 1, 2, 3, 4]]

blackPawnBetterPosition=[[0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 1, 1, 0, 0, 1, 1, 1],
                         [1, 1, 1, 3, 3, 1, 1, 1],
                         [1, 1, 1, 4, 4, 1, 1, 1],
                         [2, 3, 3, 5, 5, 3, 3, 2],
                         [5, 6, 6, 7, 7, 6, 6, 5],
                         [8, 8, 8, 8, 8, 8, 8, 8],
                         [8, 8, 8, 8, 8, 8, 8, 8],]

whitePawnBetterPosition=[[8, 8, 8, 8, 8, 8, 8, 8],
                         [8, 8, 8, 8, 8, 8, 8, 8],
                         [5, 6, 6, 7, 7, 6, 6, 5],
                         [2, 3, 3, 5, 5, 3, 3, 2],
                         [1, 1, 1, 4, 4, 1, 1, 1],
                         [1, 1, 1, 3, 3, 1, 1, 1],
                         [1, 1, 1, 0, 0, 1, 1, 1],
                         [0, 0, 0, 0, 0, 0, 0, 0],]

kingBetterPosition=[[1, 1, 6, 1, 5, 1, 7, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 6, 1, 5, 1, 7, 1]]

piecePositionalScores={"N":knightBetterPosition, "B":bishopBetterPosition,"bP":blackPawnBetterPosition,"wP":whitePawnBetterPosition,"K":kingBetterPosition}

CheckMate=1000
StaleMate=0
Depth=4

def scoreBoard(gs):#sadece taş puanlarına göre bakıyo piyonların ve taşların pozisyonlarına göre kıyaslama yaptırmalıyız
    if gs.checkMate:
        if gs.whiteToMove:
            return -CheckMate
        else:
            return CheckMate
    elif gs.staleMate:
        return StaleMate
    
    score=0
    for r in range(len(gs.board)):
        for c in range(len(gs.board[r])):
            square=gs.board[r][c]
            if square!="..":
                piecePositionalScore=0
                #pozisyon puanlarına da bakacağız
                if square[1]!="R" and square[1]!="Q":#bunlar için better pozisyon hazırlamadım
                    if square[1]=="P":#piyonlar içiin
                        piecePositionalScore=piecePositionalScores[square][r][c]
                    else:#diğer taşlar için
                        piecePositionalScore=piecePositionalScores[square[1]][r][c]
                
                if square[0]=="w":
                    score+=pieceScore[square[1]]+piecePositionalScore *.1
                elif square[0]=="b":
                    score-=pieceScore[square[1]]+piecePositionalScore *.1
    return score


#helper method for algorithms-----------------------------------------
def bestMove(gs,validMoves):
    global nextMove
    nextMove=None
    random.shuffle(validMoves)
    #miniMaxMove(gs,validMoves,Depth,gs.whiteToMove)
    #negaMaxMove(gs,validMoves,Depth ,1 if gs.whiteToMove else -1)
    #openingMoves(lastmove)
    negaMaxAlphaBetaMove(gs,validMoves,Depth,-CheckMate,CheckMate,1 if gs.whiteToMove else -1)#-CheckMate ve CheckMate aslında +sonsuz - sonsuz gibi düşünülebilir hiç ulaşılamayacak değerler
    return nextMove

def miniMaxMove(gs,validMoves,depth,whiteToMove):
    global nextMove
    if depth==0:
        return scoreBoard(gs)
    
    if whiteToMove:
        maxScore=-CheckMate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves=gs.getValidMoves()
            score=miniMaxMove(gs,nextMoves,depth-1,False)
            if score>maxScore:
                maxScore=score
                if depth==Depth:
                    nextMove=move
            gs.undoMove()
        return maxScore
    else:
        minScore=CheckMate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves=gs.getValidMoves()
            score=miniMaxMove(gs,nextMoves,depth-1,True)
            if score<minScore:
                minScore=score
                if depth==Depth:
                    nextMove=move
            gs.undoMove()
        return minScore

#negamax-----------------------------------------
def negaMaxMove(gs,validMoves,depth,sign):
    global nextMove
    if depth==0:
        return sign*scoreBoard(gs)
    
    maxScore=-CheckMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves=gs.getValidMoves()
        score= -negaMaxMove(gs,nextMoves, depth-1, -sign) #buradaki - önemli. 
        if score>maxScore:
            maxScore=score
            if depth==Depth:
                nextMove=move
        gs.undoMove()
    return maxScore

def negaMaxAlphaBetaMove(gs,validMoves,depth,alpha,beta,sign):
    global nextMove
    if depth==0:
        return sign*scoreBoard(gs)
    
    #move ordering eklenebilir sonradan

    maxScore=-CheckMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves=gs.getValidMoves()
        score= -negaMaxAlphaBetaMove(gs,nextMoves, depth-1,-beta,-alpha,-sign) #alpha ve beta burada değişiyor 
        if score>maxScore:
            maxScore=score
            if depth==Depth:
                nextMove=move
        gs.undoMove()
        if maxScore>alpha:#kesme kısmı
            alpha=maxScore
        
        if alpha>=beta:#eğer alpha betayı geçerse veya beta alphayı geçerse buduyoruz
            break

    return maxScore


def moveRandomly(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]
