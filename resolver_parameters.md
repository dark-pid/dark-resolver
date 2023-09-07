# Resolver Parameters

This page details the dARK Resolver parameters.

## Resolver Paramenter

| PARAMETER                           | DESCRIPTION | TYPE | EXAMPLE | 
| ---                                 | ---         | ---  | ---     |
| [MANAGED_NAM_DICT](#managed-nam-list)               | managed nam list | DICT | '{ "8033": true , "8003": true }' |


### MANAGED NAM LIST

The NAM (authorities) that the resolver is responsible.

The `MANAGED_NAM_DICT` is required and must be valid to **start a resolver**. If the variable is not set the resolver will not start.

The `MANAGED_NAM_DICT` is a list, and must have the folowing syntax:

> - Considering one NAM
>``` bash
> export MANAGED_NAM_DICT='{"`<nam_value_1>`": true}'
>```

or

> - Considering multiples NAM
>``` bash
> export MANAGED_NAM_DICT='{"`<nam_value_1>`": true, "`<nam_value_2>`": true}'
>```

The validation will be performed by the following code:

>```python
> import json
> env_list = json.loads(os.environ['MANAGED_NAM_DICT'])
>```

