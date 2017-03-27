# Data Cube Viewer 

Python/Qt program to view a data cube by slicing it up. 

Currently only supports fortran unformatted 3/4D binary files and formatted 2D files.
Files have to be written by
open(unit, file=file_name, access='direct', form='unformatted', recl=record_length)
write(unit, rec=1)

Currently can view Fluence and Avgerage fluence per layer from x, y, and z planes. Also can view boreholes at any position.
Can save plots of average fluence and gifs of slices.

![Screenshot](https://github.com/lewisfish/data_cube_viewer/blob/master/Screenshot.png)

## Requires
Matplotlib

PyQt4

#### ToDo

  - Fix bugs(memory leak??)
  - Ability to open any fortran unformmated binary file
  - Controlable colorbars(partially done with autoscale)
  - Save data from whats on screen(partially done with gif making and saving of boreholes)
  - more...
