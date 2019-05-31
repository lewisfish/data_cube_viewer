import numpy as np


class datacube(object):
    """docstring for datacube"""
    def __init__(self):
        super(datacube, self).__init__()
        self.name = None
        self.ndim = None
        self.dtype = None
        self.cubeorder = None
        self.data = np.array([])

    def readslice(self, *args):
        data = np.fromfile(file=self.name, dtype=self.dtype, sep="")
        data = data.reshape(self.ndim, order='F')
        if self.cubeorder == 4:
            data = data[:, :, :, max(args[0], 0)]
        self.data = data[:, :, :]
        del data

    def is_perfect_n(self, x, n):
        # shitty cheat so i dont have to enter numbers... sometimes dosent work
        x = abs(x)
        p = x ** (1. / n)
        if int(round(p)) ** n == x:
            return int(round(p))
        else:
            return 0


if __name__ == '__main__':
    import numpy as np
    import os

    filename = "rhokap.raw"
    x = datacube(filename)
    x.ndim = (160, 160, 160)
    x.dtype = np.float64
    x.cubeorder = 3
    p = os.path.getsize(x.name)
    p /= 8
    y = x.readslice()
    print(x.is_perfect_cube(p))
