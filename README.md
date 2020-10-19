# Automated tests for Automation Week UI challenges from MoT

This repo provides test automation code for Automation Week UI challenges of Ministry of Testing 2020.
Different implementations and techniques are provided, showcasing how this could be achieved. Each has pros/cons that have to be considered.

Note: it's a learning exercise, so it may not be perfect. Nevertheless, I think it can be useful to get started.

## Overview of UI challenges

Next follows a description of the UI challenges for the sample website application [Restful Brooker Platform](https://automationintesting.online/) kindly provided by [Mark Winteringham](https://twitter.com/2bittester) / [Richard Bradshaw](https://twitter.com/FriendlyTester).

The tests are pretty simple and the purpose is to exercise test automation, refining the approach, be aware of some challenges, etc.

![](images/target_sut.jpg)

### Challenge 1: Beginner

_Create an automated test that completes the contact us form on the homepage, submits it, and asserts that the form was completed successfully._

### Challenge 3: Intermediate

_Create an automated test that reads a message on the admin side of the site._

_You’ll need to trigger a message in the first place, login as admin, open that specific message and validate its contents._

### Challenge 3: Advanced

_Create an automated test where a user successfully books a room from the homepage._

_You’ll have to click ‘Book this Room’, drag over dates you wish to book, complete the required information and submit the booking._

## Approach for implementing automated tests

In this repo, you'll find two different Python implementations for automated tests/checks:

- one using pytest
- another using Model-Based Testing (MBT), using AltWalker which in turn uses GraphWalker

Both make use of the Page Objects Model (POM) facilated by the pypom library. As pages can have different sections/regions, we can abstract those precisely as classes inherited from the Region class. This will make code cleaner and more readable.

```python
class FrontPage(Page):
    """Interact with frontpage."""

    _admin_panel_locator = (By.LINK_TEXT, "Admin panel")

    class ContactForm(Region):

        _contact_form_name_locator = (By.ID, "name")
...
```

In both implementations, you'll see references to a faking data library. I've combined controlled randomization of data to provide greater coverage; this is especially valuable in the MBT implementation as the model can be exercised automatically "indefinitely" (to a certain point).

### Standard tests using pytest

This implementation is what I would call the traditional/common way of implementing automated tests.
Tests are implemented in the file [contact_form_pom_tests.py](contact_form_pom_tests.py), as seen in this example for the sucessful contact test.

```python
    def test_contact_form_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()
        page.contact_form.fill_contact_data(name="sergio", email="sergio.freire@example.com", phone="+1234567890",
                                            subject="doubt", description="Can I book rooms up to 2 months ahead of time?")
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch sergio!\nWe'll get back to you about\ndoubt\nas soon as possible.")
```

In this case data was hard-coded. However, by using [faker](https://faker.readthedocs.io/en/master/) library we can create a [custom test data provider](tests/my_contact_provider.py) for the contact and our test method can be rewriten as:

```python
    def test_contact_form_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()
        name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()
        page.contact_form.fill_contact_data(name=name, email=email, phone=phone,
                                            subject=subject, description=description)
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch sergio!\nWe'll get back to you about\ndoubt\nas soon as 
```

### Model-based tests using AltWalker and GraphWalker

With MBT, usually we have the model (either made using a visual model editor or from the IDE) and the underlying code.
In our case, models are stored in JSON format under the [models](models) directory.
The test code associated to vertices and egdges is implemented in the file [test.py](tests/test.py).

Using [Model Editor](https://altom.gitlab.io/altwalker/model-editor/) (or [GraphWalker Studio](https://graphwalker.github.io/)), we can model our application using a directed graph. In simple words, each vertex represents a state and each edge is a transition/action made in the application. Tests are made on the vertices/states.
Modeling is a challenge in itself and we can model the application and how we interact with it in different ways. Models are not exaustive; they're a focused perspective on a certain behavior that we want to understand. MBT provides greater coverage and also a great way to visualize and discuss the application behavior/usage.

For the first challenge (i.e. contact form submission), we start from an initial state, from where we just have one possible action/edge: load the frontpage.
Then we can consider another state, where the frontpage is loaded and the contact form is available.
Two additional states are possible: one for a successful contact and another for an unsuccessful contact submission. We can go to these states by either submiting valid or invalid contact data.
One curious thing comes out from the model: after a successful contact, we can only make a new contact if we load/refresh the frontpage again. Was this an expected behavior? Well, we would have to discuss with the team.

![](images/mbt_contact_form.jpg)

With GraphWalker Studio we can run the model in offline and see the paths (sequence of vertices and edges) performed.

The code for each vertex and edge is quite simple as seen ahead.

Example of __e_submit_valid_contact_data__ code, showcasing usage of faker library:
```python

    def e_submit_valid_contact_data(self, data):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()

        data['global.last_contact_name'] = name
        data['global.last_contact_email'] = email
        data['global.last_contact_phone'] = phone
        data['global.last_contact_subject'] = subject
        data['global.last_contact_description'] = description

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)
```

Example of __v_contact_successful__ code:
```python
    def v_contact_successful(self, data):
        page = FrontPage(self.driver, BASE_URL)        
        name = data['last_contact_name']
        subject = data['last_contact_subject']
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch {name}!\nWe'll get back to you about\n{subject}\nas soon as possible.")
```


![](images/mbt_contact_form_offline.gif)

One can make this model a bit more detailed and complex, by making explicit edges/transitions for the process of submiting one field as invalid. This makes the graph harder to read though and it will only be relevant if we want to distinguish those cases.

![](images/mbt_contact_form_detailed.jpg)

In order to validate if the contact/message appears correctly in the admin page (3rd challenge), we start from a vertex/state related to a sucessful contact. This vertex has a shared state with the first model shared earlier, which allows AltWalker/GraphWalker to jump from one to the other.

We can then go to the admin panel, authenticate if needed, go to the inbox/messages section, open and check the details of the last contact message.
We can see several edges corresponding to actions that can be done, allowing to transverse the graph and thus go to different application states.

Some edges (e.g. e_admin_correct_login) have "actions" defined in the model, to set an internal variable that can be useful later on.

Example:
```javacript
logged_in=true;
```

Some edges (e.g. e_click_admin_panel, from v_contact_successful to v_admin_login) have "guards", so they're only performed if those guard conditions are true.

Example:
```javacript
logged_in!=true
```

In this exercise, we take advantage of using model variables (e.g. last_contact_name, last_contact_subject) to temporarily store information about the last contact. The actual contact data used is implemented in code side and is populated on the model variables used for this purpose.

![](images/mbt_message_backoffice.jpg)


### Pre-requisites

- Python3
- Firefox (or other browser)
- GraphWalker v4.2.0 (v4.3.0 has some issues with AltWalker v0.2.7); see instructions [here](https://graphwalker.github.io/)

Install the python dependencies:

```pip install -r requirements.txt```

### Running automated tests

#### Standard tests using pytest

In order to run the standard pytest tests, just execute:
```pytest -s contact_form_pom_tests.py.py```

or, if you prefer using the helper bash script:

```./run_pytest.sh```

#### Model-based tests using AltWalker and GraphWalker

In order to run AltWalker tests (e.g. for the contact form), just execute the following commands.

```bash

altwalker check -m models/contact_form.json "random(vertex_coverage(100) and edge_coverage(100))"
altwalker verify -m models/contact_form.json tests
altwalker online tests -m models/contact_form.json "random(vertex_coverage(100) and edge_coverage(100))"
```

If you prefer, you may use the helper bash scripts:

```./run_altwalker_contact.sh```

```./run_altwalker_contact_detailed.sh```

```./run_altwalker_contact_with_message.sh```

If you wish to run the tests against a specific URL instead of the default (https://aw1.automationintesting.online), you just need to define the BASE_URL environment variable.

```bash
BASE_URL="https://aw3.automationintesting.online" ./run_pytest.sh
```

## Final thoughts

On the app:

- app has some testability issues that inhibit usage of stable locators
- app has several bugs, intended or not :)

On the automated tests implementation:

- we can automate checks for the current behavior but we can't gurantee if that is the original intended one (e.g. phone format, fields size, flow behavior)
- randomization of data: control it, for reproduction purposes, using a seed
- Model-Based Testing:
  - can easily expose usage scenarios that go beyond happy paths
  - models can connect with one another through shared states, which is useful
  - can be combined with randomization of data to provide greater coverage
  - beware of managing data outside of the model (i.e. in the code) and in the model using variables
  - not used to replace traditional tests (happy path and negative tests)
  - can be harder to debug


## Room for improvement

These are some points that can be further improved:

- locators
- use structured test data in the code
- implement room booking (3rd challenge) using MBT

## References

- [AltWalker documentation](https://altom.gitlab.io/altwalker/altwalker/index.html)
- [Examples provided by AltWalker](https://altom.gitlab.io/altwalker/altwalker/examples.html)
- [GraphWalker and GraphWalker Studio](https://graphwalker.github.io/)
- Python packages
  - [pypom](https://pypom.readthedocs.io/en/latest/)
  - [webdriver](https://pypi.org/project/selenium/)
  - [faker](https://faker.readthedocs.io/en/master/)

## Contact

You can find me on [Twitter](https://twitter.com/darktelecom).

## LICENSE

[MIT](LICENSE).