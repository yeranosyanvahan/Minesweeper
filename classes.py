import numpy as np
import random
import time
import pygame
class Grid:
    def __init__(self,width,height):
        self.size=(width,height)
        self.clear()
        self.set_background_color((127,127,127))
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
        pygame.init()
        pygame.display.set_caption("MineSweeper")
        self.xmin, self.xmax = border, Width+border
        self.ymin, self.ymax = top_border, top_border+Height
        images=['empty','flag','Grid', 'grid1', 'grid2', 'grid3', 'grid4', 'grid5', 'grid6', 'grid7', 'grid8','mine','mineClicked','mineFalse','Transparent_grid']
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
        self.unitsize=(Width//Grid.size[0],Height//Grid.size[1])
        self.sprite={mapper[img]:
                     pygame.transform.scale(pygame.image.load(f"Sprites/{img}.png"),self.unitsize)
                     for img in images}
        self.Win=pygame.display.set_mode((self.xmax+border,self.ymax+border))
        
        Board_indeces=np.zeros((*self.Grid.size,(2)))
        for ix,x in enumerate(np.linspace(self.xmin,self.xmax-self.unitsize[0],self.Grid.size[0])):
            for iy,y in enumerate(np.linspace(self.ymin,self.ymax-self.unitsize[1],self.Grid.size[1])):
                Board_indeces[ix][iy]=np.array([x,y])
        self.Board_indeces=Board_indeces
        self.background_color=(0,0,0)
    def set_background_color(self,color):
        self.Win.fill(color)
        self.background_color=color
        
    def draw_board(self):
        drawboard = np.concatenate([self.Board_indeces,
                                    self.Grid.visible.reshape(*self.Grid.visible.shape,1),
                                    self.Grid.background], axis=-1)
        def mapper(sample):
            x,y=tuple(sample[:2])
            image=self.sprite[sample[2]]
            color=sample[3:]
            pygame.draw.rect(self.Win, color,pygame.Rect((x,y), self.unitsize))
            self.Win.blit(image,(x,y))

            
        list(map(mapper,drawboard.reshape(-1,drawboard.shape[-1])))
        pygame.display.update()
        
    def play(self):
       clock = pygame.time.Clock()
       run = True
       win = False
       self.Grid.boardcolorinit()
       while run:
        for event in pygame.event.get():
            clock.tick(60)
            if event.type == pygame.QUIT:
                run=False
                self.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                X,Y=event.pos
                X=((X-self.xmin))//self.unitsize[0]
                Y=((Y-self.ymin))//self.unitsize[1]
                if(X>=0 and X<self.Grid.size[0] and Y>=0 and Y<self.Grid.size[1]):
                     if event.button == 1: # left click
                         res = self.Grid.massclick((X,Y))
                         over,refresh = (res['over'],res['refresh'])
                         if(over):
                            run = False
                            win = res['win']
                            break
                         if(refresh):
                            self.Grid.update()
                            self.draw_board()

                     elif event.button == 3: # right click
                         refresh = self.Grid.rclick((X,Y))['refresh']
                         if(refresh):
                            self.draw_board()
       self.draw_board()
       if(win):
            self.drawtext("You Won. Press R to Restart or Q to quit")
       else:
            self.drawtext("You Lose. Press R to Restart or Q to quit")

        
       run = True
       while run:
            for event in pygame.event.get():
              if event.type == pygame.QUIT:
                run=False
                self.quit()
              if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        run=False
                        self.quit()
                    if event.key == pygame.K_r:
                        run=False
                        G=self.Grid.grid
                        self.Grid.generate(np.sum(G==-1)+np.sum(G==-9))
                        self.set_background_color(self.background_color)
                        self.draw_board()
                        self.play()
    def wait(self,sec):
        clock = pygame.time.Clock()
        for _ in range(sec*60):
         clock.tick(60)
         pygame.event.get()
            
    def quit(self):
        pygame.quit()
        
    def drawtext(self,txt, s=24):
        screen_text = pygame.font.SysFont("Calibri", s, True).render(txt, True, (0, 0, 0))
        rect = screen_text.get_rect()
        rect.center = ( (self.xmax+self.xmin)/2, self.ymin -12 )
        
        rect.width+=100
        rect.x-=50
        self.Win.fill(self.background_color,rect)
        
        rect.x+=50
        rect.width-=100
        self.Win.blit(screen_text, rect)
        
        pygame.display.update()
        