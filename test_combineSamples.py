from unittest import TestCase
from unittest import main

import shelve
import glob
import os

from combineSamples import combineSamples


class Test_combineSamples(TestCase):

    def setUp(self):
        # initialize expected results
        self.pattern = "boiler_sample_*.csv"
        self.pathnames = glob.glob("./" + self.pattern, recursive=False)
        self.files = [os.path.basename(f) for f in self.pathnames if os.path.isfile(f)]
        
        with shelve.open('expected_results') as expected_results:
            self.exp = expected_results['combineSamples']
            self.exp_default = expected_results['combineSamples.default']

            # call bbanalyze with default file
            self.act = combineSamples(self.pattern)


        self.shape = self.exp['samples'].shape
        self.cwd = os.getcwd()



    def test_combine_samples_default_path(self):
        # check for different numbers of control samples

        for control_count in range(5, 20, 5):
            # test for control sample size in [5, 10, 15]
            
            actual = combineSamples(self.pattern, control_samples=control_count)

            # check basic cells
            self.assertEqual(self.pattern, actual['pattern'])
            self.assertEqual(".", actual['path'])
            self.assertEqual(control_count, actual['control_samples'])
            self.assertEqual(self.files, actual['filenames'])
            self.assertEqual(len(self.files), actual['files'])

            # dimensions of the 'samples' data frame should match, regardless of the control_count
            self.assertEqual(self.exp['samples'].shape, actual['samples'].shape)

            # there should be control_count rows in the 'control' dataframe (columns same as 'samples')
            self.assertEqual((control_count, self.shape[1]), actual['control'].shape)

            # samples not included in 'control' dataframe should be in 'test' dataframe
            self.assertEqual((self.shape[0] - control_count, self.shape[1]), actual['test'].shape)


    def test_combine_samples_explicit_path(self):
        # check for different numbers of control samples

        for control_count in range(5, 20, 5):
            # test for control sample size in [5, 10, 15]

            actual = combineSamples(self.pattern, self.cwd, control_samples=control_count)

            # check basic cells
            self.assertEqual(self.pattern, actual['pattern'])
            self.assertEqual(self.cwd, actual['path'])
            self.assertEqual(control_count, actual['control_samples'])
            self.assertEqual(self.files, actual['filenames'])
            self.assertEqual(len(self.files), actual['files'])

            # dimensions of the 'samples' data frame should match, regardless of the control_count
            self.assertEqual(self.exp['samples'].shape, actual['samples'].shape)

            # there should be control_count rows in the 'control' dataframe (columns same as 'samples')
            self.assertEqual((control_count, self.shape[1]), actual['control'].shape)

            # samples not included in 'control' dataframe should be in 'test' dataframe
            self.assertEqual((self.shape[0] - control_count, self.shape[1]), actual['test'].shape)


    def test_default_control_count(self):
        # check using the default value for control_count

        actual = combineSamples(self.pattern)

        # check basic cells
        self.assertEqual(self.pattern, actual['pattern'])
        self.assertEqual(".", actual['path'])
        self.assertEqual(self.exp_default['control_samples'], actual['control_samples'])
        self.assertEqual(self.files, actual['filenames'])
        self.assertEqual(len(self.files), actual['files'])

        # Compare actual sample dataframes
        # these tests superseded due to floating point inaccuracy issues
        # for k in ['samples', 'control', 'test']:
        #     with self.subTest(Sample=k):
        #         self.assertTrue(self.exp_default[k].equals(actual[k]))

        # verify sample fields one at a time, limiting precision to 5 decimal places

        for k in ['samples', 'control', 'test']:
            exp = self.exp_default[k]
            nrow, ncol = exp.shape
            idx = exp.index
            colnames = exp

            for i in exp.index:
                for j in exp.keys():
                    with self.subTest(dataframe=k, sample=exp.loc[i, 'sample'], column=j):
                        self.assertAlmostEqual(exp.loc[i, j], actual[k].loc[i,j], places=5)



if __name__ == '__main__':
    rslt = main(verbosity=2, exit=False)





