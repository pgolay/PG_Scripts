import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

"""
Plane from frame at surface mid param
Plane from points on mesh vertices
Plane from brep verts or render mesh

Project plane normal to cplane
Rotate object on CPlane normal from projected plane normal to
projected camera/target normal

GetObject
options Add, remove


SetUserText to tag/untag objects

"""

def test():
    
    aAll = rs.NormalObjects()
    tagged = []
    for Id in aAll:
        x = rs.GetUserText(Id)
        if x:
            if "FACECAMERA" in x:
                idx = x.index("FACECAMERA")
                if idx is not None: 
                 tagged.append(Id)
                 
     
    #Ids = rs.GetObjects( objects=tagged)
 
    class Custom_GetObject(Rhino.Input.Custom.GetObject):
        
        def __init__(self, objects):
            self.m_objects = objects
            
        def CustomGeometryFilter( self, rhino_object ):
            print str(rhino_object.Id)
            print "True"
            if objects and not rhino_object.Id in objects:
                print "False" 
                return False
            testrc = True

            return testrc.Object
    
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select objects")
    optRemove = go.AddOption("RemoveObjects")
    
    while True:
        rc = go.GetMultiple(1,0)

        if go.CommandResult()!=Rhino.Commands.Result.Success:
            return go.CommandResult()
            
        elif rc==Rhino.Input.GetResult.Option:
            gor = Custom_GetObject(tagged)
            gor.AcceptNothing(True)
            gor.SetCommandPrompt("Select objects")
            remove_rc = gor.GetMultiple(1,0)

            pass
            break
        break
    
    
test()