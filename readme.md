# Data Cube Viewer 

Python/Qt program to view a data cube by slicing it up. 

Currently only supports fortran unformatted 3/4D binary files and un/formatted 2D files.
Files have to be written by:

open(unit, file=file_name, access='direct', form='unformatted', recl=record_length)

write(u,recl=1)array

or

open(unit, file=file_name, access='stream', form='unformatted)

write(u)array

Currently can view Fluence and Avgerage fluence per layer from x, y, and z planes. Also can view boreholes at any position.
Can save plots of average fluence, images, raw data and gifs of slices.
Ability to change colour map of plot, clip colourbar, interpolation method and the normalisation method (currently just Log, Linear or symmetric law).

![Screenshot](https://github.com/lewisfish/data_cube_viewer/blob/master/Screenshot.png)

## Requires

Python >= 3.5

Matplotlib >= 1.5

PyQt5

For gif/video making need:

ImageMagick >= 6.7.7-10

ffmpeg >= 2.8.15 

#### ToDo

  - [ ] Fix bugs
  - [x] Fixed memory leak
  - [ ] Ability to open any fortran unformmated binary file
  - [x] Controlable colorbars(partially done with autoscale)
  - [x] Save data from whats on screen(partially done with gif making and saving of boreholes)
  - [ ] more...
