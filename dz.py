import pygame, random, json

pygame.init()

W,H=620,760
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("2048 Improved")
clock=pygame.time.Clock()

BOARD_X,BOARD_Y=40,170
BOARD_SIZE=540
CELL=BOARD_SIZE//4
SAVE="best_score.json"

BG=(250,248,239); TEXT=(119,110,101); BOARD=(187,173,160); WHITE=(255,255,255)
COLORS={0:(205,193,180),2:(238,228,218),4:(237,224,200),8:(242,177,121),16:(245,149,99),
32:(246,124,95),64:(246,94,59),128:(237,207,114),256:(237,204,97),512:(237,200,80),
1024:(237,197,63),2048:(237,194,46)}

title=pygame.font.SysFont("arial",56,True)
font=pygame.font.SysFont("arial",34,True)
small=pygame.font.SysFont("arial",24,True)

def load_best():
    try:
        with open(SAVE,"r") as f: return json.load(f)["best"]
    except: return 0

def save_best(v):
    with open(SAVE,"w") as f: json.dump({"best":v},f)

class Anim:
    def __init__(self,r,c):
        self.r=r; self.c=c; self.scale=0.1
    def update(self):
        self.scale=min(1.0,self.scale+0.08)

class Game:
    def __init__(self):
        self.best=load_best()
        self.state="menu"
        self.reset()

    def reset(self):
        self.score=0
        self.board=[[0]*4 for _ in range(4)]
        self.anims=[]
        self.add_tile(); self.add_tile()

    def add_tile(self):
        empty=[(r,c) for r in range(4) for c in range(4) if self.board[r][c]==0]
        if empty:
            r,c=random.choice(empty)
            self.board[r][c]=4 if random.random()<0.1 else 2
            self.anims.append(Anim(r,c))

    def can_move(self):
        for row in self.board:
            if 0 in row: return True
        for r in range(4):
            for c in range(4):
                if r<3 and self.board[r][c]==self.board[r+1][c]: return True
                if c<3 and self.board[r][c]==self.board[r][c+1]: return True
        return False

    def move_left(self,b):
        gain=0; out=[]
        for row in b:
            row=[x for x in row if x]
            i=0
            while i<len(row)-1:
                if row[i]==row[i+1]:
                    row[i]*=2; gain+=row[i]; row.pop(i+1)
                i+=1
            out.append(row+[0]*(4-len(row)))
        return out,gain

    def move(self,d):
        old=[r[:] for r in self.board]

        if d=="L":
            self.board,g=self.move_left(self.board)
        elif d=="R":
            b=[r[::-1] for r in self.board]
            b,g=self.move_left(b)
            self.board=[r[::-1] for r in b]
        elif d=="U":
            b=[list(x) for x in zip(*self.board)]
            b,g=self.move_left(b)
            self.board=[list(x) for x in zip(*b)]
        else:
            b=[list(x) for x in zip(*self.board)]
            b=[r[::-1] for r in b]
            b,g=self.move_left(b)
            b=[r[::-1] for r in b]
            self.board=[list(x) for x in zip(*b)]

        if self.board!=old:
            self.score+=g
            if self.score>self.best:
                self.best=self.score; save_best(self.best)
            self.add_tile()

        # Always check win/lose
        if any(2048 in row for row in self.board):
            self.state="win"
        elif not self.can_move():
            self.state="lose"

    def update(self):
        for a in self.anims[:]:
            a.update()
            if a.scale>=1:
                self.anims.remove(a)

    def draw(self):
        screen.fill(BG)
        screen.blit(title.render("2048",True,TEXT),(40,40))
        screen.blit(small.render(f"Score: {self.score}",True,TEXT),(350,40))
        screen.blit(small.render(f"Best: {self.best}",True,TEXT),(350,75))

        pygame.draw.rect(screen,BOARD,(BOARD_X,BOARD_Y,BOARD_SIZE,BOARD_SIZE),border_radius=10)

        for r in range(4):
            for c in range(4):
                v=self.board[r][c]
                x=BOARD_X+c*CELL+5; y=BOARD_Y+r*CELL+5; size=CELL-10

                scale=1.0
                for a in self.anims:
                    if a.r==r and a.c==c:
                        scale=a.scale

                ds=int(size*scale)
                rect=pygame.Rect(x+(size-ds)//2,y+(size-ds)//2,ds,ds)
                pygame.draw.rect(screen,COLORS.get(v,(60,60,60)),rect,border_radius=8)

                if v:
                    txt=font.render(str(v),True,TEXT)
                    screen.blit(txt,txt.get_rect(center=rect.center))

        if self.state in ("win","lose"):
            ov=pygame.Surface((W,H)); ov.set_alpha(180); ov.fill((0,0,0))
            screen.blit(ov,(0,0))
            msg="YOU WIN!" if self.state=="win" else "GAME OVER"
            screen.blit(title.render(msg,True,WHITE),
                        title.render(msg,True,WHITE).get_rect(center=(W//2,300)))
            self.btn=pygame.Rect(W//2-120,380,240,60)
            pygame.draw.rect(screen,(143,122,102),self.btn,border_radius=10)
            screen.blit(small.render("PLAY AGAIN",True,WHITE),
                        small.render("PLAY AGAIN",True,WHITE).get_rect(center=self.btn.center))

g=Game()
start=pygame.Rect(W//2-120,350,240,70)

run=True
while run:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type==pygame.QUIT: run=False

        if g.state=="menu":
            if e.type==pygame.MOUSEBUTTONDOWN and start.collidepoint(e.pos):
                g.state="game"

        elif g.state=="game":
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_LEFT: g.move("L")
                if e.key==pygame.K_RIGHT: g.move("R")
                if e.key==pygame.K_UP: g.move("U")
                if e.key==pygame.K_DOWN: g.move("D")

        elif g.state in ("win","lose"):
            if e.type==pygame.MOUSEBUTTONDOWN and g.btn.collidepoint(e.pos):
                g.reset(); g.state="game"

    g.update()

    if g.state=="menu":
        screen.fill(BG)
        screen.blit(title.render("2048",True,TEXT),
                    title.render("2048",True,TEXT).get_rect(center=(W//2,220)))
        pygame.draw.rect(screen,(143,122,102),start,border_radius=10)
        screen.blit(font.render("PLAY",True,WHITE),
                    font.render("PLAY",True,WHITE).get_rect(center=start.center))
    else:
        g.draw()

    pygame.display.flip()

pygame.quit()
