def curve_end(crv, par):
    h_length = crv.GetLength()/2
    test_pt = crv.PointAtLength(h_length)
    rc, h_par = crv.ClosestPoint(test_pt)
    end = 0
    if par > h_par: end = 1
    return end