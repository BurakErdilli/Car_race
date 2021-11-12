import pygame
import time
import math
from utils import scale_image,blit_rotate_center,blit_text_center
pygame.font.init()

GRASS =  scale_image(pygame.image.load("assets/grass.jpg"),3)
TRACK = scale_image(pygame.image.load("assets/track.png"),0.9)
FINISH = scale_image(pygame.image.load("assets/finish.png"))
FINISH_POS=(130,250)
FINISH_MASK = pygame.mask.from_surface(FINISH)
RED_CAR = scale_image(pygame.image.load("assets/red-car.png"),0.55)
GREEN_CAR = scale_image(pygame.image.load("assets/green-car.png"),0.55)
BORDER= scale_image(pygame.image.load("assets/track-border.png"),0.9)
BORDER_MASK=pygame.mask.from_surface(BORDER)

width,height = TRACK.get_width(),TRACK.get_height()


WIN=pygame.display.set_mode((width,height))
pygame.display.set_caption("Racing Game! ")
PATH=[(186, 107), (142, 69), (37, 94), (39, 227), (37, 362), (123, 515), (185, 567), (239, 700), (290, 732), (373, 692), (404, 636), (402, 549), (437, 478), (516, 474), (603, 529), (608, 623), (594, 698), (646, 720), (719, 713), (749, 633), (744, 532), (757, 438), (695, 379), (540, 362), (414, 366), (424, 288), (477, 260), (621, 255), (718, 254), (757, 166), (731, 108), (624, 77), (499, 74), (410, 57), (350, 62), (296, 114), (270, 252), (296, 340), (231, 408), (150, 354), (158, 245), (154, 182)]
MAIN_FONT = pygame.font.SysFont("comicsans",44)

fps=165

class GameInfo:
    LEVELS=10
    def __init__(self,level=1):
        self.level=level
        self.started = False
        self.level_start_time=0

    def next_level(self):
        self.level+=1
        self.started=False

    def reset(self):
        self.level=1
        self.started=False
        self.level_start_time=0

    def game_finished(self):
        return  self.level> self.LEVELS

    def start_level(self):
        self.started=True
        self.level_start_time=time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time()-self.level_start_time,3)



