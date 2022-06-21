# See LICENSE for details

import os
import sys
import pluggy
import shutil
from river_core.log import logger
import river_core.utils as utils
from river_core.constants import *
import random
import re
import datetime
import pytest
from envyaml import EnvYAML


def gen_cmd_list(gen_config, seed, count, output_dir, module_dir):

    logger.debug('Now generating commands for gen plugin')

    gen_list = utils.load_yaml(gen_config)
    setup_dir = ''
    run_command = []
    dirname = output_dir + '/aapg'
    utils.sys_command('aapg setup --setup_dir {0}'.format(dirname))
    setup_dir = dirname

    for key, value in gen_list.items():
        if key == 'configs':
            for configs in gen_list[key]:
                template_name = os.path.basename(configs)
                config_file = os.path.abspath(configs)
                for i in range(int(count)):
                    if seed == 'random':
                        gen_seed = random.randint(0, 10000)
                    else:
                        gen_seed = int(seed)

                    now = datetime.datetime.now()
                    gen_prefix = '{0:06}_{1}'.format(
                        gen_seed, now.strftime('%d%m%Y%H%M%S%f'))
                    test_prefix = 'aapg_{0}_{1}_{2:05}'.format(
                        template_name.replace('.yaml', ''), gen_prefix, i)
                    testdir = '{0}/asm/{1}'.format(dirname, test_prefix)
                    run_command.append('aapg gen \
                                        --config_file {0} \
                                        --setup_dir {1} \
                                        --output_dir {2} \
                                        --asm_name {3} \
                                        --seed {4}\
                                        '.format(config_file, setup_dir,
                                                 testdir, test_prefix,
                                                 gen_seed))

    return run_command


def idfnc(val):
    template_match = re.search('--config_file (.*).yaml', '{0}'.format(val))
    logger.debug('{0}'.format(val))
    return 'Generating {0}'.format(template_match.group(1))


def pytest_generate_tests(metafunc):
    if 'test_input' in metafunc.fixturenames:
        test_list = gen_cmd_list(metafunc.config.getoption("configlist"),
                                 metafunc.config.getoption("seed"),
                                 metafunc.config.getoption("count"),
                                 metafunc.config.getoption("output_dir"),
                                 metafunc.config.getoption("module_dir"))
        metafunc.parametrize('test_input', test_list, ids=idfnc, indirect=True)


@pytest.fixture
def test_input(request, autouse=True):
    # compile tests
    program = request.param
    template_match = re.search('--config_file (.*).yaml', program)
    #sys_command(program)
    #return 0
    if os.path.isfile('{0}.yaml'.format(template_match.group(1))):
        (ret, out, err) = utils.sys_command(program)
        return ret
    else:
        logger.error('File not found {0}'.format(template_match.group(1)))
        return 1


def test_eval(test_input):
    assert test_input == 0
