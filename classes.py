import numpy as np
import random
import time
import pygame
from PIL import Image
class Grid:
    def __init__(self,width,height):
        self.size=(width,height)
        self.clear()
        self.set_background_color((127,127,127))
        self.shape=(width,height)
    def update(self):
        pass
    # Get neighbors of a cell
    def neighbors(self,positions):
        positions=np.array(positions)
        stack=[]
        for addx in range(-1,2,1):
            for addy in range(-1,2,1):
                if(addx!=0 or addy !=0):
                    stack.append(positions+np.array([addx,addy]))
                
        stack = np.vstack(stack)
        X=stack.T[0]
        stack=stack[np.logical_and(X>=0, X<=self.size[0]-1)]
        Y=stack.T[1]
        stack=stack[np.logical_and(Y>=0, Y<=self.size[1]-1)]
        return stack
    
    def reset(self):
        self.visible=np.zeros(self.size,dtype=np.int8)+9
    
    def rclick(self,position):
        clicked=self.visible[position]
        if(clicked==9):
            self.visible[position]=-5
            return {'refresh':True}
        elif(clicked==-5):
            self.visible[position]=9
            return {'refresh':True}
        return {'refresh':False}

    def iswin(self):
        G=self.grid
        V=self.visible
        known=sum(V[V>=0])-sum(V[V==9])
        if(sum(G[G!=-1])==known):
            return True
        return False
    def lclick(self,position):
        self.massclick([position])
#         position=tuple(position)
#         if(self.visible[position]!=9):
#             return {'over':False,'refresh':False}
#         clicked=self.grid[position]
#         self.visible[position]=clicked
#         if(clicked==-1):
#             self.visible=self.grid
#             self.visible[position]=-9
#             return {'over':True,'win':False,'refresh':True}
#         elif(clicked==0):
#             neighbors=self.neighbors([position])
#             neighbors=neighbors[self.visible[tuple(neighbors.T)]==9]
#             [self.lclick(n) for n in neighbors]
#         if(self.iswin()):
#             return {'over':True,'win':True,'refresh':True}
#         return {'over':False,'refresh':True}
    # Put bombs in random locations
    def set_background_color(self,color):
        self.background = np.zeros((*self.grid.shape,(len(color))), dtype=np.uint8)+np.array(color)
    def randomize(self,n_bombs):
        sample= random.sample(range(self.size[0]*self.size[1]),n_bombs)
        grid=self.grid.reshape(-1)
        grid[sample]=-1
        self.grid=grid.reshape(self.size)
    # Generate the grid to play
    def clear(self):
        self.grid=np.zeros(self.size,dtype=np.int8)
        self.visible=np.zeros(self.size,dtype=np.int8)+9
    def generate(self,n_bombs):
        self.clear()
        self.randomize(n_bombs)
        stack=[]
        G=self.grid
        Bombs=np.argwhere(G==-1)
        stack=self.neighbors(Bombs)
        stack=stack[G[tuple(stack.T)]!=-1]
        for s in stack:
            G[tuple(s)]+=1
        self.grid=G
        
    def massclick(self,positions):
        positions=np.array(positions)
        visible_values=self.visible[tuple(positions.T)]
        positions = positions[visible_values==9]
        actual_values = self.grid[tuple(positions.T)]
        if(len(actual_values)==0):
            return {'over':False,'refresh':False}
        self.visible[tuple(positions.T)] = self.grid[tuple(positions.T)]
        positioning={-1:tuple(positions[actual_values==-1].T),
                      0:tuple(positions[actual_values==0].T)}
        
        if(-1 in actual_values):
            self.visible=self.grid
            self.visible[positioning[-1]]=-9
            return {'over':True,'win':False,'refresh':True}

        if(0 in actual_values):
            neighbors=self.neighbors(positions[actual_values==0])
            neighbors=np.unique(neighbors,axis=0)
            self.massclick(neighbors)
            
        if(self.iswin()):
            return {'over':True,'win':True,'refresh':True}
        return {'over':False,'refresh':True}   
    
