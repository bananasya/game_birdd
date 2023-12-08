import pygame
from random import randint


class Button:
    def __init__(self, window, coord_x, coord_y, button_width, button_height, images=None):
        if images is None:
            images = []
        self.surface = window
        self.x = coord_x
        self.y = coord_y
        self.b_width = button_width
        self.b_height = button_height
        self.images = images
        self.pointer = 0

    def hitbox(self):
        global width
        return pygame.Rect(self.x, self.y, self.b_width, self.b_height)

    def show(self):
        self.surface.blit(pygame.image.load(self.images[self.pointer]), self.hitbox())

    def change(self):
        self.pointer = (self.pointer + 1) % len(self.images)
        self.surface.blit(pygame.image.load(self.images[self.pointer]), self.hitbox())

    def get_point(self):
        return self.pointer

    def collision(self, x, y):
        if self.hitbox().collidepoint((x, y)):
            return True
        else:
            return False


class Menu:
    def __init__(self, window):
        self.surface = window
        self.clock = pygame.time.Clock()
        self.button_play = Button(self.surface, int((width - 206) // 2), 300, 206, 56, ['images/button_play.png'])
        self.button_diff = Button(self.surface, int((width - 206) // 2), 380, 206, 56, ['images/button_easy.png',
                                                                                        'images/button_medium.png',
                                                                                        'images/button_hard.png'])
        self.button_quit = Button(self.surface, int((width - 206) // 2), 460, 206, 56, ['images/button_quit.png'])

    def fill_background(self):
        global width, height

        img_bg = pygame.image.load('images/background.png')
        for i in range(0, (width // 288) + 1):
            self.surface.blit(img_bg, pygame.Rect(i * 288, 0, 288, height))

        img_logo = pygame.image.load('images/flappy_logo.png')  # 578 x 159
        self.surface.blit(img_logo, pygame.Rect(int((width - 578) // 2), 70, 578, 159))

    def show_button(self):
        self.button_play.show()
        self.button_diff.show()
        self.button_quit.show()
        
    def change_difficult(self):
        self.button_diff.change()

    def main(self):

        self.fill_background()
        self.show_button()

        is_run = True
        is_click = False

        while is_run:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.button_play.collision(mouse_x, mouse_y) and is_click:
                run_game(self.button_diff.get_point())
            if self.button_diff.collision(mouse_x, mouse_y) and is_click:
                self.change_difficult()
            if self.button_quit.collision(mouse_x, mouse_y) and is_click:
                is_run = False
            is_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    is_click = True
                    
            pygame.display.update()
            self.clock.tick(fps)


class Bird:
    def __init__(self, bird_width, bird_height, images):
        global width, height
        self.x = width // 3
        self.y = height // 2
        self.bird_w = bird_width
        self.bird_h = bird_height
        self.angle = 0
        self.speed = 0
        self.boost = 0
        self.images = pygame.image.load(images)

    def hitbox(self):
        return pygame.Rect(self.x, self.y, self.bird_w, self.bird_h)

    def fall(self):
        self.speed = (self.speed + self.boost + 1) * 0.98
        self.y += self.speed

    def pushing(self, is_pushing):
        if is_pushing:
            self.boost = -2
        else:
            self.boost = 0
            
    def rotate(self):
        self.angle = (self.angle + 0.2) % 4
        image = self.images.subsurface(self.bird_w * int(self.angle), 0, self.bird_w, self.bird_h)
        image = pygame.transform.rotate(image, self.speed * -1.5)
        surface.blit(image, self.hitbox())

    def top(self):
        return self.hitbox().top

    def bottom(self):
        return self.hitbox().bottom

    def right(self):
        return self.hitbox().right

    def left(self):
        return self.hitbox().left

    def collision(self, rect):
        return self.hitbox().colliderect(rect)


class Pause:
    def __init__(self, difficult):
        self.difficult = difficult
        self.clock = pygame.time.Clock()
        self.button_resume = Button(surface, int((width - 206) // 2), 300, 206, 56, ['images/button_resume.png'])
        self.button_menu = Button(surface, int((width - 206) // 2), 380, 206, 56, ['images/button_menu.png'])
        self.button_quit = Button(surface, int((width - 206) // 2), 460, 206, 56, ['images/button_quit.png'])

    def fill_background(self):
        global width, height
        red_image = pygame.Surface((width, height), pygame.SRCALPHA)
        red_image.fill((255, 255, 255, 180))
        surface.blit(red_image, (0, 0))

    def show_button(self):
        self.button_resume.show()
        self.button_menu.show()
        self.button_quit.show()

    def main(self):

        self.fill_background()
        self.show_button()
        pygame.display.update()

        is_run = True
        is_click = False

        while is_run:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.button_resume.collision(mouse_x, mouse_y) and is_click:
                return 'play'
            if self.button_menu.collision(mouse_x, mouse_y) and is_click:
                return 'menu'
            if self.button_quit.collision(mouse_x, mouse_y) and is_click:
                return 'exit'
            is_click = False

            pygame.display.update()
            self.clock.tick(fps)


def run_game(difficult):
    img_bg = pygame.image.load('images/background.png')
    img_ptop = pygame.image.load('images/top.png')
    img_pdown = pygame.image.load('images/bottom.png')

    bird = Bird(27, 20, 'images/birds.png')
    speed = (difficult + 1) * 5
    lives = 3 - difficult
    timer = 10
    
    pipes = []
    pipes_scores = []
    pipe_speed = speed
    pipe_size = 200 - difficult * 20
    pipe_pos = height // 2
    bges = [pygame.Rect(0, 0, 290, 600)]

    scores = 0
    
    state = 'start'
    is_run = True
    while is_run:
        push = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = 'pause'

        if state != 'pause':
            if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]:
                push = True

            if timer:
                timer -= 1

            for i in range(len(bges) - 1, -1, -1):
                bg = bges[i]
                bg.x -= pipe_speed // 2

                if bg.right < 0:
                    bges.remove(bg)

                if bges[len(bges) - 1].right <= width:
                    bges.append(pygame.Rect(bges[len(bges) - 1].right, 0, 288, 600))

            for i in range(len(pipes) - 1, -1, -1):
                pipe = pipes[i]
                pipe.x -= pipe_speed

                if pipe.right < 0:
                    pipes.remove(pipe)
                    if pipe in pipes_scores:
                        pipes_scores.remove(pipe)

            if state == 'start':
                if push and not timer and not len(pipes):
                    state = 'play'

                bird.y += (height // 2 - bird.y) * 0.1

            elif state == 'play':

                bird.pushing(push)
                bird.fall()

                if not len(pipes) or pipes[len(pipes) - 1].x < width - 200:
                    pipes.append(pygame.Rect(width, 0, 52, pipe_pos - pipe_size // 2))
                    pipes.append(pygame.Rect(width, pipe_pos + pipe_size // 2, 52, height - pipe_pos + pipe_size // 2))

                    pipe_pos += randint(-100, 100)
                    if pipe_pos < pipe_size:
                        pipe_pos = pipe_size
                    elif pipe_pos > height - pipe_size:
                        pipe_pos = height - pipe_size

                if bird.top() < 0 or bird.bottom() > height:
                    state = 'fall'

                for pipe in pipes:
                    if bird.collision(pipe):
                        state = 'fall'

                    if pipe.right < bird.left() and pipe not in pipes_scores:
                        pipes_scores.append(pipe)
                        scores += 0.5
                        pipe_speed = speed + scores // 100

            elif state == 'fall':
                bird.speed = 0
                bird.boost = 0
                pipe_pos = height // 2

                lives -= 1
                if lives:
                    state = 'start'
                    timer = 60
                else:
                    state = 'game over'
                    timer = 120

            else:
                bird.fall()
                if not timer:
                    is_run = False

            for bg in bges:
                surface.blit(img_bg, bg)

            for pipe in pipes:
                if not pipe.y:
                    rect = img_ptop.get_rect(bottomleft=pipe.bottomleft)
                    surface.blit(img_ptop, rect)
                else:
                    rect = img_pdown.get_rect(topleft=pipe.topleft)
                    surface.blit(img_pdown, rect)

            bird.rotate()

            text = font.render('Score: ' + str(int(scores)), 1, 'white')
            surface.blit(text, (10, 10))

            text = font.render("Lives: " + str(lives), 1, 'white')
            surface.blit(text, (10, 50))
        else:
            pause = Pause(difficult)
            state = pause.main()
            print(state)
            if state == 'menu':
                menu = Menu(surface)
                menu.main()
            elif state == 'exit':
                is_run = False

        
        pygame.display.update()
        clock.tick(fps)


if __name__ == "__main__":
    pygame.init()
    width = 600
    height = 600
    fps = 30

    surface = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    pygame.display.set_caption('Flappy bird')
    pygame.display.set_icon(pygame.image.load('images/icon.png'))
    font = pygame.font.Font(None, 45)

    menu = Menu(surface)
    menu.main()
    pygame.quit()
