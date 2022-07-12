# quoll
Image quality assessment for electron tomography

# Installation

1. Clone the repository. In a terminal:

```
git clone https://github.com/rosalindfranklininstitute/quoll.git
```

2. Navigate to the Quoll directory and create a new conda environment for Quoll. This installs all the pre-requisite libraries to use Quoll. Don't forget to activate this environment

```
conda env create -n quoll -f quoll_env.yaml
conda activate quoll
```

3. Pip install the quoll package

```
pip install -e .
```


# Examples

The [examples](https://github.com/rosalindfranklininstitute/quoll/tree/main/examples) folder contains Jupyter notebooks for example usage.

Alternatively the [tests](https://github.com/rosalindfranklininstitute/quoll/tree/main/tests) also go through some ways of using quoll.