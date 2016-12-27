
import scriptcontext as sc
import System


def vp_size():
    
    view = sc.doc.Views.ActiveView
    
    rect = view.ScreenRectangle
    width_in_pixels = rect.Width
    height_in_pixels = rect.Height
    
    graphics = System.Drawing.Graphics.FromHwnd(System.IntPtr.Zero)
    pixels_per_inch_x = graphics.DpiX
    pixels_per_inch_y = graphics.DpiY
    
    width_in_inches = width_in_pixels/pixels_per_inch_x
    height_in_inches = height_in_pixels / pixels_per_inch_y
    
    mm_per_inch = 25.4
    width_in_mm = width_in_inches * mm_per_inch
    height_in_mm = height_in_inches * mm_per_inch
    
    name = view.ActiveViewport.Name
    print name,"view width:",  str(width_in_mm), "mm"
    print name, "view height:",  str(height_in_mm), "mm"


vp_size()