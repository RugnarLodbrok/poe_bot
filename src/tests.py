from mouse import ReIndexList


def test_reindex(n):
    for i in range(1, n):
        for j in range(1, n):
            print(i, j)
            assert len(list(ReIndexList(list(range(i)), j))) == j, "error for: {} {}".format(i, j)


def main():
    test_reindex(100)


if __name__ == '__main__':
    main()