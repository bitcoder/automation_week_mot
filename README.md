# Automated tests for Automation Week UI challenges from MoT

This repo provides test automation code for Automation Week UI challenges of Ministry of Testing 2020.
Different implementations and techniques are provided, showcasing how this could be achieved. Each has pros/cons that have to be considered.

Note: it's a learning exercise, so it may not be perfect. Nevertheless, I think it can be useful to get started.

## Overview of UI challenges

Next follows a description of the UI challenges for the sample website application [Restful Brooker Platform](https://automationintesting.online/) kindly provided by [Mark Winteringham](https://twitter.com/2bittester) / [Richard Bradshaw](https://twitter.com/FriendlyTester).

### 1. Beginner

_Create an automated test that completes the contact us form on the homepage, submits it, and asserts that the form was completed successfully._

### 2. Intermediate

_Create an automated test that reads a message on the admin side of the site._

_You’ll need to trigger a message in the first place, login as admin, open that specific message and validate its contents._

### 3. Advanced

_Create an automated test where a user successfully books a room from the homepage._

_You’ll have to click ‘Book this Room’, drag over dates you wish to book, complete the required information and submit the booking._

## Approach for implementing automated tests

In this repo, you'll find two different Python implementations for automated tests/checks based on the Page Objects Model (POM):

- one using Pytest
- another using Model-Based Testing, using AltWalker and GraphWalker

### Pre-requisites

- Python3
- Firefox (or other browser)
- GraphWalker v4.2.0 (v4.3.0 has some issues with AltWalker v0.2.7); see instructions [here](https://graphwalker.github.io/)

Install the python dependencies:

```pip install -r requirements.txt```

### Running automated tests

#### Standard tests using Pytest

In order to run the standard Pytest tests, just execute:
```pytest -s contact_form_pom_tests.py.py```

or, if you prefer using the helper bash script:

```./run_pytest.sh```

#### Model-based tests using AltWalker and GraphWalker

In order to run the standard Pytest tests, just execute:
```bash

altwalker check -m models/contact_form.json "random(vertex_coverage(100) and edge_coverage(100))"
altwalker verify -m models/contact_form.json tests
altwalker online tests -m models/contact_form.json "random(vertex_coverage(100) and edge_coverage(100))"

```


or, if you prefer using the helper bash scripts:

```./run_altwalker_contact.sh```

```./run_altwalker_contact_detailed.sh```

```./run_altwalker_contact_with_message.sh```

## Final thoughts

On the app:

- app has some testability issues that inhibit usage of stable locators
- app has several bugs (intended or not :)) 

On the automated tests implementation:

- we can automate checks for the current behavior but we can't gurantee if that is the original intended one (e.g. phone format, fields size, flow behavior)
- randomization of data: control it, for reproduction purposes, using a seed
- Model-Based Testing:
  - beware with state management
  - not used to replace traditional tests (happy-path and negative tests)
  - can be harder to debug
  - models can connect with one another through shared states, which is useful

app has some testability issues that inhibit usage of stable locators

## References

- [AltWalker documentation](https://altom.gitlab.io/altwalker/altwalker/index.html)
- [Examples provided by AltWalker](https://altom.gitlab.io/altwalker/altwalker/examples.html)
- Python packages
  - [pypom](https://pypom.readthedocs.io/en/latest/)
  - [webdriver](https://pypi.org/project/selenium/)
  - [faker](https://faker.readthedocs.io/en/master/)

## Contact

You can find me on [Twitter](https://twitter.com/darktelecom).

## LICENSE

[MIT](LICENSE).