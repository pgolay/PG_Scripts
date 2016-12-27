import os
import glob
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import itertools


def test():
    crntVersion = rs.ExeVersion()
    folder = rs.BrowseForFolder(rs.WorkingFolder(),"Select folder to process")
    if folder is None: return
    
    #    files = os.listdir(folder)
    #    print files

    files =  glob.glob(folder+"\*.igs") + glob.glob(folder+"\*.stp")
    pass
   
    if not files:
        print "None"
        return
    n = 0



    rs.EnableRedraw(False)
    for file in files:
        if n <10:
            rs.Command("_-Open " +chr(34) + file +chr(34) + " _Enter")
            layouts  = sc.doc.Views.GetViewList(False, True)
                    
            if len(layouts) ==0:
                rs.Command("_-Layout _Enter 279.4 215.9 4 ")
                
            layouts  = sc.doc.Views.GetViewList(False, True)
            x = layouts[0].PageName
            LayoutId  = layouts[0].ActiveViewportID
            rs.CurrentView(LayoutId)
            dets = layouts[0].GetDetailViews()
            Ids = [det.Id for det in dets]
            for Id in Ids:
                rs.CurrentDetail(LayoutId, Id)
                rs.Command ("SetDisplayMode Rendered")
            pass
             
            #rs.Command("_-Print _Setup _Destination _Printer " + chr(34)+"CutePDF Writer"+ chr(34) + " _OutputType=Raster _View _Viewport " + chr(34) +x +chr(34) + " _ScaleToFit _Enter _Enter _Go _Enter Enter")
            rs.Command ("_-Save _Version=" + str(crntVersion) + " _Enter _Enter" )
        n = n +1
        
    rs.Command ("-_New _None ")
    rs.EnableRedraw(True)

    
if __name__ == "__main__":
    test()