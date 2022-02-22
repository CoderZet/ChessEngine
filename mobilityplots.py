import matplotlib.pyplot as plt 

def drawPlot(white,black,moveNumListw,moveNumListb):
    x=len(moveNumListw)
    plt.plot(moveNumListw,white,"o-b",label="White")#bu çizgiyi beyaz yapmayı öğren
    plt.plot(moveNumListb,black,"o-k",label="Black")
    plt.axis([0,x,0,60]) #bu lazım kaçıncı hamle

    plt.title("Mobility")
    plt.xlabel("Move Number")
    plt.ylabel("Valid Moves Number")


    #plt.legend()
    plt.savefig("Mobility.png",dpi=85)

    #plt.show()
    

        


