import unittest
from collections import namedtuple
from numpy import array

# define QuadForm = ax^2 + bxy + cy^2
QuadForm = namedtuple('QuadForm', ['a', 'b', 'c'])

# links
# http://oeis.org/A000924
# https://mathworld.wolfram.com/ClassNumber.html
# https://www.springer.com/gp/book/9780387970370
# https://arxiv.org/pdf/1704.00902.pdf
# http://zakuski.utsa.edu/~jagy/indefinite_binary_Buell.pdf


# reduced form |b| <= a <= c
# discriminant = b^2 - 4ac
# if discriminant = -D
# then only a finite amount of reduced forms. This is the class number
# Proof:
# 4b^2 <= 4ac = b^2 + D
# => 3b^2 <= D
# b <= sqrt(D/3)

class QuadraticForm:
    S = array([[0, -1], [1, 0]])
    T = array([[1, 1], [0, 1]])

    def __init__(self, a, b, c):
        self.f = QuadForm(a=a, b=b, c=c)

    def discriminant(self):
        """Return the discriminant"""
        return self.f.b**2 - 4 * self.f.a * self.f.c

    def matrix_form(self):
        """
        Return matrix
        A = [ a , b/2]
            [b/2,  c ]
        """
        return array([[self.f.a, self.f.b/2], [self.f.b/2, self.f.c]])

    def is_reduced(self):
        """
        Return boolean if quadratic form is in reduced state.
        Reduced is defined as:
        D = discriminant
        if D > 0:
           0 < b < sqrt(D)
           and
           sqrt(D) - b < 2 |a| < sqrt(D) + b
        if D < 0:
           |b| <= a <= c

        # todo see if these are equivalent to
        # -|a| < b <= |a| or 0 <= b <= |a| = |c|

        another definition:
        if |b| ≤ a ≤ c, and b ≥ 0 if either a = c or |b| = a
        """
        # D = self.discriminant()

        def third():
            condition_1 = - abs(self.f.a) < self.f.b <= abs(self.f.a)
            condition_2 = 0 <= self.f.b <= abs(self.f.a)
            condition_3 = abs(self.f.a) == abs(self.f.c)

            return condition_1 or (condition_2 and condition_3)

        def first():
            """
            if D < 0 then |b| <= a <= c
            if D > 0 then 0 < b < sqrt(D) and sqrt(D) - b < 2|a| < sqrt(D) + b
            """
            D = self.discriminant()
            if D < 0:
                return abs(self.f.b) <= self.f.a <= self.f.c
            elif D > 0:
                sr_D = D**0.5
                cond_1 = 0 < self.f.b < sr_D
                cond_2 = sr_D - self.f.b < 2 * abs(self.f.a) < sr_D + self.f.b
                return cond_1 and cond_2
            else:
                raise NotImplementedError("D cannot be 0, yet.")

        # return third()
        return first()

    def reduce(self):
        """
        Return a reduced form
        """
        pass

    def adjacent(self):
        pass

    def form(self):
        """Returns if form is indefinite or definite"""
        pass

    def __str__(self):
        return f'a: {self.f.a}, b: {self.f.b}, c: {self.f.c}'


