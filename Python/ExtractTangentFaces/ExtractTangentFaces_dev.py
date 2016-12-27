import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
###############################################
#This version has automatic largest face selection.
###############################################

"""
Selects and extract tangent faces from a polysurface.
"""

def vector_angle(vec1, vec2):
    #returns the angle in degrees between two vectors
    vec1.Unitize()
    vec2.Unitize()
    DP = vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]
    
    if DP > .999999:
        return 0
    elif DP < -.999999:
        return 180
    else:
        return Rhino.RhinoMath.ToDegrees (math.acos(DP))
        
#def make_extracted_brep(brep, tan_face_idx):
#    #NOTE: Use this version if a way to split disjoint breps IS found.
#######################################################################

#    #Remove the tangent faces from the brep.
#    tan_face_idx.sort()
#    tan_face_idx.reverse()
#    for face_idx in tan_face_idx:
#        brep.Geometry.Faces.RemoveAt(face_idx)
#    return brep.Geometry
    
def make_extracted_brep(brep, tan_face_idx):
    #NOTE: Use this version if no way to split disjoint breps is found.
    ###################################################################
    
    #Make a brep or breps from an input brep minus the faces in a list.
    
    all_faces = brep.Geometry.Faces
    face_idx = list()
    other_faces = list()
    other_breps = list()
    
    for face_item in all_faces:
        face_idx.append(face_item.FaceIndex)
    
    for idx_item in face_idx:
        if not idx_item in tan_face_idx:
            face_obj = all_faces[idx_item].DuplicateFace(True)
            other_faces.append(face_obj)
        
    if other_faces:
        #Join the faces into one or more new breps
        j_tol = scriptcontext.doc.ModelAbsoluteTolerance
        joinedBreps = Rhino.Geometry.Brep.JoinBreps(other_faces, j_tol)
        for brep_item in joinedBreps:
            if brep_item.IsValid:
                #Add the joined breps to the document
               brep_ID = scriptcontext.doc.Objects.AddBrep(brep_item)
               other_breps.append(brep_ID)
               
    return other_breps
    
def check_for_nakeds(idx, brep):
    
    boolNaked = False
    AllEdges = brep.Geometry.Edges
    FaceList = brep.Geometry.Faces
    edges = FaceList[idx].AdjacentEdges()
    
    if edges:
        for edge in edges:
            if str(AllEdges[edge].Valence) == "Naked":
                boolNaked = True
                break
                
    return boolNaked
    
def create_faces( brep, FaceIdxList ):
    
    NewFaces = list()
    AllFaces = brep.Geometry.Faces
    
    for idx in FaceIdxList:
        NewFaces.append(AllFaces[idx].DuplicateFace(True))
        
    return NewFaces
    
def slow_highlight_selected_faces ( brep, tan_face_Idx ):
    
    #Rhino.DocObjects.BrepObject.HighlightSubObject( BrepObj, StartIdx, True )
    
    AllFaces = brep.Geometry.Faces
    Rhino.DocObjects.BrepObject.UnhighlightAllSubObjects(brep)
    
    for idx in tan_face_Idx:
        Rhino.DocObjects.BrepObject.HighlightSubObject( brep, AllFaces[idx].ComponentIndex(), True )
        scriptcontext.doc.Views.Redraw()

    return
    
def fast_highlight_selected_faces ( brep, tan_face_Idx ):
    
    #Rhino.DocObjects.BrepObject.HighlightSubObject( BrepObj, StartIdx, True )
    
    AllFaces = brep.Geometry.Faces
    Rhino.DocObjects.BrepObject.UnhighlightAllSubObjects(brep)
    for idx in tan_face_Idx:
        Rhino.DocObjects.BrepObject.HighlightSubObject( brep, AllFaces[idx].ComponentIndex(), True )
    scriptcontext.doc.Views.Redraw()
    
    return
    
