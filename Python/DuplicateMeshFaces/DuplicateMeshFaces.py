import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino


def duplicates(lst, n):
    result = [i for i, x in enumerate(lst) if x == lst[n]]
    return result

def ExtractAllDuplicateMeshFaces():
    
    rc, objRef = Rhino.Input.RhinoGet.GetOneObject("Select a mesh", False, Rhino.DocObjects.ObjectType.Mesh)
    if rc != Rhino.Commands.Result.Success:return
    
    mesh = objRef.Object().Geometry
    count = mesh.Vertices.Count
    vList = [mesh.Vertices[i] for i in range (count)]
    faceTVs = []
    
    for  face in mesh.Faces:
        tvFace  = [mesh.TopologyVertices.TopologyVertexIndex(n) for n in face]
        faceTVs.append(set((sorted(tvFace))))
        pass
        
    dups = []
    deleteFaces = []
    
    for i in range(len(faceTVs)):
        temp = duplicates(faceTVs, i)
        if len(temp) > 1:
            dups.append(temp[0])
            for n in range(len(temp)):
                deleteFaces.append(temp[n])
            
    dups = set(dups)
    
    M1 = Rhino.Geometry.Mesh()
    p = 0
    
    for idx in dups:
        face = mesh.Faces[idx]
        verts = [mesh.Vertices[n] for n in face]
        for vert in verts:M1.Vertices.Add(vert) 
        faceVerts = [p + n for n in range(len(verts))]
        
        if len(verts) ==4:
            M1.Faces.AddFace(p, p+1, p+2, p+3)
        else:
            M1.Faces.AddFace(p, p+1, p+2)
        p = p + len(verts)
        pass
    
    mesh.Faces.DeleteFaces(deleteFaces)
    sc.doc.Objects.Replace(objRef.ObjectId, mesh)
    
    newMeshId = sc.doc.Objects.AddMesh(M1)
    sc.doc.Objects.UnselectAll()
    
    if newMeshId:
         rs.FlashObject(newMeshId)
         rs.MatchObjectAttributes(newMeshId, objRef.ObjectId)
    sc.doc.Objects.Select(newMeshId, True, True)
    sc.doc.Views.Redraw()

    
if __name__ == "__main__":
    ExtractAllDuplicateMeshFaces()