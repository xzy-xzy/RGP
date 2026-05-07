# RGP
Dataset and code for the paper [Investigating More Explainable and Partition-Free Compositionality Estimation for LLMs: A Rule-Generation Perspective](https://arxiv.org/abs/2604.27340).

## Dataset Generation
See `generate_dataset.sh` and `generate_samples.py`. We have saved the generated dataset in the `dataset` folder.

## Rule-Generation Perspective
To obtain compositionality estimation from the rule-generation perspective, use the following commands:
```
python api_serial.py --model [model] --type [type] --api_key [api_key]
python program_eval_5.py --model [model] --type [type]
```
Here, `type` can be set to `[h, v, b, r, hr]`, corresponding to Horizontal, Vertical, Block, Random, and Setting Combination (H+R), respectively. You can conduct experiments with Random Index by adding `--index_shuffle`. You can specify `base_url` in `config.py` if the default URL does not meet your expectations.

You can choose the Python file for calling the API based on your required features:

`serial`: Serial calls

`async`: Asynchronous calls

`stream`: Streaming output

`batch`: Batch calls

`claude`: For Claude models

## Compositional Generalization Tests
To obtain the results of compositional generalization tests, use the following command:
```
python cg_api_async.py --model [model] --type [type] --api_key [api_key]
python program_eval_cg.py --model [model] --type [type]
```
Settings can be modified in a similar way to the rule-generation perspective.

## Citation
```
@misc{xu2026investigatingexplainablepartitionfreecompositionality,
      title={Investigating More Explainable and Partition-Free Compositionality Estimation for LLMs: A Rule-Generation Perspective}, 
      author={Ziyao Xu and Cong Wang and Houfeng Wang},
      year={2026},
      eprint={2604.27340},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2604.27340}, 
}
```
