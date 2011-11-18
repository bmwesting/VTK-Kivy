from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock, ClockBase
from kivy.graphics import Color, Rectangle, Callback, Fbo
from vtk import *
from OpenGL.GL import *
from OpenGL.GLU import *

# set the environment so that special renderer is used by vtk
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
ren.GetActiveCamera().Dolly(.3)
ren.GetActiveCamera().Azimuth(0.5)
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
        Clock.schedule_interval(self.updateVTK, 1 / 1.)
        with self.canvas:
            self.fbo = Fbo(size=(512,512), clear_color=(.3, .3, .3, .8), push_viewport=True, with_depthbuffer=True)
            self.size = self.fbo.size
            Color(0, 0, 1)
            Rectangle(pos=self.pos, size=self.size, texture=self.fbo.texture)
            
            Callback(self.drawVTK, reset_context=True)
            
    def drawVTK(self, instr):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        VTKClock.tick()
        glViewport(0,0,512,512)
        self.fbo.clear_buffer()
        
        #push GL state of Kivy
        glUseProgram(0)
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
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

