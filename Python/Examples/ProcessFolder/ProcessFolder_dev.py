import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import os


def PrintLayoutsToPDF():
    if sc.sticky.has_key("PrintFolder"):
        defFolder = sc.sticky["PrintFolder"]
    else:
        defFolder = rs.WorkingFolder()
    folder = rs.BrowseForFolder(folder = defFolder, message= "Folder to process", title="Print all layouts")
    
    if folder is None: return
    sc.sticky["PrintFolder"] = folder
    
    files = os.listdir(folder)
    if files is None:
        print "No 3dm files found in " + folder
        return
    
    printerName = "Microsoft Print to PDF"
    
    rList = []
    for file in files:
        file = os.path.normcase(file)
        #print file
        if os.path.splitext(file)[1] == ".3dm":
            rList.append(chr(34) + folder + "\\" + file + chr(34))
    if len(rList) == 0: return
    
    for file in rList:
        layout = False
        rs.Command ("~-_Open " + file + " Enter", False)
        views = sc.doc.Views
        for view in views:
            pass
            if type(view) == Rhino.Display.RhinoPageView:
                print file + ": Layouts found"
                layout = True
                break
        if layout:
            rs.Command ("~_-Print _Setup _View _AllLayouts _Enter _Destination _Printer " + printerName + " _Enter _Enter _Go " + file.replace("3dm", "pdf")  + " _Enter", False)
        pass

    
    pass
if __name__ == "__main__":
    PrintLayoutsToPDF()