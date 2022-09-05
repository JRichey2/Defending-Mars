from struct import Struct
from math import sqrt, sin, cos, radians, atan2, degrees

__all__ = ['V2', 'V3']


class V3:
    'Simple 3D vector type that does what you expect'

    __slots__ = ['x', 'y', 'z']
    packer = Struct('ddd')

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return "{}({:.3f}, {:.3f}, {:.3f})".format(self.__class__.__name__,
                                                   self.x, self.y, self.z)

    @classmethod
    def from_bytes(cls, packed_bytes):
        '''Creates a new vector from a bytes object that is
            in the format created by calling bytes(...) on
            an instance of a V3.

            a = V3(10, 20, 30)
            packed_bytes = bytes(a)
            b = V3.from_bytes(packed_bytes)
            assert a == b

        '''
        x, y, z = cls.packer.unpack(packed_bytes)
        return cls(x, y, z)

    def __bytes__(self):
        return self.packer.pack(self.x, self.y, self.z)

    def __eq__(self, other):
        if abs(self.x - other.x) > 0.0001:
            return False
        elif abs(self.y - other.y) > 0.0001:
            return False
        elif abs(self.z - other.z) > 0.0001:
            return False
        else:
            return True

    def __add__(self, other):
        return self.__class__(self.x + other.x,
                              self.y + other.y,
                              self.z + other.z)

    def __sub__(self, other):
        return self.__class__(self.x - other.x,
                              self.y - other.y,
                              self.z - other.z)

    def __mul__(self, other):
        return self.__class__(self.x * other,
                              self.y * other,
                              self.z * other)

    def __truediv__(self, other):
        return self.__class__(self.x / other,
                              self.y / other,
                              self.z / other)

    def __getitem__(self, key):
        '''Allows vec[0] to provide the x component
            and vec[1] to provide the y component.
            this will be slower than using obj.x or obj.y'''
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            message = "Cannot get the {}th item".format(key)
            raise IndexError("3D Vectors only have 3 components, " + message)

    def __setitem__(self, key, value):
        '''Allows vec[0] = x to set the x component
            and vec[1] = y to set the y component'''
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            message = "Cannot set the {}th item".format(key)
            raise IndexError("3D Vectors only have 3 components, " + message)

    def __delitem__(self, key):
        raise NotImplementedError("Cannot remove a component")

    @property
    def copy(self):
        'Makes a copy of the vector'
        return self.__class__(self.x, self.y, self.z)

    @property
    def length(self):
        'The magnitude of the vector'
        x = self.x
        y = self.y
        z = self.z
        return sqrt(x * x + y * y + z * z)

    @length.setter
    def length(self, value):
        scale = value / self.length
        self.x *= scale
        self.y *= scale
        self.z *= scale

    @property
    def length_squared(self):
        'The squared magnitude of the vector.  Fast for length compares'
        x = self.x
        y = self.y
        z = self.z
        return x * x + y * y + z * z

    def normalize(self):
        mag = self.length
        self.x /= mag
        self.y /= mag
        self.z /= mag

    @property
    def normalized(self):
        return self / self.length

    @normalized.setter
    def normalized(self, other):
        other = other.normalized * self.length
        self.x = other.x
        self.y = other.y
        self.z = other.z

    @property
    def x_radians(self):
        return V2(self.y, self.z).radians

    @property
    def x_degrees(self):
        return V2(self.y, self.z).degrees

    @property
    def y_radians(self):
        return V2(self.z, self.x).radians

    @property
    def y_degrees(self):
        return V2(self.z, self.x).degrees

    @property
    def z_radians(self):
        return V2(self.x, self.y).radians

    @property
    def z_degrees(self):
        return V2(self.x, self.y).degrees

    def __neg__(self):
        return self.__class__(-self.x, -self.y, -self.z)

    def __pos__(self):
        return self.__class__(self.x, self.y, self.z)

    def __abs__(self):
        return self.length

    def __hash__(self):
        return hash(hash(self.x) + hash(self.y) + hash(self.z))

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __reversed__(self):
        yield self.z
        yield self.y
        yield self.x

    def __contains__(self, item):
        'Returns true if either component matches the item'
        if abs(self.x - item) < 0.0001:
            return True
        elif abs(self.y - item) < 0.0001:
            return True
        elif abs(self.z - item) < 0.0001:
            return True
        else:
            return False

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def write(self, writable):
        'Writes itself to the file-like object passed in as binary'
        return writable.write(bytes(self))