def grow(brep, tan_face_Idx, intGrow):
    
    # tan_face_Idx is a list of tangent faces indices in the original brep.
    # dup_faces is a list of dups of the tangent faces, as geometry.
    # dup_faceID is a list of ID's of the duped faces.
    
    all_faces = brep.Geometry.Faces
    
    TempFaceIdx = list()
    RemoveFaces = list()
    
    for idx in tan_face_Idx:
        CurrentFace = all_faces[idx]
        test_faces = CurrentFace.AdjacentFaces() #Indices

        if test_faces:
            if intGrow == 0: # Grow
                for faceIdx in test_faces:
                        if faceIdx not in tan_face_Idx and faceIdx not in TempFaceIdx :
                            TempFaceIdx.append (faceIdx)
                            
            else: # Shrink
                if idx not in RemoveFaces:
                    for faceIdx in test_faces:
                        if faceIdx not in tan_face_Idx  or check_for_nakeds(CurrentFace.FaceIndex, brep):
                           if idx not in RemoveFaces:RemoveFaces.append(idx)
                          
    if RemoveFaces:
        for idx in RemoveFaces:
            tan_face_Idx.remove(idx)
     
    if TempFaceIdx:
        for idx in TempFaceIdx:
            tan_face_Idx.append (idx)
            
    #scriptcontext.doc.Views.Redraw()
    
    return (tan_face_Idx)
    
def add_face( brep, tan_face_Idx, NewIdx ):
    
    AllFaces = brep.Geometry.Faces # Indices
    
    if NewIdx in tan_face_Idx:
        tan_face_Idx.remove(NewIdx)
    else:
        tan_face_Idx.append(NewIdx)
        #Rhino.DocObjects.BrepObject.HighlightSubObject( brep, objref.GeometryComponentIndex, True )
    #    scriptcontext.doc.Views.Redraw()
    return tan_face_Idx
    
def get_angle_tol(Brep):
    
    Brep.UnselectAllSubObjects()
    tol_old = 1
    if scriptcontext.sticky.has_key("tol_old"):
        tol_old = scriptcontext.sticky["tol_old"]
    go = Rhino.Input.Custom.GetObject()
    go.AcceptNothing(True)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    go.SubObjectSelect = True
        # Make sure any selection is deslected
    go.EnablePreSelect(False, True)
            #accept a typed number, if any, to be retrieved as angle tolerace
    go.AcceptNumber(True, False)
    
    go.AlreadySelectedObjectSelect #Property, how do I set this?
    
    tolOption = Rhino.Input.Custom.OptionDouble(tol_old)
    go.AddOptionDouble("AngleTolerance", tolOption)
    optGrow = go.AddOption("Grow")
    optShrink = go.AddOption("Shrink")
    
    go.SetCommandPromptDefault(str(tol_old))
    go.SetCommandPrompt("Select faces to add or remove. Press Enter to accept current face selection.")
    
    a_tol = tol_old
    objref = None
    
    #gw = Rhino.Input.Custom.GetBaseClass.SetCommandPrompt("Recalulating tangent surfaces for angle tolerance " + str(a_tol))
    while True:
        boolGrow = False
        boolShrink = False
        # perform the get operation. This will prompt the user to
        get_rc = go.Get()
        # print scriptcontext.escape_test()
        if go.CommandResult()!= Rhino.Commands.Result.Success:
            #return a_tol, False, False
            return go.CommandResult()
            
        if get_rc == Rhino.Input.GetResult.Nothing:
            a_tol, boolGrow, boolShrink
            
        if get_rc == Rhino.Input.GetResult.Cancel:
            break
          
        if get_rc==Rhino.Input.GetResult.Object:
            
            objref = go.Object(0)
            FaceIdx = objref.GeometryComponentIndex.Index
            return FaceIdx

        if get_rc==Rhino.Input.GetResult.Option:
            
            a_tol = tolOption.CurrentValue
            # save the value for use in the future
            scriptcontext.sticky["tol_old"] = a_tol
            selected_index = go.Option().Index
    
            if selected_index == 2: boolGrow = True
            if selected_index == 3: boolShrink = True
            return a_tol, boolGrow, boolShrink
        break
    
    return get_rc
    
    def FindLargestFace():
    
    
        def selBrep():
            go= Rhino.Input.Custom.GetObject()
            go.SetCommandPrompt("Select a polysurface.")
            go.SubObjectSelect = False
            objref = None
            rc_valid = True #Check for invalid faces.
            while True:
                # perform the get operation. 
                get_rc = go.Get()
                
                if go.CommandResult()!=Rhino.Commands.Result.Success:
     #                print get_rc
                    return False, 0,0
                    #return go.CommandResult()
                    
                if get_rc==Rhino.Input.GetResult.Object:
                    objref = go.Object(0)
                    BrepObj = objref.Object()
                    error_message = "The polysurface has some bad faces. Try removing these with ExtractBadSrf first."
                    if not BrepObj.IsValid:
                        print error_message
                        Rhino.UI.Dialogs.ShowMessageBox(error_message, "Bad faces encountered.")
                        rc_valid= False #tag brep has invalid face
                        return [False , objref, -1]
                    scriptcontext.doc.Views.Redraw()
                    return [rc_valid, objref, 0]
                    
        rc_valid, objref, X = selBrep()
    
    if not rc_valid: return [False , objref, -1] # if there is an invalid face bail and return this info to the calling function
    brep = objref.Geometry()
    faces = brep.Faces
    Num_faces = str(faces.Count)
    area = 0
    idx = 0
    n = 0
    Rhino.RhinoApp.SetCommandPrompt ( "Searching for the largest of " + Num_faces + " faces...")
    for face in faces:
        if not face.IsValid: print "No Good"
        #k = face.DuplicateFace(True)
        m = Rhino.Geometry.AreaMassProperties.Compute(face)
        temp_area = m.Area
        if temp_area >= area:
            area = temp_area
            idx = n
        n = n + 1
        
    print  "Largest face area = " + str(round(area,3)), "; Face # ", idx
  #    rs.UnselectAllObjects()
    rc = scriptcontext.doc.Objects.UnselectAll()
    if rc>0: scriptcontext.doc.Views.Redraw()
    fast_highlight_selected_faces(objref.Object(), [idx])
    
    X = objref.Object().GetHighlightedSubObjects()[0]
    return   rc_valid, objref, X
    
