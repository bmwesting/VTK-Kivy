from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock, ClockBase
from kivy.graphics import Color, Rectangle, Callback, Fbo
from kivy.graphics.opengl import glEnable, GL_DEPTH_TEST, GL_CULL_FACE
from vtk import *
from OpenGL.GL import *

# set the environment so that special render window is called
import os
os.environ['VTK_RENDERER'] = 'EmbedOpenGL'

cone = vtkConeSource()
mapper = vtkPolyDataMapper()
actor = vtkActor()
ren = vtkRenderer()
renWin = vtkRenderWindow()

mapper.SetInput(cone.GetOutput())
actor.SetMapper(mapper)
ren.AddActor(actor)
ren.SetBackground(0.0, 1.0, 0.0)
ren.GetActiveCamera().Dolly(.1)
renWin.AddRenderer(ren)
renWin.SetSize(512,512)

VTKClock = ClockBase()

class VTKWidget(Widget):
    
    def __init__(self, **kwargs):
        super(VTKWidget,self).__init__(**kwargs)
        self.setupVTK()
    
    def updateVTK(self, *largs):
        self.fbo.ask_update()
        self.canvas.ask_update()

    def setupVTK(self):
        Clock.schedule_interval(self.updateVTK, 1 / 60.)
        with self.canvas:
            self.fbo = Fbo(size=(512,512), clear_color=(.3, .3, .3, .8), push_viewport=True)
            self.size = self.fbo.size
            Color(1, 1, 0)
            Rectangle(pos=self.pos, size=self.size, texture=self.fbo.texture)
            Callback(self.drawVTK, reset_context=True)
            
    def drawVTK(self, instr):
        VTKClock.tick()
        self.fbo.clear_buffer()
        
        #push GL state of Kivy
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        #Load identity and render VTK
        glLoadIdentity()
        renWin.Render()
        
        #pop previous state of Kivy
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glPopAttrib()
        
class MyVTKApp(App):
    def build(self):
        return VTKWidget()

if __name__ == '__main__':
    MyVTKApp().run()
