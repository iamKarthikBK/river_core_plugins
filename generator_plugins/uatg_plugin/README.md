## changes to be made in river_core.ini to enable uatg generator
```
[uatg]
jobs = 4
count = 1
seed = random
isa_config_yaml = /path/to//c64/rv64i_isa.yaml
core_config_yaml = /path/to//c64/core64.yaml
custom_config_yaml = /path/to/c64/rv64i_custom.yaml
csr_grouping_yaml = /path/to//c64/csr_grouping64.yaml
modules_dir = /path/to/modulesdir
work_dir = /user's/preferred/workdir
linker_dir = /the/directory/containing/link.ld/and/model_test.h/files
modules = all
generate_covergroups = true
alias_file = /path/to/aliasing/file 
check_logs = True
```

In addition to this change, update the generator parameter to select uatg as shown.
```
generator = uatg
```
You can find documentaion about the changes to be made in the river_core.ini [here](uatg.readthedocs.io)