def get_tangent_faces( brep, StartIdx, a_tol ):
    
    #Make list to keep track of indices of edges already checked.
    checked_edges = list()
    
    all_faces = brep.Geometry.Faces
       
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
        brepEdges = brep.Geometry.Edges
        adjIdx = all_faces[crnt_face].AdjacentEdges()
        testEdges = list()
        
        for idx in adjIdx:
            if not idx in checked_edges: #.count(idx):
                testEdges.append(idx)
                
        if testEdges:
               
            for item in testEdges:
                testFaces = brep.Geometry.Edges[item].AdjacentFaces()
                if brep.Geometry.Edges[item].IsSmoothManifoldEdge (r_tol):
                    
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
    
def FindLargestFace():
    
    
    def selBrep():
        go= Rhino.Input.Custom.GetObject()
        go.SetCommandPrompt("Select a polysurface.")
        go.SubObjectSelect = False
        objref = None
        rc_valid = True #Check for invalid faces.
        while True:
            # perform the get operation. 
            get_rc = go.Get()
            
            if go.CommandResult()!=Rhino.Commands.Result.Success:
 #                print get_rc
                return False, 0,0
                #return go.CommandResult()
                
            if get_rc==Rhino.Input.GetResult.Object:
                objref = go.Object(0)
                BrepObj = objref.Object()
                error_message = "The polysurface has some bad faces. Try removing these with ExtractBadSrf first."
                if not BrepObj.IsValid:
                    print error_message
                    Rhino.UI.Dialogs.ShowMessageBox(error_message, "Bad faces encountered.")
                    rc_valid= False #tag brep has invalid face
                    return [False , objref, -1]
                scriptcontext.doc.Views.Redraw()
                return [rc_valid, objref, 0]
                
    rc_valid, objref, X = selBrep()
    
    if not rc_valid: return [False , objref, -1] # if there is an invalid face bail and return this info to the calling function
    brep = objref.Geometry()
    faces = brep.Faces
    Num_faces = str(faces.Count)
    area = 0
    idx = 0
    n = 0
    Rhino.RhinoApp.SetCommandPrompt ( "Searching for the largest of " + Num_faces + " faces...")
    for face in faces:
        if not face.IsValid: print "No Good"
        #k = face.DuplicateFace(True)
        m = Rhino.Geometry.AreaMassProperties.Compute(face)
        temp_area = m.Area
        if temp_area >= area:
            area = temp_area
            idx = n
        n = n + 1
        
    print  "Largest face area = " + str(round(area,3)), "; Face # ", idx
  #    rs.UnselectAllObjects()
    rc = scriptcontext.doc.Objects.UnselectAll()
    if rc>0: scriptcontext.doc.Views.Redraw()
    fast_highlight_selected_faces(objref.Object(), [idx])
    
    X = objref.Object().GetHighlightedSubObjects()[0]
    return   rc_valid, objref, X

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def ExtractTangentFaces():
    def get_selection():
        
        #Get the input face selection and the angle tolerance and Copy and Join 
        #options from the user. A typed number should be interpreted as angle tolerance.
        # return the settings and the selected face objref and brep ID.
        
        # default tolerance:
        a_tol = scriptcontext.doc.ModelAngleToleranceDegrees
        
        # retrieve a previously used number if any
        if scriptcontext.sticky.has_key("tol_old"):
            a_tol = scriptcontext.sticky["tol_old"]
            
        #Set up the three options
        boolOptionDup = Rhino.Input.Custom.OptionToggle(False, "No", "Yes")
        boolOptionJoin = Rhino.Input.Custom.OptionToggle(True, "No", "Yes")
        tolOption = Rhino.Input.Custom.OptionDouble(a_tol)
        #autoOption = Rhino.Input.Custom.GetOption.AddOption("AutoSelectStartingFace")
        
        #set up the getter and add options
        gs = Rhino.Input.Custom.GetObject()
        
        gs.SetCommandPrompt("Select a starting face in a polysurface.")
        gs.AddOption("LargestFace")
        gs.AddOptionDouble("AngleTolerance", tolOption)
        gs.AddOptionToggle("Copy", boolOptionDup)
        gs.AddOptionToggle("JoinOutput", boolOptionJoin)
        
        #add a geometry filter for the getter
        gs.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
        gs.SubObjectSelect = True
        
        #accept a typed number, if any, to be retrieved as angle tolerace
        gs.AcceptNumber(True, False)
        
        blnCopy = False
        blnJoin = True
        objref = None
        rc_valid=True
        
        while True:
            # perform the get operation. 
            get_rc = gs.Get()
            
            if gs.CommandResult()!=Rhino.Commands.Result.Success:
                return gs.CommandResult()
                
            if get_rc==Rhino.Input.GetResult.Object:
                objref = gs.Object(0)
                StartIdx = objref.GeometryComponentIndex
                scriptcontext.doc.Views.Redraw()
              
            elif get_rc==Rhino.Input.GetResult.Option:
                a_tol = tolOption.CurrentValue
                # save the value for use in the future
                scriptcontext.sticky["tol_old"] = a_tol
                blnCopy = boolOptionDup.CurrentValue
                blnJoin = boolOptionJoin.CurrentValue
                selected_index = gs.Option().Index
                
                if selected_index == 1:
                     rc_valid, objref, StartIdx = FindLargestFace()
                     if not objref or not rc_valid: return False
                     break
                continue
                
            elif get_rc == Rhino.Input.GetResult.Number:
                a_tol = gs.Number()
                # save the value for use in the future
                scriptcontext.sticky["tol_old"] = a_tol
                blnCopy = boolOptionDup.CurrentValue
                blnJoin = boolOptionJoin.CurrentValue
                tolOption = Rhino.Input.Custom.OptionDouble(a_tol)
                continue
            break
       
        return ( rc_valid, objref, StartIdx, a_tol, blnCopy, blnJoin )

    input = get_selection()
    #print input.GetType()
    if input.GetType() != tuple: return
    
    if input[0] == False: return #invalid brep or no selection
    
    rc_valid, objref, StartIdx, a_tol, blnCopy, blnJoin = input
    if not rc_valid: return
    if objref: BrepObj = objref.Object() # the parent Brep

    if not BrepObj: return Rhino.Commands.Result.Failure
    
    #StartIdx = objref.GeometryComponentIndex  #ComponentIndex
    #idx = StartIdx.Index
    Rhino.DocObjects.BrepObject.HighlightSubObject( BrepObj, StartIdx, True )

    # check for bad faces
    if not BrepObj.IsValid:
        print "The polysurface has some bad faces. Try removing these with ExtractBadSrf first."
        Rhino.UI.Dialogs.ShowMessageBox("The polysurface has some bad faces. Try removing these with ExtractBadSrf first.", "Bad faces encountered.")#, buttons: MessageBoxButtons, icon: MessageBoxIcon, defaultButton: MessageBoxDefaultButton)
        return Rhino.Commands.Result.Failure
        
    id = objref.ObjectId
    Ext = False
    k = Rhino.DocObjects.BrepObject.GetType(BrepObj)
    
    #if it's an extrusion-
    if k.Name == "ExtrusionObject":
        ExtId = k.GUID
        Ext = True
    #create a brep object from the extrusion
        NewBrep = Rhino.Geometry.Extrusion.ToBrep(BrepObj.Geometry,True)
        BrepId = scriptcontext.doc.Objects.AddBrep(NewBrep)
        BrepObj = scriptcontext.doc.Objects.Find(BrepId)
        rs.MatchObjectAttributes(BrepId ,id)
        new_objref = Rhino.DocObjects.ObjRef(BrepId)
        scriptcontext.doc.Objects.Hide(id, False)
        fast_highlight_selected_faces ( BrepObj, [idx] )
        print Rhino.DocObjects.BrepObject.HighlightSubObject( BrepObj, StartIdx, True )
        #BrepObj =
    
    else:
        BrepObj =scriptcontext.doc.Objects.Find(id)
        
    BrepObj.UnselectAllSubObjects()
    
    testingBrep = BrepObj.Geometry
    #FindLargestFace()
    
    brepIds = ExtractAdjacentTangentFaces(BrepObj, StartIdx.Index, a_tol, blnCopy, blnJoin)
    if Ext:
        scriptcontext.doc.Objects.Show(id, False)
        scriptcontext.doc.Objects.Delete(BrepId, True)
         
         
    if brepIds:
        
        #--------------------------------------------------
        #--------------------------------------------------
        
        #     # Use this if removing faces from input Brep
        #    if breps[0]:
        #        new_id = scriptcontext.doc.Objects.AddBrep(breps[0])
        #        rs.MatchObjectAttributes(new_id, ID)
        #--------------------------------------------------
        # Use this if rebuilding breps in my own function
        if brepIds[0]:
            for item in brepIds[0]:
                rs.MatchObjectAttributes(item,id)
        #--------------------------------------------------
        #--------------------------------------------------
            
        if brepIds[0]:
                       
          for item in brepIds[0]:
              rs.MatchObjectAttributes(item,id)
              if Ext:
                  temp = scriptcontext.doc.Objects.Find(item)
                  temp.Attributes.WireDensity = 1
                  temp.CommitChanges()
            
            
        if brepIds[1]:
            for item in brepIds[1]:
                rs.MatchObjectAttributes(item,id)
            if Ext:
                temp = scriptcontext.doc.Objects.Find(item)
                temp.Attributes.WireDensity = 1
                temp.CommitChanges()
                
        if not blnCopy: 
            if brepIds[0] or brepIds[1]: scriptcontext.doc.Objects.Delete(id, True)

        scriptcontext.doc.Objects.UnselectAll()
        
        for new_id in brepIds[1]:
            rhObj = scriptcontext.doc.Objects.Find(new_id)

            if rhObj: rhObj.Select(True)

    scriptcontext.doc.Views.Redraw()
    return Rhino.Commands.Result.Success
    
    
ExtractTangentFaces()