class AbstractCar:

    def __init__(self,max_vel,rotation_vel):
        self.img=self.IMG
        self.max_vel=max_vel
        self.vel=0
        self.rotation_vel=rotation_vel
        self.angle=0
        self.x,self.y=self.start_pos
        self.acceleration=0.1


    def rotate(self,left=False,right=False):
        if left:
            self.angle+= self.rotation_vel

        elif right:
            self.angle-=self.rotation_vel

    def draw(self,win):
        blit_rotate_center(win,self.img,(self.x,self.y),self.angle)

    def move_forward(self):
        self.vel=min(self.vel + self.acceleration,self.max_vel)
        self.move()


    def reset(self):
        self.vel=0
        self.angle=0
        self.x,self.y=self.start_pos


    def move_backward(self):
        self.vel=max(self.vel - self.acceleration,-self.max_vel/2)
        self.move()

    def move(self):
        radians =  math.radians(self.angle)
        vertical = math.cos(radians)*self.vel
        horizontal = math.sin(radians)*self.vel

        self.y-=vertical
        self.x-=horizontal

    def collide(self,mask,x=0,y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset= (int(self.x - x), int(self.y -y))
        poi= mask.overlap(car_mask,offset)
        return poi



class ComputerCar(AbstractCar):
    IMG=GREEN_CAR
    start_pos =(150,200)
    def __init__(self,max_vel,rotation_vel,path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel=max_vel


    def draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win,(255,0,0),point,5)
    def next_level(self,level):
        self.reset()
        self.vel=self.max_vel+(level-1)*0.2
        self.current_point=0

        pass


    def draw(self,win):
        super().draw(win)

    def calculate_angle(self):
        target_x,target_y = self.path[self.current_point]
        x_diff= target_x-self.x
        y_diff=target_y-self.y
        if y_diff==0:
            comp_angle=math.pi/2
        else:
            comp_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            comp_angle+=math.pi

        diff_angle= self.angle-math.degrees(comp_angle)
        if diff_angle>=180:
            diff_angle-=360

        if diff_angle>0:
            self.angle-=min(self.rotation_vel,abs(diff_angle))

        else:
            self.angle+=min(self.rotation_vel,abs(diff_angle))

    def update_path_point(self):
        target=self.path[self.current_point]
        rect = pygame.Rect(self.x,self.y,self.IMG.get_width(),self.IMG.get_height())
        if rect.collidepoint(*target):
            self.current_point+=1



    def move(self):
        if self.current_point>=len(self.path):
            return
        self.calculate_angle()
        self.update_path_point()
        super().move()




class PlayerCar(AbstractCar):
    IMG = RED_CAR
    start_pos=(180,200)

    def collision(self):
        self.vel=-self.vel*0.1
        # self.angle+=math.pi/4
        self.move()


    def reduce_speed(self):
        if self.vel>self.max_vel:
            self.vel=max(self.vel-self.acceleration/10,self.max_vel)
            self.move()

        elif self.vel >0:
            self.vel=max(self.vel-self.acceleration/2 ,0)
            self.move()


        else:
            self.vel= min(self.vel + self.acceleration/2 ,0 )
            self.move()

    def boost_traction(self):
        if self.vel < self.max_vel*1.4:
            self.vel+=0.1

        self.move()


def draw(win,images,player_car,computer_car,game_info):
    for img,pos in images:
        win.blit(img,pos)

    level_text=MAIN_FONT.render(f"Level:{game_info.level}",1,(255,255,255))
    win.blit(level_text,(10,height-level_text.get_height()-70))
    time_text=MAIN_FONT.render(f"Time:{game_info.get_level_time()}s",1,(255,255,255))
    win.blit(time_text,(10,height-time_text.get_height()-40))
    vel_text=MAIN_FONT.render(f"Velocity:{round(player_car.vel,2)}px/s (%{round((100*player_car.vel)/player_car.max_vel,2)})",1,(255,255,255))
    win.blit(vel_text,(10,height-vel_text.get_height()-10))
    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def move_player(player_car):

    keys = pygame.key.get_pressed()
    moved = False
    drs = False
    if keys[pygame.K_a] and player_car.vel!=0 :
        player_car.rotate(left=True)
    if keys[pygame.K_d] and player_car.vel!=0:
        player_car.rotate(right=True)


    if keys[pygame.K_w]:
        if not keys[pygame.K_p]:

            player_car.move_forward()

        if keys[pygame.K_p]:
            player_car.boost_traction()
        moved=True



    if keys[pygame.K_s]:
        moved=True
        player_car.move_backward()


    if not drs:
        player_car.reduce_speed()
    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car,computer_car,game_info):
    if player_car.collide(BORDER_MASK)!= None:
        player_car.collision()

        print("exceeding track limits,will be added to laptime!")

    computer_finish_pio_collide = computer_car.collide(FINISH_MASK,*FINISH_POS)
    if computer_finish_pio_collide != None:
        blit_text_center(WIN,MAIN_FONT,"You Lost!")
        pygame.time.wait(9000)
        player_car.reset()
        computer_car.reset()

        print("Computer Won!")


    player_finish_pio_collide = player_car.collide(FINISH_MASK,*FINISH_POS)

    if player_finish_pio_collide!=None:
        if player_finish_pio_collide[1]==0:
            player_car.collision()

        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)
            print("You Won!")

run=True
clock = pygame.time.Clock()
images=[(GRASS,(0,0)),(TRACK,(0,0)),(FINISH,FINISH_POS),(BORDER,(0,0))]
player_car=PlayerCar(4,4)
computer_car=ComputerCar(1,10,PATH)
game_info=GameInfo()

# TODO player_car.max_vel+=drs_zone_speed also acc
while run:
    clock.tick(fps)
    draw(WIN,images,player_car,computer_car,game_info)
    while not game_info.started:
        blit_text_center(WIN,MAIN_FONT,f"Press any key to start level{game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            ex=pygame.key.get_pressed()
            if event.type == pygame.QUIT or ex[pygame.K_q]:
                pygame.quit()
                break

            if event.type==pygame.KEYDOWN:
                game_info.start_level()


    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
            break

        # if event.type==pygame.MOUSEBUTTONDOWN:
        #     pos = pygame.mouse.get_pos()
        #     computer_car.path.append(pos)
    move_player(player_car)
    computer_car.move()
    handle_collision(player_car,computer_car,game_info)
    if game_info.game_finished():
        blit_text_center(WIN,MAIN_FONT,"You Won The Championship!")
        pygame.display.update()
        pygame.time.wait(9000)
        player_car.reset()
        computer_car.reset()

pygame.quit()

