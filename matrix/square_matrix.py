from matrix.basic_matrix import Matrix, MatrixError
import unittest
import copy


class SquareMatrix(Matrix):
    def __init__(self, ls_entries=None, matrix=None):
        """
        Construct a Square Matrix class
        Args:
            ls_entries: given a list of lists construct a matrix
            matrix: given a Matrix type
        """
        if ls_entries is not None and isinstance(ls_entries, list):
            super().__init__(ls_entries)
        elif matrix is not None and isinstance(matrix, Matrix):
            super().__init__(ls_entries=matrix.ls_entries)
        else:
            raise MatrixError('Square matrix not instantiated correctly.')

        if not self.is_square():
            raise MatrixError('Not a square matrix.')
        self.size = self.len_row

    def determinant(self):
        """Computes the determinate of the square matrix"""
        # base case for 2x2 matrix
        if self.size == 2:
            # a*d - b*c
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]

        determinant = 0
        for col in range(self.size):
            determinant += ((-1) ** col) * self[0][col] * self.minor_matrix(0, col).determinant()

        return determinant

    def inverse(self):
        determinant = self.determinant()
        if determinant == 0:
            raise MatrixError("Matrix is singular")

        # special case for 2x2 matrix:
        if self.size == 2:
            return [[self[1][1] / determinant, -1 * self[0][1] / determinant],
                    [-1 * self[1][0] / determinant, self[0][0] / determinant]]

        # find matrix of minors
        minors = self.zero_matrix(row_dim=self.size, col_dim=self.size)

        for row in range(self.size):
            for col in range(self.size):
                minor = self.minor_matrix(row, col)
                minors[row][col] = ((-1) ** (row + col)) * minor.determinant()

        t_minors = minors.transpose()

        for row in range(t_minors.len_row):
            for col in range(t_minors.len_row):
                t_minors[row][col] /= determinant

        return t_minors

    def square_root(self):
        raise NotImplementedError

    def LU_decomposition(self):
        """
        Returns: the LU decomposition of the self.ls_entries matrix
        self.ls_entries matrix must be square
            L, U where [A] = [L][U]
            L: <Matrix> m x m lower triangular matrix
            U: <Matrix> m x m upper triangular matrix
        """

        # L and U are both square matrices
        L = self.identity(self.len_row).ls_entries
        U = [[0] * self.len_row for x in range(self.len_row)]
        A = SquareMatrix(copy.deepcopy(self.ls_entries))

        # Need to pivot first for stability
        for i in range(self.len_row):
            minor_col_i = list(map(abs, A[i:self.len_row, i]))
            max_row_index = minor_col_i.index(max(minor_col_i)) + i
            A[i], A[max_row_index] = A[max_row_index], A[i]

        for i in range(self.len_row):
            for j in range(i, self.len_row):  # update matrix after pivoting
                sum_upper = sum([L[i][k] * U[k][j] for k in range(i)])
                sum_lower = sum([L[j][k] * U[k][i] for k in range(i)])
                U[i][j] = A[i][j] - sum_upper
                L[j][i] = (A[j][i] - sum_lower) / U[i][i] if U[i][i] != 0 else 0

        return SquareMatrix(L), SquareMatrix(U)

    def get_toeplitz_matrix_berkowitz(self, a_0_0, row_vector, col_vector, principal):
        """

        :return: (n + 1) x n Toeplitz lower triangular matrix
        """
        size = len(principal.ls_entries) + 2  # size of the matrix that the row, vector, and principal were extracted
        L = Matrix(self.identity(size).ls_entries + [[0] * size])
        products = [-a_0_0, -row_vector.__mul__(col_vector.transpose())[0][0]]

        if size > 3:
            principal_pows = [principal] + [principal.__pow__(x) for x in range(2, size - 1)]
            products += [-row_vector.__mul__(x).__mul__(col_vector.transpose())[0][0] for x in principal_pows]

        for i in range(1, size):  # rows
            for j in range(i):
                if i - j > 0:
                    L[i][j] = products[(i - j) - 1]

        return L

    def char_eqn_berkowitz(self):
        # https://en.wikipedia.org/wiki/Samuelson%E2%80%93Berkowitz_algorithm
        A = SquareMatrix(copy.deepcopy(self.ls_entries))
        C_ls = []
        for i in range(self.size):  # todo fix this condition for the subsequent principal matrices 
            row_vector = Matrix([A[0, 1:]])
            col_vector = Matrix([A[1:, 0]])
            principal = Matrix([[A[j][x] for x in range(len(A[j])) if x != 0] for j in range(len(A.ls_entries)) if
                                j != 0])
            a_elem = A[0][0]
            A = principal
            C = self.get_toeplitz_matrix_berkowitz(a_elem, row_vector, col_vector, principal)
            C_ls.append(C)

        print(*[x.ls_entries for x in C_ls], sep='\n')

        result = C_ls[0]
        C_ls.pop(0)
        while C_ls:
            result.__mul__(C_ls[0])
            C_ls.pop(0)

        return result

    def eigenvalues(self):
        """
        Use some numerical root solving to get the roots of the characteristic equation

        :return:
        """

        # get the characteristic equation

        # power iteration?
        # inverse iteration?
        # figure out how to solve characteristic equation without using numpy

        pass

    def eigenvectors(self):
        raise NotImplementedError


class TestSquareMatrix(unittest.TestCase):
    def test_det(self):
        A = SquareMatrix(ls_entries=[[1, 2, 1], [1, 3, 2], [1, 5, 2]])

        self.assertEqual(A.determinant(), -2)

    def test_inverse(self):
        A = SquareMatrix(ls_entries=[[1, 2, 1], [1, 3, 2], [1, 5, 2]])

        A_I = 0.5 * SquareMatrix(ls_entries=[[4, -1, -1], [0, -1, 1], [-2, 3, -1]])
        self.assertEqual(A.inverse(), A_I)

    def test_lu_decomposition(self):
        A = SquareMatrix(ls_entries=[[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        L, U = A.LU_decomposition()
        multiply = L.__mul__(U)
        self.assertEqual(set(map(tuple, A.ls_entries)), set(map(tuple, multiply)))
