import Rhino
import scriptcontext as sc

def ShrinkIt():
    
    go = Rhino.Input.Custom.GetObject()
    go.EnablePreSelect(True, False)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    go.Get()
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
        
    objRef = go.Objects()[0]
    Face = objRef.Face()
    brep = Face.DuplicateFace(False)

    print brep.Faces.ShrinkFaces()
    sc.doc.Objects.AddBrep(brep)

    pass
    

    
if( __name__ == "__main__" ):
    ShrinkIt()