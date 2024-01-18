import pygame

class Mt():
    def __init__(self):
        super().__init__()
        self.Sstate2 = False
        self.dragon = None
        self.a1 = None
        self.a2 = None
        self.state = False
        self.log_in_button_rect = pygame.Rect(1678, 789, 371, 104)  # Define log_in_button_rect here
        self.strat_button_rect = pygame.Rect(1678, 977, 371, 104)

        # self.log_in_hovered = False
        self.user_input = ''
        self.password_input = ''
        self.active_input = None

    def load_images(self):
        self.dragon = pygame.image.load('CombineVersion/Data/GameData/images/Dargon/map2_complete.png').convert_alpha()

    def UIrender(self, root, font):
        user_text = font.render('User', True, (255, 255, 255))
        password_text = font.render('Password', True, (255, 255, 255))
        log_in_text = font.render('Log in', True, (255, 255, 255))
        text_height = user_text.get_height()
        # Assign log_in_button_rect here
        # self.log_in_button_rect = log_in_text.get_rect(topleft=(1678, 789))

        user_text_rect = user_text.get_rect(topleft=(1630, 314))
        password_text_rect = password_text.get_rect(topleft=(1630, 525))  # 加一些垂直间距
        log_in_text_rect = log_in_text.get_rect(topleft=(1678, 789))  # 加一些垂直间距
        # Define input box rectangles
        self.user_input_rect = pygame.Rect(1630, 379 + user_text.get_height() + 33, 200, 30)
        self.password_input_rect = pygame.Rect(1630,
                                               379 + user_text.get_height() + 173 + password_text.get_height() + 10,
                                               200, 30)
        # Render the text the user has entered
        user_input_text = font.render(self.user_input, True, (255, 255, 255))
        password_input_text = font.render(self.password_input, True, (255, 255, 255))


        # Use different images and display "Start" inside the button when hovered
        if self.state and self.log_in_hovered:
            # root.blit(self.a2, (695,679 ))
            root.blit(font.render('Start', True, (255, 255, 255)), (1678, 977))
        # else:
        #     root.blit(self.a1, (1353, 379))

        root.blit(user_text, user_text_rect.topleft)
        # root.blit(password_text, password_text_rect.topleft)
        root.blit(log_in_text, log_in_text_rect.topleft)
            # Draw input boxes
        pygame.draw.rect(root, (255, 255, 255), self.user_input_rect, 2)
        # pygame.draw.rect(root, (255, 255, 255), self.password_input_rect, 2)
        root.blit(user_input_text, (self.user_input_rect.x + 5, self.user_input_rect.y + 5))
        # root.blit(password_input_text, (self.password_input_rect.x + 5, self.password_input_rect.y + 5))



    # def run_game(self):
    #     Game.run(self)
    #     pygame.quit()
    #     sys.exit()

    def main(self):



        root = pygame.display.set_mode((1920, 1080))
        font = pygame.font.Font(None, 36)

        self.load_images()

        clock = pygame.time.Clock()
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1

                if event.type == pygame.KEYDOWN:
                    if self.active_input == 'user':
                        if event.key == pygame.K_BACKSPACE:
                            self.user_input = self.user_input[:-1]
                        else:
                            self.user_input += event.unicode
                    elif self.active_input == 'password':
                        if event.key == pygame.K_BACKSPACE:
                            self.password_input = self.password_input[:-1]
                        else:
                            self.password_input += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.user_input_rect.collidepoint(event.pos):
                        self.active_input = 'user'
                    elif self.password_input_rect.collidepoint(event.pos):
                        self.active_input = 'password'


                    self.log_in_hovered = self.log_in_button_rect.collidepoint(pygame.mouse.get_pos())
                    self.Sstate2 = self.strat_button_rect.collidepoint(pygame.mouse.get_pos())


                    if event.type == pygame.MOUSEBUTTONDOWN and self.log_in_hovered :
                        self.player_name = self.user_input
                        # self.user_input = '',
                        # self.password_input = ''
                        self.state = True

                    elif event.type == pygame.MOUSEBUTTONDOWN and self.state == True and self.Sstate2:
                        return 1, self.player_name



            root.fill((0, 0, 0))
            root.blit(self.dragon, (0, 0))
            self.UIrender(root, font)
            pygame.display.update()
            clock.tick(60)

if __name__ == '__main__':
    Mt().main()
