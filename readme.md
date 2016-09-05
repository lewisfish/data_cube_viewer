#Data Cube Viewer 

Python/Qt program to view a data cube by slicing it up. 

Currently only supports fortran unformatted binary files.
Files have to be written by
open(unit, file = file_name, access='direct', form='unformatted', recl=record_length)

Currently can view from x, y, and z planes. Also can view Average Fluence per layer and boreholes at any position

![Screenshot]
(https://github.com/lewisfish/data_cube_viewer/blob/master/Screenshot.png)

####ToDo

  - Fix bugs
  - Ability to open any fortran unformmated binary file
  - Controlable colorbars
  - non-square data cubes
  - more...


