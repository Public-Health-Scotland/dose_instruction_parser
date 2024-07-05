# GitHub workflows for `dose_instruction_parser`

> [!TIP]
> See the [GitHub actions](https://docs.github.com/en/actions) documentation for comprehensive information

* GitHub workfklows are a series of steps (known as "actions") which you can set to run automatically when certain events occur, such as when code is pushed or merged, or when pull requests are opened
* This folder contains the GitHub workflows for the [`dose_instruction_parser`](https://github.com/Public-Health-Scotland/dose_instruction_parser/) repository
* You can view the workflows and their outputs by clicking on the [`Actions`](https://github.com/Public-Health-Scotland/dose_instruction_parser/actions) tab on GitHub


## Workflows

The workflows folder contains all the GitHub workflows.

| File | Trigger | Actions |
| -- | -- | -- |
| `pylint.yml` | push | Runs [`pylint`](https://pypi.org/project/pylint/) to analyse the code, check for errors and enforce a coding standard. You need to manually check on the [output](https://github.com/Public-Health-Scotland/dose_instruction_parser/actions/workflows/pylint.yml) of this to evaluate the state of the code. |
| `docs.yml` | push to `main` | Compiles documentation and publishes to [GitHub pages](https://public-health-scotland.github.io/dose_instruction_parser/). See `doc/sphinx/README.md` for more information.|
| `tests.yml` | push | Runs tests for `dose_instruction_parser`. If tests fail, adds a message to the pull request chat with information (if a pull request is available). If tests succeed, calculates code coverage, pushes report to `coverage/` and adds message to pull request chat (if available). Updates coverage badge in `README.md`.|
