import rhinoscriptsyntax as rs
import scriptcontext
 
KEY = "OldDblInput"
 
def test():
    dblInput = 1.0
    if scriptcontext.sticky.has_key(KEY):
        dblInput = scriptcontext.sticky[KEY]
    dblIn = rs.GetReal("Number please",dblInput)
    if dblIn is not None:
        print dblIn
        scriptcontext.sticky[KEY] = dblIn
 
test()