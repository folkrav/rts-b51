from bge import logic, events, render
from unit import *

ZOOM_STEPS = 5
ZOOM_MIN = 10
ZOOM_MAX = 35
SCROLL_SPEED = 0.25


class Mouse(object):

    def __init__(self, parent):
        self.parent = parent
        self.key = {
            "LeftClick": logic.mouse.events[logic.KX_MOUSE_BUT_LEFT],
        }

    def select(self, cont):
        """ main mouse fonction, will be extended as we add mouse controls
        It is called from bge.c (controller) if mouse.events = True"""
        scene = logic.getCurrentScene()
        cam = scene.active_camera
        mouse_pos = cont.sensors["Mouse_Pos"]

        self.edge_scroll(scene, cam, mouse_pos)
        self.left_click(scene, mouse_pos)
        self.right_click(mouse_pos)
        self.scroll_wheel(scene, cam, mouse_pos)

    ############################################################################
    # Mouse movement                                                           #
    ############################################################################
    def edge_scroll(self, scene, cam, mouse_pos):
        """Detect if mouse is close to the screen edge and, if so, move the camera."""
        if mouse_pos.position[0] <= 5:
            self.move_cam(scene, cam, 1)
            if mouse_pos.position[0] < 0:
                render.setmouse_position(2, mouse_pos.position[1])
        elif mouse_pos.position[1] <= 5:
            self.move_cam(scene, cam, 2)
            if mouse_pos.position[1] < 0:
                render.setmouse_position(mouse_pos.position[0], 2)
        elif mouse_pos.position[0] >= render.getWindowWidth() - 5:
            self.move_cam(scene, cam, 3)
            if mouse_pos.position[0] > render.getWindowWidth():
                render.setmouse_position(render.getWindowWidth(), mouse_pos.position[1] - 2)
        elif mouse_pos.position[1] >= render.getWindowHeight() - 5:
            self.move_cam(scene, cam, 4)
            if mouse_pos.position[1] > render.getWindowHeight():
                render.setmouse_position(mouse_pos.position[0], render.getWindowHeight() - 2)

    ############################################################################
    # Left click                                                               #
    ############################################################################
    def left_click(self, scene, mouse_pos):
        """Handling left click actions."""
        if self.key["LeftClick"] == logic.KX_INPUT_JUST_ACTIVATED:
            self.parent.selectedUnits = []
            self.x1 = mouse_pos.hitPosition[0]
            self.y1 = mouse_pos.hitPosition[1]

        if self.key["LeftClick"] == logic.KX_INPUT_ACTIVE:
            self.x2 = mouse_pos.hitPosition[0]
            self.y2 = mouse_pos.hitPosition[1]
            z = mouse_pos.hitPosition[2] + 0.1
            self.draw_square()

        if self.key["LeftClick"] == logic.KX_INPUT_JUST_RELEASED:
            if self.x1 > self.x2:
                self.x1, self.x2 = self.x2, self.x1
            if self.y1 > self.y2:   # met en ordre croissant
                self.y1, self.y2 = self.y2, self.y1
            self.unit_select(scene, mouse_pos)

        def draw_square(self):
            render.drawLine((self.x1, self.y1, z), (self.x2, self.y1, z), (1, 0, 0))
            render.drawLine((self.x1, self.y1, z), (self.x1, self.y2, z), (1, 0, 0))
            render.drawLine((self.x2, self.y2, z), (self.x2, self.y1, z), (1, 0, 0))
            render.drawLine((self.x2, self.y2, z), (self.x1, self.y2, z), (1, 0, 0))

        def unit_select(self, ):
            for obj in scene.objects:    # itere au travers les objets de la scene (pas excellent performances)
                if isinstance(obj, Unit):    # Select = bool in object attributes
                    if obj not in bge.c.units:
                        self.parent.units.append(obj)
                    x = obj.worldPosition[0]
                    y = obj.worldPosition[1]

                    if x > self.x1 and y > self.y1 and x < self.x2 and y < self.y2:    # si a linterieur du rectangle
                        self.parent.selectedUnits.append(obj)
                        # obj.circle = scene.addObject('Select_Circle', obj)
                        obj.selected = True

    def move_cam(self, scene, cam, side):
        """Moves the camera in a direction."""
        camX = cam.position[0]
        camY = cam.position[1]
        camZ = cam.position[2]

        if side == 1:
            cam.position = [camX - SCROLL_SPEED, camY - SCROLL_SPEED, camZ]
        elif side == 2:
            cam.position = [camX - SCROLL_SPEED, camY + SCROLL_SPEED, camZ]
        elif side == 3:
            cam.position = [camX + SCROLL_SPEED, camY + SCROLL_SPEED, camZ]
        elif side == 4:
            cam.position = [camX + SCROLL_SPEED, camY - SCROLL_SPEED, camZ]

    ############################################################################
    # Right click                                                              #
    ############################################################################
    def right_click(self, mouse_pos):
        """Handling right click actions."""
        if logic.mouse.events[logic.KX_MOUSE_BUT_RIGHT] == logic.KX_INPUT_JUST_ACTIVATED:
            dist = 0
            for obj in self.parent.selectedUnits:
                obj.destination = [mouse_pos.hitPosition[0] + dist,
                                   mouse_pos.hitPosition[1],
                                   obj.worldPosition[2]]
                dist += 0.7
                if not obj.moving:
                    self.parent.movingUnits.append(obj)
                    obj.moving = True

    ############################################################################
    # Scroll wheel                                                             #
    ############################################################################
    def scroll_wheel(scene, cam, mouse_pos):
        if logic.mouse.events[logic.KX_MOUSE_BUT_MIDDLE] == logic.KX_INPUT_JUST_ACTIVATED:
            scene.objects['Way_Circle'].worldPosition.x = mouse_pos.hitPosition[0]
            scene.objects['Way_Circle'].worldPosition.y = mouse_pos.hitPosition[1]
            bge.c.buildings[0].way_point = True
            scene.objects['Way_Circle'].setVisible(True)

        if logic.mouse.events[events.WHEELDOWNMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            cam = scene.cameras["Camera"]
            if cam.ortho_scale <= ZOOM_MAX:
                for i in range(ZOOM_STEPS):
                    cam.ortho_scale += 1

        if logic.mouse.events[events.WHEELUPMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
            cam = scene.cameras["Camera"]
            if cam.ortho_scale >= ZOOM_MIN:
                for i in range(ZOOM_STEPS):
                    cam.ortho_scale -= 1
