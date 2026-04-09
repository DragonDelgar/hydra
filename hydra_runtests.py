import sys
import unittest
import cProfile

if __name__ == '__main__':
    suite = unittest.TestLoader().discover('../test')
    if 'perf' in sys.argv:
        cProfile.run("unittest.TextTestRunner(verbosity=1).run(suite)", sort='cumtime')
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)