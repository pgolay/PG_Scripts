ProjectObjects

To use the script, extract and save the .rvb file from the attached zip archive, then drag and drop the saved rvb over an open Rhino V4 or v5 window. This will load the script, set it up to load on startup in the future and register an alias 

ProjectObjects

that will run the script much like a regular command. The alias can be typed or added to a toolbar button or keyboard shortcut (F-key).

Notes:

1. The script uses the bounding box of the object in the current Cplane. If in plan view of the current cplane, any of the bounding box of the projected object is not contained in the view of the target object, the tool will fail.

2. The tool works best if there is only one target pssible- for example, projecting to a sphere may lead to strange results because the tool is too dumb at the moment to distinguish between the near side of the sphere and the far side - it may try to hit some of each, or the wrong side.

3. Use Density in X and Y (clamped to 40 in each direction) to increase the 'resolution' of the projected objects- if the target is only slightly curved, usse lower numbers, if there is high curvature or small details to conform to on the target, use higher numbers.

