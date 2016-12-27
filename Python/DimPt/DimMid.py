import rhinoscriptsyntax as rs
import Rhino

def DimMid():
    
    def get_line():
        
        gl = Rhino.Input.Custom.GetLine()
        gl.EnableFromMidPointOption(True)
        rc, line = gl.Get()
        return rc, line
        
    rc, _line_ = get_line()
    if rc != Rhino.Commands.Result.Success: return
    rs.Command ("DimAligned W" + str(_line_.From) + " W"+ str(_line_.To))
    

if( __name__ == "__main__" ):
    DimMid()