import Rhino
import rhinoscriptsyntax as rs


def GBView():
    #rs.EnableRedraw(False)
    #    view = rs.CurrentView()
    #    vPlane = rs.ViewCameraPlane(view)
    #    crntPlane = rs.ViewCPlane(view)
    #    rs.ViewCPlane(view, vPlane)
    rs.Command ("CPlane View ")
    rs.Command ("GumballAlignment World ") 
    rs.Command ("GumballAlignment CPlane ")
    rs.Command ("CPlane Previous ")
    #    rs.ViewCPlane(view, crntPlane)
    rs.EnableRedraw(True)

if( __name__ == "__main__" ):
    GBView()