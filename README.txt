# AI Group Assignment 2

This ZIP follows the three problems in the supplied assignment brief.

## Group details
- Ayush Gothwal — B24ME005
- Aman Saini — B24MT001
- Yuvraj Aswal — B24ME053
- Ayush Meena — B24MT003

## Folder contents
- `problem1/`: pure-Python Bayesian network, synthetic data, learned CPTs, comparison CSVs and error plot.
- `problem2/`: PDDL domain/problem files, generated base-scenario plans, validation and extended-scenario feasibility note.
- `problem3/`: Prolog source and proof output.
- `screenshots/`: output/visualization evidence.

## Run
Python 3 with `matplotlib` and `numpy` installed:
`python problem1/smart_home_bn.py`

The Bayesian network code uses exact enumeration and ancestral sampling, so it does not require pgmpy.
For the Prolog proof, open `problem3/royal_archive_access.pl` in SWI-Prolog and run `resolution_trace.`

## Important modeling note
The extended Mars scenario as written is unsatisfiable: Base–SiteB is the only listed route incident to SiteB, and the dust storm closes it in both directions. Rock2 at SiteB therefore cannot be reached or delivered. The package documents this rather than inventing a route that is not in the brief.
