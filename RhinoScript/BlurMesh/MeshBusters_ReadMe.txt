MeshBusters

To use the scripts, *extract and save* the .rvb files, then drag and drop them  over an open V4 window to add the following aliases:

BlurMesh
BlurMeshVariable
Halo


These can be used as a 'commands' by typing or by adding to a button.

-----

BlurMesh:

is the simplest- you select a mesh and give the script a maximum blur
amount- a distance in current model units, then tell the script how you
want the output:

    Smoothed = All welded up

    Faceted = completely unwelded, like FlatShade

    Gappy = The polygons do not stay together at all but blow apart when
they get blurred. The end result is a single mesh however.

With Smoothed on something like a mesh box, you might want to Unweld
after the fact at 60 or 80 degrees maybe to re-sharpen the edges.

-----

BlurMeshVariable:

testing some stuff... it's like BlurMesh but allow the amount of blur
to be varied in a different ways:

    X/Y/ZDirection- the blur will increase linearly from zero to the
requested amount along the positive direction of the relevant axis. Not
all that useful I think, it was in there mostly to test with.

    AlongCurve: Varies the amount of blur from zero at the beginning of the
curve to maximum at the end. This is a little more versatile than X/Y/Z.

    ProfileCurve: Currently this uses a curve drawn in WorldXY plane only.
The amount of blur varies with the distance of the curve from the X
axis. The curve is mapped to the length in CplaneX of the mesh.Basically
it means you can control the location and amount of the blur in one
direction.

    Distance: Varies the blur with distance, actually the inverse distance
for now, from a point, curve, or surface. The farther a mesh vertex is
from this geometry, the less it is blurred. The script will prompt for a
radius- any mesh points outside the radius are not moved. This is
actually probably the most useful so far.

-----

Halo:
one trick pony- makes a new mesh of sorts (or points, up to you) based
on a closed surface or polysurface. Polys are added according to a
radius from the surface until the maximum number entered by the user is
reached. This thing is dumb and slow, so go easy on the numbers- 10,000
or less is all I'd use until you see what it does and decide if it
actually does anything at all useful.

All settings guaranteed remembered. =)
Per session. I think.




Have fun, I'm sure there is a ton of stuff you'll find wrong but I
don't think it will crash or anything- that said, save your work, I
don't necessarily know what I'm doing.