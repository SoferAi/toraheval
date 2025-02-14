# TorahEval
Open source evaluation framework for Torah-related questions and knowledge assessment.

## Description
TorahEval is built upon the foundation provided by the AI Safety Institute's inspection framework (https://inspect.ai-safety-institute.org.uk). It provides a structured approach to evaluating AI models' understanding and handling of Torah-related content.

## Installation
Use uv package manager to install dependencies:
```sh
uv sync
```

## Configuration
Before running, set up your API key:
```sh
export GROQ_API_KEY=your_api_key_here
```

## Usage
Run the evaluation using:
```sh
uv run inspect eval --model groq/llama3-70b-8192
```

## Contributing
We welcome contributions! Please fork the repository and create a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.


