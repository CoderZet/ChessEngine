

class Button():

    def __init__(self,screen,x,y,image):
        self.screen=screen
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.topleft=(x,y)
    
    def draw(self):
        #draw button on screen
        self.screen.blit(self.image,(self.rect.x,self.rect.y))


