import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import System.Windows.Forms as wf


def test():
    
    Id = rs.GetObject()
    obj = sc.doc.Objects.Find(Id)
    idx = obj.Attributes.MaterialIndex
    #test = rs.MaterialTexture(0)
    mats = sc.doc.Materials
    tex = mats[0].GetBitmapTexture()
    file = mats[idx].GetBitmapTexture().FileName
    rmats = sc.doc.RenderMaterials
    
    if file is not None:
        sc.doc.Bitmaps.AddBitmap(file, True)
    pass
test()