import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc



def test():
    
    def get_inputs():
        oldCopy=False
        if sc.sticky.has_key("PROJECT_OBJECTS_COPY"):
            oldCopy= sc.sticky["PROJECT_OBJECTS_COPY"]
            
            
        go = Rhino.Input.Custom.GetObject()
        blnCopy = Rhino.Input.Custom.OptionToggle(oldCopy, "No", "Yes")
        optCopy = go.AddOptionToggle("Copy",blnCopy) 
        x = go.Get()
        pass
    get_inputs()
    
test()