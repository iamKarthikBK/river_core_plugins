# See LICENSE for details

#import riscv_config.checker as riscv_config
#from riscv_config.errors import ValidationError
import os
import sys
import pluggy
import shutil
import yaml
import random
import re
import datetime
import pytest
from glob import glob
from river_core.log import logger
from river_core.utils import *
from river_core.constants import *

gen_hookimpl = pluggy.HookimplMarker("generator")


class MicroTESKPlugin(object):
    """ Generator hook implementation """

    #@gen_hookimpl
    #def load_config(self, isa, platform):
    #    pwd = os.getcwd()

    #    try:
    #        isa_file, platform_file = riscv_config.check_specs(
    #                                    isa, platform, pwd, True)
    #    except ValidationError as msg:
    #        #logger.error(msg)
    #        print('error')
    #        sys.exit(1)

    # creates gendir and any setup related things
    @gen_hookimpl
    def pre_gen(self, output_dir):
        logger.debug('Microtesk Pre Gen Stage')
        if (os.path.isdir(output_dir)):
            logger.debug('exists')
            shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir)

    # gets the yaml file with list of configs; test count; parallel
    # isa is obtained from riscv_config
    @gen_hookimpl
    def gen(self, gen_config, spec_config, module_dir, output_dir):

        logger.debug('Extracting info from list')
        # Extract plugin specific info
        jobs = spec_config['jobs']
        seed = spec_config['seed']
        count = spec_config['count']
        filter = spec_config['filter']
        # TODO Might  be useful later on
        # Eventually add support for riscv_config
        isa = spec_config['isa']

        logger.debug('Microtesk Gen Stage')
        logger.debug(module_dir)
        pytest_file = module_dir + '/microtesk_plugin/gen_framework.py'
        logger.debug(pytest_file)

        # if norun:
        #     # to display test items
        #     pytest.main([pytest_file, '--collect-only', '-n={0}'.format(jobs), '-k={0}'.format(filter), '--configlist={0}'.format(gen_config), '-v', '--seed={0}'.format(seed), '--count={0}'.format(count),'--html=microtesk_gen.html', '--self-contained-html'])
        # else:
        pytest.main([
            pytest_file, '-n={0}'.format(jobs), '-k={0}'.format(filter),
            '--configlist={0}'.format(gen_config), '-v',
            '--seed={0}'.format(seed), '--count={0}'.format(count),
            '--html={0}/microtesk_gen.html'.format(output_dir),
            '--self-contained-html', '--output_dir={0}'.format(output_dir),
            '--module_dir={0}'.format(module_dir)
        ])

    # generates the regress list from the generation
    @gen_hookimpl
    def post_gen(self, output_dir, regressfile):
        logger.debug('Microtesk Post Gen Stage')
        test_dict = dict()
        test_files = []
        test_file = ''
        ld_file = ''
        test_dict['microtesk'] = {}
        """
        Overwrites the microtesk entries in the regressfile with the latest present in the gendir
        """
        logger.debug(output_dir)
        logger.debug(regressfile)
        remove_list = dict()
        if os.path.isdir(output_dir):
            output_dir_list = []
            for dir, _, _ in os.walk(output_dir):
                output_dir_list.extend(
                    glob(os.path.join(dir, 'microtesk_*/*.S')))
            logger.debug('Generated S files:{0}'.format(output_dir_list))
            testdir = ''
            for gentest in output_dir_list:
                testdir = os.path.dirname(gentest)
                testname = os.path.basename(gentest).replace('.S', '')
                ldname = os.path.basename(testdir)
                test_gen_dir = '{0}/../{1}'.format(testdir, testname)
                os.makedirs(test_gen_dir)
                logger.debug('created {0}'.format(test_gen_dir))
                sys_command('cp {0}/{1}.ld {2}'.format(testdir, ldname,
                                                       test_gen_dir))
                sys_command('mv {0}/{1}.S {2}'.format(testdir, testname,
                                                      test_gen_dir))
                remove_list[testdir] = 0

            for key in remove_list.keys():
                logger.debug('Removing directory: {0}'.format(testdir))
                shutil.rmtree(key)

        testdirs = os.listdir(output_dir)
        test_dict['microtesk']['microtesk_global_testpath'] = output_dir
        for testdir in testdirs:
            test_dict['microtesk'][testdir] = {'testname': '', 'ld': ''}
            testpath = output_dir + '/' + testdir
            tests = os.listdir(testpath)
            for file in tests:
                name = testpath + '/' + file
                if name.endswith('.S'):
                    test_dict['microtesk'][testdir]['testname'] = file
                elif name.endswith('.ld'):
                    test_dict['microtesk'][testdir]['ld'] = file

        if os.path.isfile(regressfile):
            with open(regressfile, 'r') as rgfile:
                testlist = yaml.safe_load(rgfile)
                testlist['microtesk'].update(test_dict)
            rgfile.close()

        rgfile = open(regressfile, 'w')

        print(test_dict)
        yaml.safe_dump(test_dict, rgfile, default_flow_style=False)
