import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc

def slow_highlight_selected_faces ( brep, tan_face_Idx ):
    
    #Rhino.DocObjects.BrepObject.HighlightSubObject( BrepObj, StartIdx, True )
    
    AllFaces = brep.Faces
    x = Rhino.DocObjects.BrepObject(brep)
    Rhino.DocObjects.BrepObject.UnhighlightAllSubObjects(brep)
    
    for idx in tan_face_Idx:
        Rhino.DocObjects.BrepObject.HighlightSubObject( brep, AllFaces[idx].ComponentIndex(), True )
        scriptcontext.doc.Views.Redraw()

    return

def get_tangent_faces( brep, StartIdx, a_tol ):
    
    #Make list to keep track of indices of edges already checked.
    checked_edges = list()
    
    all_faces = brep.Faces
       
       #this is a volatile list of the tangent face IDs in the brep.
       #The list only contains tangent
       #faces that have not yet been tested against their neighbors.
    tan_faces = list()
    tan_faces.append(StartIdx)
       
       #this is a running list of the all tangent face idx in the brep
       #Used later to create the part of the input brep that is not tangent.
    tan_face_Idx = list()
    tan_face_Idx.append(StartIdx)
    
    r_tol = Rhino.RhinoMath.ToRadians(a_tol)
    
    while tan_faces:
        crnt_face = tan_faces[0]
        tan_faces.pop(0)
        brepEdges = brep.Edges
        adjIdx = all_faces[crnt_face].AdjacentEdges()
        testEdges = list()
        
        for idx in adjIdx:
            if not idx in checked_edges: #.count(idx):
                testEdges.append(idx)
                
        if testEdges:
               
            for item in testEdges:
                testFaces = brep.Edges[item].AdjacentFaces()
                if brep.Edges[item].IsSmoothManifoldEdge (r_tol):
                    
                    for x in testFaces:
                        if not x in tan_face_Idx:
                            tan_faces.append(x)
                            tan_face_Idx.append(x)
                            
    return ( tan_face_Idx )

def ExtractAdjacentTangentFaces(brep, StartIdx, a_tol, blnCopy, blnJoin):
    #Finds contiguous tangent faces starting from a single face.
    
    NewIdx = None
    boolGrow = False
    boolShrink = False
    #set the iteration counter to zero.
    
    
    Rhino.RhinoApp.SetCommandPrompt("Please wait, calculating tangent faces")
    tan_face_Idx = get_tangent_faces(brep, StartIdx, a_tol)
    
    slow_highlight_selected_faces ( brep, tan_face_Idx)
    scriptcontext.doc.Views.Redraw()
    tol_old = 1

    
    if scriptcontext.sticky.has_key("tol_old"):
        tol_old = scriptcontext.sticky["tol_old"] 
        
    result = get_angle_tol(brep)
    if result:
        if result == Rhino.Commands.Result.Cancel:
            Rhino.DocObjects.BrepObject.UnhighlightAllSubObjects(brep)
            return
    else: return
    
    ResultType = result.GetType()
    if ResultType == tuple:
        a_tol, boolGrow, boolShrink = result
    elif ResultType == int:
         NewIdx = result #the face to add or subtract
        
    while a_tol != tol_old or boolGrow == True or boolShrink == True or NewIdx:
        
        if NewIdx: 
            AddResult = add_face ( brep, tan_face_Idx, NewIdx )
            if AddResult.GetType() == list: 
                tan_face_Idx = AddResult
                fast_highlight_selected_faces( brep, tan_face_Idx )
                NewIdx = None
                #break
        else:
            if a_tol != tol_old and a_tol <> 0:
                Rhino.RhinoApp.SetCommandPrompt("Please wait, recalculating tangent faces")
                tan_face_Idx = get_tangent_faces( brep, StartIdx, a_tol )
                slow_highlight_selected_faces ( brep, tan_face_Idx )
                
        if boolGrow:
            tan_face_Idx = grow(brep, tan_face_Idx, 0)
            fast_highlight_selected_faces( brep, tan_face_Idx )
        boolGrow = False

        if boolShrink: 
            tan_face_Idx = grow(brep, tan_face_Idx, 1)
            fast_highlight_selected_faces( brep, tan_face_Idx )
            if len(tan_face_Idx) == 0:return Rhino.Commands.Result.Failure
        boolShrink = False
        
        if scriptcontext.sticky.has_key("tol_old"):
            tol_old = scriptcontext.sticky["tol_old"] 
            
        result = get_angle_tol(brep)
        if result:
            if result == Rhino.Commands.Result.Cancel:
                Rhino.DocObjects.BrepObject.UnhighlightAllSubObjects(brep)
                return
        else: return
        
        NewIdx = None
        ResultType = result.GetType()
        if ResultType == tuple:
            a_tol, boolGrow, boolShrink = result
        elif ResultType == int:
             NewIdx = result #the face to add or subtract
        
        scriptcontext.doc.Views.Redraw()
        
    x_brep = list()
    other_breps = list()
    
    if tan_face_Idx:
        
        dup_faces = create_faces( brep,tan_face_Idx )
        
        if dup_faces:
            j_tol = scriptcontext.doc.ModelAbsoluteTolerance
            if blnJoin: 
                joinedbreps = Rhino.Geometry.Brep.JoinBreps(dup_faces, j_tol)
                for item in joinedbreps:
                    brep_ID = scriptcontext.doc.Objects.AddBrep(item)
                    x_brep.append(brep_ID)
                    obj = scriptcontext.doc.Objects.Find(brep_ID)
                    obj.Select(True)
            else: 
                for item in dup_faces:
                    x_brep.append(item.Id)
    
        if not blnCopy: other_breps = make_extracted_brep(brep, tan_face_Idx)
        scriptcontext.sticky["tol_old"] = a_tol
        Rhino.DocObjects.BrepObject.UnhighlightAllSubObjects(brep)
    return (other_breps, x_brep)

def test():
    
    j_tol = sc.doc.ModelAbsoluteTolerance
    srfs = rs.GetObjects("get em", 8, preselect=True)
    
    if srfs:
        brep = Rhino.Geometry.Brep()
        geo_list = [sc.doc.Objects.Find(srf).Geometry.Faces[0].DuplicateFace(True) for srf in srfs]
        for geo in geo_list:
            brep.Append(geo)
            
        ExtractAdjacentTangentFaces(brep, 0, 1, True,True)
            
        pass



test()