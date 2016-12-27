def FairPtsNormal(Id, apts, aIdx, factor):
    srf = sc.doc.Objects.Find(Id).Geometry.Surfaces[0]
    vec_list = []
    l = 0
    n = 0
    for idx in range(1, len(apts) - 1):
        par = rs.BrepClosestPoint(Id, apts[idx])[1]
        d = rs.EvaluateSurface(Id, par[0], par[1])
        vec =apts[idx]-d
        vec_list.append(vec)
        l = l + vec.Length
        n = n + 1
    fairTol = factor*(l/n)

    curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(apts,3,0)
    #pc = Rhino.Geometry.Curve.ProjectToPlane(curve, plane)
    fc = Rhino.Geometry.Curve.Fair(curve,fairTol,.05,0,0,5)
    #ping = sc.doc.Objects.AddCurve(pc)
    if fc:
        for idx in range(1, len(apts) - 1):
            test  = apts[idx]
            #grip closest point paranmeter on the faired curve:
            par = fc.ClosestPoint(test,0.0)
            # closest 3d point:
            temp = fc.PointAt(par[1])
            #temp closest point parameter on the surface:
            par = rs.SurfaceClosestPoint(Id,temp)
            #temp's closest 3d point on the surface
            p1 = rs.EvaluateSurface(Id,par[0], par[1] )
            #Distance from temp to the surface
            d1 = rs.Distance(temp,p1)
            #grip closest point parameter on the surface:
            par = rs.SurfaceClosestPoint(Id,test)
            #Nomral at the grip closesyt point:
            vecNorm = rs.SurfaceNormal(Id, par)*d1
            #Location of the normal:
            base = rs.EvaluateSurface(Id, par[0], par[1])
            # a new grip location the same distance from the surface
            # as the faired curve at the same point
            targ = base + vecNorm

            rs.ObjectGripLocation(Id,aIdx[idx], targ)