class Game:
    def __init__(self,Grid,Width=900,Height=500,border=10,top_border=20):
        self.Grid=Grid
        self.visible=Grid.visible
        
        self.xmin, self.xmax = border, Width+border
        self.ymin, self.ymax = top_border, top_border+Height
        self.unitsize=np.array([Width/Grid.size[0],Height/Grid.size[1]])
        self.Width, self.Height = Width, Height
        self.Size=(Width,Height)
        self.border=border
        
        mapper={ 
                 'empty':0,
                 'Grid':-999,
                 'Transparent_grid':9,
                 'flag':-5,
                 'grid1': 1,
                 'grid2': 2,
                 'grid3': 3,
                 'grid4': 4,
                 'grid5': 5,
                 'grid6': 6,
                 'grid7': 7,
                 'grid8': 8,
                 'mine': -1,
                 'mineClicked':-9,
                 'mineFalse':-99
               }

        self.sprite={mapper[img]: 
         np.asarray(Image.open(f"Sprites/{img}.png"))
         for img in mapper.keys()}        
        
        self.background_color=(0,0,0)
        
    def set_background_color(self,color):
        self.background_color=color
        
    def numpy_to_pygame_surface(array,resize=None):
        img=Image.fromarray(array)
        surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        if(resize):
            surface=pygame.transform.scale(surface,resize)
        return surface
    
    def draw_board(self):
        G=self.Grid.visible
        sprite=self.sprite
        
        IMGS=np.vstack([np.hstack([
            sprite[G[i][j]]
            for i in range(G.shape[0])]) for j in range(G.shape[1])])
        surface=Game.numpy_to_pygame_surface(IMGS,self.Size)
        
        background=self.Grid.background.astype(np.uint8)
        background=Game.numpy_to_pygame_surface(background,self.Size[::-1])
        background=pygame.transform.rotate(background,270)
        background=pygame.transform.flip(background, 1, 0)
            
        self.Win.blit(background,(self.xmin,self.ymin))
        self.Win.blit(surface,(self.xmin,self.ymin))
        pygame.display.update()
        
    def play(self):
       pygame.init()
       pygame.display.set_caption("MineSweeper")
       self.Win=pygame.display.set_mode((self.xmax+self.border,self.ymax+self.border))
       self.Win.fill(self.background_color)
        
       clock = pygame.time.Clock()
       run, refresh, win, over = True, False, False, False
       self.Grid.boardcolorinit()
       self.draw_board()
       while run:
        for event in pygame.event.get():
            clock.tick(60)
            # Check If quitted or pressed a key
            if event.type == pygame.QUIT:
                run=False
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run=False
                    pygame.quit()
                    break
                if event.key == pygame.K_r:
                    G=self.Grid.grid
                    self.Win.fill(self.background_color)
                    self.Grid.generate(np.sum(G==-1)+np.sum(G==-9))
                    self.Grid.boardcolorinit()
                    self.draw_board()
                    
            #Get the position of the mouse and convert it to grid coordinates
            XY=np.array(pygame.mouse.get_pos())-np.array([self.xmin,self.ymin])
            X,Y=(XY//self.unitsize).astype(int)
            # Check if X or Y overflow
            if(self.Grid.size[0]>X>=0 and self.Grid.size[1]>Y>=0):    
            # Check if positioned at a unopened grid
             if(self.Grid.visible[X,Y]!=9):
                self.drawtext("",n=1)    
             else:
                P=self.Grid.Probspace[X,Y]
                if(P==-1):  self.drawtext("???",n=1)  
                elif(P==1): self.drawtext("BOMB!",n=1) 
                elif(P==0): self.drawtext("safe",n=1)
                else:       self.drawtext(f"P:{str(round(P, 2))}",n=1)
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: # left click
                         res = self.Grid.massclick((X,Y))
                         over,refresh = (res['over'],res['refresh'])
                         if(over):
                            win = "Won" if res['win'] else "Loose"
                            self.drawtext(f"You {win}. Press R to Restart or Q to quit")
                            self.draw_board()
                            break
                         if(refresh):
                            self.Grid.update()
                            self.draw_board()
                            self.drawtext(f"Ncomb:{self.Grid.Poss}",n=1,x=0)
                            

                    elif event.button == 3: # right click
                         refresh = self.Grid.rclick((X,Y))['refresh']
                         if(refresh):
                            self.draw_board()
        
    def drawtext(self,txt,n=2, s=24, x=None):
        screen_text = pygame.font.SysFont("Calibri", s, True).render(txt, True, (0, 0, 0))
        rect = screen_text.get_rect()
        rect.center = ( (self.xmax+self.xmin)/2, n*24-12)

        if(x!=None):
            rect.x=x
        rect.width+=300
        rect.x-=150
        self.Win.fill(self.background_color,rect)
        
        rect.x+=150
        rect.width-=300
        self.Win.blit(screen_text, rect)
        
        pygame.display.update()
        