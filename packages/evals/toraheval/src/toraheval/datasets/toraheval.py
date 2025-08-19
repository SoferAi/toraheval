from deepeval.dataset import EvaluationDataset, Golden

dataset = EvaluationDataset(
    goldens=[
        Golden(input="What is the first word of the Torah?", expected_output="בראשית")
    ]
)
