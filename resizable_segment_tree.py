#
# Copyright (C) 2025 George Zhang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Non-recursive segment tree supporting resizing

The general idea is that values are at odd indices, with parents located
between the children::
    G               -      10000
    8       -              x1000
    4   -   C   -          xx100
    2 - 6 - A - E - I -    xxx10
    1 3 5 7 9 B D F H J    xxxx1

See this blog post for a simpler non-recursive but non-resizable segment tree:
https://codeforces.com/blog/entry/18051
"""

class ResizableSegmentTree:
    def __init__(self, func, values):
        self.func = func
        self.tree = tree = (len(values)<<1) * [None]
        for i, value in enumerate(values):
            j = (i<<1) | 1
            tree[j] = value
            k = 1
            while j & (k<<1):  # is j a right child?
                p = j & ~k | (k<<1)  # calculate parent index
                tree[p] = func(tree[j & ~(k<<1)], tree[j])  # update parent
                j = p
                k <<= 1

    def __setitem__(self, i, value):
        func = self.func
        tree = self.tree
        j = (i<<1) | 1
        tree[j] = value
        k = 1
        while j | (k<<1) < len(tree):  # is the right child inside the tree?
            p = j & ~k | (k<<1)
            tree[p] = func(tree[j & ~(k<<1)], tree[j | (k<<1)])
            j = p
            k <<= 1

    def __getitem__(self, i):
        return self.tree[(i<<1) | 1]

    def __len__(self):
        return len(self.tree) >> 1

    def append(self, value):
        tree = self.tree
        i = len(tree) >> 1
        tree += (None, None)
        self[i] = value

    def query(self, i, j):
        func = self.func
        tree = self.tree
        assert 0 <= i < len(self)
        assert 0 < j <= len(self)
        assert i < j
        i = (i<<1) | 1
        j = (j<<1) | 1
        left = right = None
        k = 1
        while i < j:
            if i & (k<<1):
                if left is None:
                    left = tree[i]
                else:
                    left = func(left, tree[i])
                i += k<<1
            if j & (k<<1):
                j -= k<<1
                if right is None:
                    right = tree[j]
                else:
                    right = func(tree[j], right)
            i = i & ~k | (k<<1)
            j = j & ~k | (k<<1)
            k <<= 1
        assert left is not None or right is not None
        if left is None:
            return right
        if right is None:
            return left
        return func(left, right)

    @staticmethod
    def _format(tree):
        out = [[]]
        for i in range(1, len(tree)):
            out[(i&-i).bit_length() - 1].append(tree[i])
            if out[-1]:
                out.append([])
        out.pop()
        return out

    def _print(self, width=4):
        out = self._format(self.tree)
        for i, parts in enumerate(reversed(out)):
            ww = 2**(len(out)-i-1)
            for part in parts:
                print(end=f'{part!r:>{width}}')
                if ww > 1:
                    print(end=f'{"":>{(ww//2-1)*width}}')
                    print(end=f'{"-":>{width}}')
                    print(end=f'{"":>{(ww//2-1)*width}}')
            print()

if __name__ == "__main__":
    # test initializing tree
    t = ResizableSegmentTree(lambda a, b: a + b, [1, 2, 3, 4, 5, 6])
    print("== initial tree")
    print(t, t.tree)
    t._print()

    # test queries are correct
    def test_tree_query(tree):
        for i in range(len(tree)):
            for j in range(i+1, len(tree)+1):
                assert tree.query(i, j) == sum(tree[x] for x in range(i, j))
    test_tree_query(t)

    # test resizing
    t.append(7)
    t.append(8)
    t.append(9)
    t.append(10)
    print()
    print("== after resizing")
    t._print()
    test_tree_query(t)

    # test updates
    t[2] = 15
    t[6] = 16
    t[8] = 17
    print()
    print("== after updates")
    t._print()
    test_tree_query(t)
