import pygame
from settings import *
from utility import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack):
        super().__init__(groups)
        self.image=pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)
        self.hitbox=self.rect.inflate(-35,-26) #set hitbox within image instead of rectangle

        #graphics
        self.import_player_assets()
        self.status='down'
        self.frame_index=0
        self.animation_speed=0.15

        #movement
        self.direction=pygame.math.Vector2()
        self.attacking=False
        self.attack_cd=400
        self.attack_duration=None

        #weapon
        self.create_attack=create_attack
        self.destroy_attack=destroy_attack
        self.weapon_index=0 # id of weapon
        self.weapon=list(weapon_data.keys())[self.weapon_index]
        self.can_switch_sweapon=True
        self.weapon_switch_cd=None
        self.switch_duration_cd=200

        #stats
        self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 6}
        self.health=self.stats['health']
        self.energy=self.stats['energy']
        self.xp=696
        self.speed=self.stats['speed']

        self.obstacle_sprites=obstacle_sprites

    def import_player_assets(self):
        character_path='../graphics/player/'
        self.animations = {'up':[],'down':[],'left':[],'right':[],
                           'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
                           'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}
        for animation in self.animations.keys():
            full_path=character_path+animation
            self.animations[animation]=import_folder(full_path)

    def input(self):
        if not self.attacking:
            keys=pygame.key.get_pressed()

            #movement input
            if keys[pygame.K_w]:
                self.direction.y=-1
                self.status='up'
            elif keys[pygame.K_s]:
                self.direction.y=1
                self.status='down'
            else:
                self.direction.y=0
            
            if keys[pygame.K_a]:
                self.direction.x=-1
                self.status='left'
            elif keys[pygame.K_d]:
                self.direction.x=1
                self.status='right'
            else:
                self.direction.x=0

            #attack input
            if keys[pygame.K_SPACE]:
                self.attacking=True
                self.attack_duration=pygame.time.get_ticks()
                self.create_attack()
            
            #crossbow
            if keys[pygame.K_RETURN]:
                self.attacking=True
                self.attack_duration=pygame.time.get_ticks()

            if keys[pygame.K_q] and self.can_switch_sweapon:
                self.can_switch_sweapon=False
                self.weapon_switch_cd=pygame.time.get_ticks()

                # make sure cycle between weapons instead of going out of range
                if self.weapon_index<len(list(weapon_data.keys()))-1:
                    self.weapon_index+=1
                else:
                    self.weapon_index=0
                self.weapon=list(weapon_data.keys())[self.weapon_index]

    def get_status(self):
        # idle
        if self.direction.x==0 and self.direction.y==0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status+='_idle'
        if self.attacking:
            self.direction.x=self.direction.y=0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status=self.status.replace('_idle','_attack')
                else:
                    self.status+='_attack'
        else:
                if 'attack' in self.status:
                    self.status=self.status.replace('_attack','')

    def move(self,speed):
        if self.direction.magnitude()!=0:
            self.direction=self.direction.normalize()

        self.hitbox.x+=self.direction.x*speed
        self.collision('h')
        self.hitbox.y+=self.direction.y*speed
        self.collision('v')
        self.rect.center=self.hitbox.center

    def collision(self,direction):
        if direction=='h':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x>0: #moving right
                        self.hitbox.right=sprite.hitbox.left
                    if self.direction.x<0: #moving left
                        self.hitbox.left=sprite.hitbox.right
        if direction=='v':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y<0: #moving down
                        self.hitbox.top=sprite.hitbox.bottom
                    if self.direction.y>0: #moving up
                        self.hitbox.bottom=sprite.hitbox.top
    
    def cooldowns(self):
        current_time=pygame.time.get_ticks()
        if self.attacking:
            if current_time-self.attack_duration>=self.attack_cd:
                self.attacking=False
                self.destroy_attack() 
        
        # weapon switch cooldown
        if not self.can_switch_sweapon:
            if current_time-self.weapon_switch_cd>=self.switch_duration_cd:
                self.can_switch_sweapon=True

    def animate(self):
        animation=self.animations[self.status]

        # loop over frame_index
        self.frame_index+=self.animation_speed
        if self.frame_index>=len(animation):
            self.frame_index=0

        # set image
        self.image=animation[int(self.frame_index)]
        self.rect=self.image.get_rect(center=self.hitbox.center)
    
    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)