class V2:
    'Simple 2D vector type that does what you expect'

    __slots__ = ['x', 'y']
    packer = Struct('dd')

    def __init__(self, x=0.0, y=0.0):
        '''Most efficient way to make a V2: from x and y

            # (0.0, 0.0)
            a = V2()

            # (10, 0.0)
            b = V2(x=10)

            # (0.0, 10.0)
            c = V2(y=10)

            # (3.0, 4.0)
            d = V2(3.0, 4.0)
        '''
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def from_degrees_and_length(cls, angle, length):
        '''Creates a new vector from an angle in degrees and a length

            # (10.0, 0.0)
            V2.from_degrees_and_length(0, 10.0)

            # (0.707, 0.707)
            V2.from_degrees_and_length(45, 10.0)
        '''
        angle = radians(angle)
        x = cos(angle) * length
        y = sin(angle) * length
        return cls(x, y)

    @classmethod
    def from_radians_and_length(cls, angle, length):
        '''Creates a new vector from an angle in radians and a length

            # (10.0, 0.0)
            V2.from_radians_and_length(0, 10.0)

            # (0.707, 0.707)
            Vecor.from_radians_and_length(pi / 4, 1.0)
        '''
        x = cos(angle) * length
        y = sin(angle) * length
        return cls(x, y)

    @classmethod
    def from_bytes(cls, packed_bytes):
        '''Creates a new vector from a bytes object that is
            in the format created by calling bytes(...) on
            an instance of a V2.

            a = V2(10, 20)
            packed_bytes = bytes(a)
            b = V2.from_bytes(packed_bytes)
            assert a == b

        '''
        x, y = cls.packer.unpack(packed_bytes)
        return cls(x, y)

    def __repr__(self):
        return "{}({:.3f}, {:.3f})".format(self.__class__.__name__,
                                           self.x, self.y)

    def __bytes__(self):
        return self.packer.pack(self.x, self.y)

    def __add__(self, other):
        return self.__class__(self.x + other.x,
                              self.y + other.y)

    def __sub__(self, other):
        return self.__class__(self.x - other.x,
                              self.y - other.y)

    def __mul__(self, other):
        return self.__class__(self.x * other,
                              self.y * other)

    def __truediv__(self, other):
        return self.__class__(self.x / other,
                              self.y / other)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __itruediv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    def __pos__(self):
        return self.__class__(+self.x, +self.y)

    def __abs__(self):
        return self.length

    def __eq__(self, other):
        if abs(self.x - other.x) > 0.0001:
            return False
        elif abs(self.y - other.y) > 0.0001:
            return False
        else:
            return True

    def __hash__(self):
        return hash(hash(self.x) + hash(self.y))

    def __bool__(self):
        return True

    def __getitem__(self, key):
        '''Allows vec[0] to provide the x component
            and vec[1] to provide the y component.
            this will be slower than using obj.x or obj.y'''
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            message = "Cannot get the {}th item".format(key)
            raise IndexError("2D Vectors only have 2 components, " + message)

    def __setitem__(self, key, value):
        '''Allows vec[0] = x to set the x component
            and vec[1] = y to set the y component'''
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            message = "Cannot set the {}th item".format(key)
            raise IndexError("2D Vectors only have 2 components, " + message)

    def __delitem__(self, key):
        raise NotImplementedError("Cannot remove a component")

    def __iter__(self):
        yield self.x
        yield self.y

    def __reversed__(self):
        yield self.y
        yield self.x

    def __contains__(self, item):
        'Returns true if either component matches the item'
        if abs(self.x - item) < 0.0001:
            return True
        elif abs(self.y - item) < 0.0001:
            return True
        else:
            return False

    @property
    def length(self):
        'The magnitude of the vector'
        x = self.x
        y = self.y
        return sqrt(x * x + y * y)

    @length.setter
    def length(self, value):
        'Sets the magnitude of the vector'
        current = self.length
        self *= (value / current)

    @property
    def length_squared(self):
        'The squared magnitude of the vector.  Fast for length compares'
        x = self.x
        y = self.y
        return x * x + y * y

    def normalize(self):
        'Grows or Shrinks the vector to a size of 1.0 but maintains angle'
        self.length = 1

    @property
    def normalized(self):
        'Returns a normalized copy of the vector'
        return self / self.length

    @normalized.setter
    def normalized(self, value):
        '''Ensures the vector, when normalized, will match the normalized
            version of the vector povided'''
        self.radians = value.radians

    @property
    def degrees(self):
        'Returns the angle of the vector in degrees'
        return degrees(self.radians)

    @degrees.setter
    def degrees(self, value):
        'Sets the angle of the vector in degrees'
        self.radians = radians(value)

    @property
    def radians(self):
        'Returns the angle of the vector in radians'
        return atan2(self.y, self.x)

    @radians.setter
    def radians(self, value):
        'Sets the angle of the vector in radians'
        new_v = self.__class__.from_radians_and_length(value, self.length)
        self.x = new_v.x
        self.y = new_v.y

    @property
    def copy(self):
        'Makes a copy of the vector'
        return self.__class__(self.x, self.y)

    def dot_product(self, other):
        'Returns the dot product'
        return self.x * other.x + self.y * other.y

    @property
    def x_vector(self):
        'Returns a vector with only the x component'
        return self.__class__(self.x, 0)

    @property
    def y_vector(self):
        'Returns a vector with only the y component'
        return self.__class__(0, self.y)

    @property
    def mirror(self):
        'A copy of the vector mirrored over x and y. same as * -1 or -obj'
        return -self

    @property
    def mirror_x(self):
        'A copy of the vector mirrored over the x axis'
        return self.__class__(self.x, -self.y)

    @property
    def mirror_y(self):
        'A copy of the vector mirrored over the y axis'
        return self.__class__(-self.x, self.y)

    def write(self, writable):
        'Writes itself to the file-like object passed in as binary'
        return writable.write(bytes(self))