def factors_of_n(n):
    """Given an <int> n, return list of tuples of positive integers that multiply to n"""
    assert isinstance(n, int)
    assert n > -1
    ls_out = [(1, n)]
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            ls_out.append((i, n//i))
    return ls_out


def get_reduced_forms(D, debug=False, old=False):
    """Given an <int> D, computes all reduced forms of discriminant = -D of the binary quadratic form"""
    abs_b_max = int((D / 3) ** 0.5)
    if debug:
        print(f'max_abs_b: {abs_b_max}')
    ls_potential_reduced_quad_forms = []
    for b in range(abs_b_max + 1):
        # temp = 4ac = b^2 + D
        b2 = b ** 2
        temp = b2 + D
        if temp % 4 != 0:
            continue
        else:
            # temp = ac
            temp = temp // 4
            # ac >= b^2
            ls_fac = factors_of_n(temp)
            for fac_tup in ls_fac:
                if not old:
                    quad_form = QuadraticForm(a=fac_tup[0], b=b, c=fac_tup[1])
                    if quad_form.is_reduced():
                        ls_potential_reduced_quad_forms.append(quad_form)
                        if debug:
                            print(quad_form)
                    quad_form = QuadraticForm(a=fac_tup[0], b=-b, c=fac_tup[1])
                    if quad_form.is_reduced():
                        ls_potential_reduced_quad_forms.append(quad_form)
                        if debug:
                            print(quad_form)
                if old:
                    quad_form = QuadraticForm(a=fac_tup[0], b=b, c=fac_tup[1])
                    if fac_tup[0] >= b and fac_tup[1] >= b:
                        # todo keep list of reduced forms, to check that these new forms are not reduced
                        # example (a,b,c) = (1, -1, 12) ~ (1, 1, 12) through using multiplication of T
                        # T = (1, 1)
                        #     (0, 1)
                        # Where A = ( a , b/2)
                        #         = (b/2,  c )
                        # A' = T^t * A * T
                        # print(b, b2, temp, fac_tup)
                        ls_potential_reduced_quad_forms.append(quad_form)
                        if debug:
                            print(quad_form)

        # todo implement reduce solutions method which removes multiples of S and T
        # S = (0, -1)   T = (1, 1)    , since SL2(Z) = <S, T>
        #     (1,  0)       (0, 1)

    return ls_potential_reduced_quad_forms


def get_class_number(D, debug=False, old=False):
    """Given an <int> D, computes the class number of discriminant = -D of the binary quadratic form"""
    ls_reduced = get_reduced_forms(D, debug=debug, old=old)
    # todo filter some reduced forms, see example with D = 47
    return len(ls_reduced)


def get_negative_class_type(max_n, cn):
    ls_out = []
    print(f'---CLASS NUMBER {cn}---')
    for i in range(1, max_n):
        if get_class_number(i, old=True) == cn:
            ls_out.append(i)
    return ls_out


def test_factors_n():
    assert factors_of_n(1) == [(1, 1)]
    assert factors_of_n(2) == [(1, 2)]
    assert factors_of_n(4) == [(1, 4), (2, 2)]


if __name__ == '__main__':
    test_factors_n()

    # print(get_negative_class_type(max_n=170, cn=1))
    # todo figure out which one is more right
    assert get_negative_class_type(max_n=170, cn=1) == [3, 4, 7, 8, 11, 19, 43, 67, 163]
    # assert get_negative_class_type(max_n=170, cn=1) == [3, 7, 11, 19, 43, 67, 163]

    print(get_negative_class_type(max_n=170, cn=2))

    print('---DEBUG 47---')
    # this should equal to 5, not 3. Not sure if this is possible to compute.
    print(get_class_number(47, debug=True))
    # D = 47
    #  a   b   c   works
    #  1   1   12    Y
    #  1  -1   12    X
    #  2   1    6    Y
    #  2  -1    6    Y
    #  3   1    4    Y
    #  3  -1    4    Y

    # note that the solution (1, -1, 12) ~ (1, 1, 12) hence it should not be part of the class number
    # using T = np.array([[1, 1], [0, 1]])
    # we have T' * (1, -1, 12) * T = (1, 1, 12)
    # (1 0) * (  1   -1/2) * (1 1) = ( 1  1/2)
    # (1 1)   (-1/2   12 )   (0 1)   (1/2  1 )

# import numpy as np
# A = np.array([[1, 1/2], [1/2, 41]])
# S = np.array([[0, -1], [1, 0]])
# T = np.array([[1, 1], [0, 1]])
# A2 = np.array([[1, -1/2], [-1/2, 41]])
# T.transpose() @ A2 @ T