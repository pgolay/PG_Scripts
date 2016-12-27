import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
from System import Drawing
 
"""
FInd verts
find topoVerts idx per vertex
find groups of verts per idx
    dict?  {tvIDX: [vIdx,xIdx,vIdx]}
find face associated with each Vert per tVert
 search face list for the idx - if found add the face to a list.
find the face normals from each face
Average the normals
Set the normal at the same idx as each vertex to this vector.
Find TVerts



"""
def test():
    
    rc, objRef = Rhino.Input.RhinoGet.GetOneObject("Select a mesh.", False, filter = Rhino.DocObjects.ObjectType.Mesh)
    if rc != Rhino.Commands.Result.Success: return
    
    mesh = objRef.Object().Geometry
    tVerts = mesh.TopologyVertices
    fNorms  = mesh.FaceNormals
    vNorms = mesh.Normals
   
    for n in range (tVerts.Count):
        vecs = [fNorms[i] for i in range(len(tVerts.ConnectedFaces(n)))]
        
        k =0
        result = Rhino.Geometry.Vector3f.Unset
        
        for vec in vecs:
            result = result + vec
            result.Unitize()
            k = k + 1
            
        result = result/k
        result.Unitize()
        
        for idx in tVerts.MeshVertexIndices(n):
            vNorms.SetNormal(idx, result)

    sc.doc.Objects.Replace(objRef.ObjectId, mesh)
    
    sc.doc.Views.Redraw()

        
test()