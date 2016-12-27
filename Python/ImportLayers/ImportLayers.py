import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

def ImportSomeLayers(Layers, Title):
    layerStates = [(layer,False) for layer in Layers]
    importLayers = rs.CheckListBox(layerStates, "Select layers to import",Title)
    if importLayers is None: return
    for n in range(len (Layers)):
        if importLayers[n][1]:
            sc.doc.Layers.Add(Layers[n])
            
            
def ImportSomeMaterials(Materials, Title):
    matStates = [(mat,False) for mat in Materials]
    importMats = rs.CheckListBox(matStates, "Select materials to import",Title)
    if importMats is None: return
    for n in range(len (importMats)):
        if importMats[n][1]:
            
            sc.doc.Materials.Add(Materials[n])
            
def ImportSomeDimStyles(Styles, Title):
    
    styleStates = [(style,False) for style in Styles]
    importStyles = rs.CheckListBox(styleStates, "Select DimStyles to import",Title)
    if importStyles is None: return
    for n in range(len (Styles)):
        if importStyles[n][1]:
            sc.doc.DimStyles.Add(Styles[n])
            
def ImportSomeHatches(Hatches, Title):
    
    hatchStates = [(hatch.Name,False) for hatch in Hatches]
    importHatches = rs.CheckListBox(hatchStates, "Select hatch patterns to import",Title)
    if importHatches is None: return
    for n in range(len (Hatches)):
        if importHatches[n][1]:
            sc.doc.HatchPatterns.Add(Hatches[n])  
            
def ImportSomeViews(Views, Title):
    
    viewStates = [(view.Name,False) for view in Views]
    importViews = rs.CheckListBox(viewStates, "Select named views to import",Title)
    if importViews is None: return
    for n in range(len (Views)):
        if importViews[n][1]:
            sc.doc.NamedViews.Add(Views[n])
    
    #    
    #def ImportSomeCPlanes(Planes, Title):
    #    
    #    planeStates = [(plane,False) for plane in Planes]
    #    importPlanes = rs.CheckListBox(planeStates, "Select named CPlanes to import",Title)
    #    if importPlanes is None: return
    #    for n in range(len (Planes)):
    #        if importPlanes[n][1]:
    #            sc.doc.NamedCPlanes.Add(Planes[n])
            
            
def ImportNotes(Notes, Title):
    q =Notes.Notes 
    crnt = sc.doc.Notes
    if (q) is not None:
        print q
        b = Rhino.RhinoDoc.Notes
        sc.doc.Notes = crnt + "\n \n" + q
        
        
        
def SortObjects(Objects):
    pass
    n = 0
    extrusions = []
    breps = []
    srfs = []
    curves = []
    meshes = []
    for object in Objects:
        
        x = object.Geometry.ObjectType
        attr = object.Attributes
        name = object.Name
        
        if  x == Rhino.DocObjects.ObjectType.Extrusion:
            extrusions.append((object.Geometry, attr))
            print "EXTRUSION"
            
        elif x == Rhino.DocObjects.ObjectType.Brep:
            breps.append((object.Geometry, attr))
            print "BREP"
            if object.Geometry.Faces.Count == 1:
                print "SRF"
                srfs.append(breps.pop())
                if object.Geometry.IsSolid:
                    print "CLOSED SRF"
                else:
                    print "OPEN SRF"
        elif x == Rhino.DocObjects.ObjectType.Curve:
            #print "CURVE"
            curves.append((object.Geometry, attr))
            if object.Geometry.IsClosed:
                print "CLOSED CURVE"
            else:
                print "OPEN CURVE"
       
        elif x == Rhino.DocObjects.ObjectType.Mesh:
            meshes.append((object.Geometry, attr))
            if object.Geometry.IsClosed:
                print "CLOSED MESH"
            else:
                print "OPEN MESH"
            pass

        n = n + 1
    return (curves, breps, extrusions, srfs, meshes)

    pass

def test():
    Title = "SelectiveImport"
    file= rs.OpenFileName("Import layers", extension="3dm")
    if not file: return
    x = Rhino.FileIO.File3dm.Read(file)
    if x is None: return
    
    things = ["Layers", "Materials", "DimStyles", "HatchPatterns", "Views", "Notes", "Curves", "Extrusions", "Surfaces", "Polysurfaces", "Meshes"]
    thingStates =  [(thing,False) for thing in things]
    
    if sc.sticky.has_key("ThingStates"):
        thingStates = sc.sticky["ThingStates"]
    
    importThings = rs.CheckListBox(thingStates, "Select items to import", Title)
    if importThings is None: return
    sc.sticky["ThingStates"] = importThings
    
    geoList = SortObjects(x.Objects)
    
    for n in range(len(things)):
        if importThings[n][1]:
            if n == 0:
                ImportSomeLayers(x.Layers, Title)
            elif n ==1:
                ImportSomeMaterials(x.Materials, Title)
            elif n==2:
                ImportSomeDimStyles(x.DimStyles, Title)
            elif n == 3:
                ImportSomeHatches(x.HatchPatterns, Title)
            elif n == 4:
                q = x.HatchPatterns
                ImportSomeViews(x.NamedViews, Title)
            elif n == 5:
                if x.Notes.Notes is not None:
                    string = ImportNotes(x.Notes, Title)
            elif n == 6:
                if len(geoList[0]) !=0:
                    for geo in geoList[0]:
                        sc.doc.Objects.AddCurve(geo[0])
            elif n == 7:
                if len(geoList[1]) !=0:
                    for geo in geoList[1]:
                        sc.doc.Objects.AddBrep(geo[0])
            elif n == 8:
                if len(geoList[2]) !=0:
                    for geo in geoList[2]:
                        sc.doc.Objects.AddExtrusion(geo[0])
            elif n == 9:
                if len(geoList[3]) !=0:
                    for geo in geoList[3]:
                        sc.doc.Objects.AddBrep(geo[0])
            elif n == 10:
                if len(geoList[4]) !=0:
                    for geo in geoList[4]:
                        
                        temp = sc.doc.Objects.AddMesh(geo[0])
                        item = sc.doc.Objects.Find(temp)
                        item.Attributes = geo[1]
                        pass
                    

    #            elif n ==8: 
    #                ImportInstanceDefinitions(x.InstanceDefinitions, Title)
                
    sc.doc.Views.Redraw()
            
      
test()